"""Unit 1 curation, wave 3: grammar Q&A "PRACTICE" (활용) drills from the
vocab_grammar booklet's 이에요/예요 page (page 32). Only page 32's pair is
usable - page 33's (은/는) practice Q&A blocks are NEEDS_REVIEW on the
answer side, so they are deliberately skipped per the project's
APPROVED/EDITED-only rule (see /memories/repo/phase1-scaffold.md).

Run with backend/.venv active:
    cd backend && source .venv/bin/activate && cd ..
    python -m content_pipeline.curate_unit1_wave3
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

PROPOSED_BY = "assistant:curate_unit1_wave3"

# (prompt_question, accepted_answer, source page, source block_index of the answer)
# Source: data/verified/vocab_grammar/page_032.json blocks 35/38 and 39/40,
# both APPROVED.
GRAMMAR_PRACTICE_QA: list[tuple[str, str, int, int]] = [
    ("가: 회사원이에요? 나: 네. ___", "회사원이에요", 32, 38),
    ("가: 모자예요? 나: 네. ___", "모자예요", 32, 40),
]


def _load_backend_models():
    from app.db.session import SessionLocal
    from app.models.activity import AcceptedAnswer, Activity
    from app.models.content_source import ContentBlock, ContentSource
    from app.models.curriculum import GrammarPoint, Lesson, Unit
    from app.models.enums import ActivityType, CurationStatus, SourceType

    return {
        "SessionLocal": SessionLocal,
        "AcceptedAnswer": AcceptedAnswer,
        "Activity": Activity,
        "ContentBlock": ContentBlock,
        "ContentSource": ContentSource,
        "GrammarPoint": GrammarPoint,
        "Lesson": Lesson,
        "Unit": Unit,
        "ActivityType": ActivityType,
        "CurationStatus": CurationStatus,
        "SourceType": SourceType,
    }


def curate_unit1_wave3() -> dict[str, int]:
    m = _load_backend_models()
    db = m["SessionLocal"]()
    try:
        unit = db.query(m["Unit"]).filter_by(number="01").one()
        lesson = db.query(m["Lesson"]).filter_by(unit_id=unit.id).one()
        vg_source = db.query(m["ContentSource"]).filter_by(source_type=m["SourceType"].VOCAB_GRAMMAR).one()
        grammar_point = db.query(m["GrammarPoint"]).filter_by(lesson_id=lesson.id, name_ko="이에요/예요").one()

        def block_id(page: int, index: int):
            block = db.query(m["ContentBlock"]).filter_by(source_id=vg_source.id, page_number=page, block_index=index).one()
            return block.id

        created = {"activities": 0}
        for prompt, answer, page, idx in GRAMMAR_PRACTICE_QA:
            existing = db.query(m["Activity"]).filter_by(lesson_id=lesson.id, prompt=prompt).one_or_none()
            if existing is not None:
                continue
            activity = m["Activity"](
                lesson_id=lesson.id,
                type=m["ActivityType"].GRAMMAR_PRACTICE,
                prompt=prompt,
                activity_metadata={"grammar_point_id": str(grammar_point.id)},
                source_block_id=block_id(page, idx),
                curation_status=m["CurationStatus"].DRAFT,
                proposed_by=PROPOSED_BY,
            )
            db.add(activity)
            db.flush()
            db.add(m["AcceptedAnswer"](activity_id=activity.id, answer_text=answer, is_primary=True))
            created["activities"] += 1

        db.commit()
        return created
    finally:
        db.close()


if __name__ == "__main__":
    result = curate_unit1_wave3()
    print(f"Unit 1 curation draft (wave 3): {result}")
