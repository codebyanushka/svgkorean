"""Stage 6: promote verified pages and import them into the database.

Two separate steps, both idempotent (safe to re-run):

1. ``promote_unit(unit_number)`` copies each source's reviewed page JSON from
   ``data/extracted/verification/`` into ``data/verified/`` UNCHANGED - no
   field is rewritten, so a page whose ``verified_by`` says
   "assistant_vision_preliminary_review_pending_human_signoff" still says
   that in ``data/verified/``. Promotion is not the same thing as human
   sign-off; it only means a page has been through the review workflow at
   all (see docs/content-pipeline.md).
2. ``seed_unit(unit_number)`` reads ``data/verified/`` (never data/raw/ or
   data/extracted/) and upserts ``ContentSource``/``ContentBlock`` rows via
   the backend's SQLAlchemy models, tagging every block with its unit/lesson
   for auditability. This step must run with the *backend* virtualenv active
   (it needs SQLAlchemy + psycopg2, which the OCR venv does not have):

       cd backend && source .venv/bin/activate && cd ..
       python -m content_pipeline.seed 1

Deliberately NOT done here: creating ``Vocabulary``/``GrammarPoint``/
``Activity`` rows. Turning a raw ``ContentBlock`` into curriculum content is
an editorial decision (what is this block - a vocab entry, a grammar
explanation, an exercise?) that requires a human to look at each block, not
something this script infers. That is a separate, later curation step.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from content_pipeline import config

VERIFICATION_DIR = config.EXTRACTED_DIR / "verification"

SOURCE_TYPE_BY_KEY = {
    "textbook": "TEXTBOOK",
    "workbook": "WORKBOOK",
    "vocab_grammar": "VOCAB_GRAMMAR",
    "additional_activities": "ADDITIONAL_ACTIVITIES",
}

SOURCE_TITLE_BY_KEY = {
    "textbook": "Sejong Korean 1A - Textbook",
    "workbook": "Sejong Korean 1A - Workbook",
    "vocab_grammar": "Sejong Korean 1A - Vocabulary and Grammar",
    "additional_activities": "Sejong Korean 1A - Additional Activities",
}


def resolve_unit_pages(unit_number: int) -> dict[str, list[int]]:
    """Which physical pages, per source, belong to a given unit - built from
    content_pipeline/config.py's page-range constants."""
    unit_dict_name = f"UNIT_{unit_number}_PAGE_RANGES"
    unit_ranges = getattr(config, unit_dict_name, None)
    if unit_ranges is None:
        raise ValueError(f"No {unit_dict_name} defined in content_pipeline.config for unit {unit_number}")

    pages: dict[str, list[int]] = {}
    for source_key in ("textbook", "workbook"):
        if source_key in unit_ranges:
            pages[source_key] = config.unit_pages(unit_ranges, source_key)

    if unit_number in config.VOCAB_GRAMMAR_PART1_RANGES:
        part1 = config.unit_pages_by_number(config.VOCAB_GRAMMAR_PART1_RANGES, unit_number)
        part2 = config.unit_pages_by_number(config.VOCAB_GRAMMAR_PART2_RANGES, unit_number)
        pages["vocab_grammar"] = part1 + part2

    if unit_number in config.ADDITIONAL_ACTIVITIES_RANGES:
        pages["additional_activities"] = config.unit_pages_by_number(config.ADDITIONAL_ACTIVITIES_RANGES, unit_number)

    if unit_number == 1 and "workbook" in pages:
        pages["workbook"] = [p for p in pages["workbook"] if p not in config.WORKBOOK_EXCLUDED_NON_UNIT1_PAGES]

    return pages


def promote_page(source_key: str, page_number: int) -> Path:
    """Copy one reviewed page's JSON from data/extracted/verification/ into
    data/verified/, unchanged. Raises if the page hasn't been reviewed yet."""
    src_path = VERIFICATION_DIR / source_key / f"page_{page_number:03d}.json"
    if not src_path.exists():
        raise FileNotFoundError(f"No verification record for {source_key} page {page_number}: {src_path}")
    payload = json.loads(src_path.read_text(encoding="utf-8"))
    out_dir = config.VERIFIED_DIR / source_key
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"page_{page_number:03d}.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def promote_unit(unit_number: int) -> dict[str, list[Path]]:
    """Promote every page belonging to a unit, across all 4 sources."""
    pages_by_source = resolve_unit_pages(unit_number)
    promoted: dict[str, list[Path]] = {}
    for source_key, pages in pages_by_source.items():
        promoted[source_key] = [promote_page(source_key, p) for p in pages]
    return promoted


def _load_backend_models():
    """Lazy-import the backend's SQLAlchemy models. Requires the backend
    virtualenv (SQLAlchemy/psycopg2), not .venv-ocr - imported lazily so
    `promote_unit` alone works from either environment."""
    backend_dir = str(config.REPO_ROOT / "backend")
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    from app.db.session import SessionLocal
    from app.models.content_source import ContentBlock, ContentSource
    from app.models.curriculum import Lesson, Unit
    from app.models.enums import SourceType

    return SessionLocal, ContentSource, ContentBlock, Unit, Lesson, SourceType


def get_or_create_content_source(session, ContentSource, SourceType, source_key: str):
    source_type = SourceType[SOURCE_TYPE_BY_KEY[source_key]]
    row = session.query(ContentSource).filter_by(source_type=source_type).one_or_none()
    if row is not None:
        return row
    row = ContentSource(
        source_type=source_type,
        title=SOURCE_TITLE_BY_KEY[source_key],
        file_path=str(config.SOURCE_PDFS[source_key]),
    )
    session.add(row)
    session.flush()
    return row


def get_or_create_unit_and_lesson(session, Unit, Lesson, unit_number: int):
    number = f"{unit_number:02d}"
    unit = session.query(Unit).filter_by(number=number).one_or_none()
    if unit is None:
        unit = Unit(number=number)
        session.add(unit)
        session.flush()
    lesson = session.query(Lesson).filter_by(unit_id=unit.id).order_by(Lesson.created_at).first()
    if lesson is None:
        lesson = Lesson(unit_id=unit.id, title=f"Unit {unit_number}")
        session.add(lesson)
        session.flush()
    return unit, lesson


def import_page_blocks(session, ContentBlock, source, unit, lesson, source_key: str, page_number: int) -> dict[str, int]:
    """Upsert every block on one verified page as a ContentBlock row. Keyed
    on (source_id, page_number, block_index) for idempotency - re-running
    this updates existing rows instead of duplicating them."""
    path = config.VERIFIED_DIR / source_key / f"page_{page_number:03d}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    for block in payload["blocks"]:
        existing = (
            session.query(ContentBlock)
            .filter_by(source_id=source.id, page_number=page_number, block_index=block["block_index"])
            .one_or_none()
        )
        row = existing or ContentBlock(
            source_id=source.id,
            page_number=page_number,
            block_index=block["block_index"],
        )
        row.language = block["language"]
        row.bbox = list(block["bbox"])
        row.ocr_engine = block.get("ocr_engine")
        row.ocr_confidence = block.get("ocr_confidence")
        row.draft_text = block["draft_text"]
        row.unit_id = unit.id
        row.lesson_id = lesson.id
        row.verification_status = block["verification_status"]
        row.verified_text = block.get("verified_text")
        row.verified_by = block.get("verified_by")
        row.notes = block.get("notes")
        if existing is None:
            session.add(row)
        counts[block["verification_status"]] = counts.get(block["verification_status"], 0) + 1
    return counts


def seed_unit(unit_number: int) -> dict[str, dict[str, int]]:
    """Promote + import every source's pages for one unit. Returns a
    per-source count of blocks by verification_status for reporting."""
    promote_unit(unit_number)
    SessionLocal, ContentSource, ContentBlock, Unit, Lesson, SourceType = _load_backend_models()
    pages_by_source = resolve_unit_pages(unit_number)

    report: dict[str, dict[str, int]] = {}
    session = SessionLocal()
    try:
        unit, lesson = get_or_create_unit_and_lesson(session, Unit, Lesson, unit_number)
        for source_key, pages in pages_by_source.items():
            source = get_or_create_content_source(session, ContentSource, SourceType, source_key)
            source_counts: dict[str, int] = {}
            for page_number in pages:
                page_counts = import_page_blocks(session, ContentBlock, source, unit, lesson, source_key, page_number)
                for status, n in page_counts.items():
                    source_counts[status] = source_counts.get(status, 0) + n
            report[source_key] = source_counts
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    return report


def seed_verified_content(verified_dir: Path) -> None:
    """Back-compat alias kept for the old stub signature. Prefer seed_unit()."""
    raise NotImplementedError("Use seed_unit(unit_number) instead - see module docstring.")


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Usage: python -m content_pipeline.seed <unit_number>", file=sys.stderr)
        raise SystemExit(2)
    result = seed_unit(int(sys.argv[1]))
    for source_key, counts in result.items():
        print(source_key, counts)
