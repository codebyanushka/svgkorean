"""Promote + import vocab_grammar Part-1 (vocabulary list) pages for units
2-10 into the database as ContentBlock rows.

Unlike ``seed.py``'s ``seed_unit()``, this does NOT require textbook/
workbook/grammar(Part-2)/additional_activities pages to be rendered+verified
- the Vocabulary Memory Lab product only needs the vocabulary list itself,
so only ``VOCAB_GRAMMAR_PART1_RANGES`` pages are promoted+imported here.
Reuses ``promote_page``/``import_page_blocks``/``get_or_create_unit_and_lesson``/
``get_or_create_content_source`` from ``content_pipeline.seed`` unchanged.

Run with backend/.venv active:
    cd backend && source .venv/bin/activate && cd ..
    python -m content_pipeline.seed_vocab_units
"""

from __future__ import annotations

from content_pipeline import config
from content_pipeline.seed import (
    _load_backend_models,
    get_or_create_content_source,
    get_or_create_unit_and_lesson,
    import_page_blocks,
    promote_page,
)

SOURCE_KEY = "vocab_grammar"


def seed_vocab_unit(unit_number: int) -> dict[str, int]:
    pages = config.unit_pages_by_number(config.VOCAB_GRAMMAR_PART1_RANGES, unit_number)
    for page_number in pages:
        promote_page(SOURCE_KEY, page_number)

    SessionLocal, ContentSource, ContentBlock, Unit, Lesson, SourceType = _load_backend_models()
    session = SessionLocal()
    try:
        unit, lesson = get_or_create_unit_and_lesson(session, Unit, Lesson, unit_number)
        source = get_or_create_content_source(session, ContentSource, SourceType, SOURCE_KEY)
        counts: dict[str, int] = {}
        for page_number in pages:
            page_counts = import_page_blocks(session, ContentBlock, source, unit, lesson, SOURCE_KEY, page_number)
            for status, n in page_counts.items():
                counts[status] = counts.get(status, 0) + n
        session.commit()
        return counts
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    for unit_number in range(2, 11):
        counts = seed_vocab_unit(unit_number)
        print(f"unit {unit_number}: {counts}")


if __name__ == "__main__":
    main()
