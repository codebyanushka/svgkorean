"""Unit 1 curation, wave 6: a real dialogue-reading activity for the
textbook p.44 Anna/Juno opener dialogue (활동 1), rendered by the frontend
as an illustrated "Listen and read" card rather than a quiz question.

Speaker attribution for block 8 ("안나 씨는 학생이에요?") was not captured
with an explicit speaker tag by OCR, but the surrounding APPROVED text plus
direct visual inspection of the rendered page image (both characters'
speech bubbles) confirms it's 주노's line, combined with his own
introduction into one turn - re-confirmed against the actual page image
during this session, not guessed from text alone.

Run with backend/.venv active:
    cd backend && source .venv/bin/activate && cd ..
    python -m content_pipeline.curate_unit1_wave6
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

PROPOSED_BY = "assistant:curate_unit1_wave6"

DIALOGUE = [
    {"speaker": "안나", "avatar": "female", "text": "안녕하세요? 저는 안나예요."},
    {"speaker": "주노", "avatar": "male", "text": "안녕하세요? 저는 주노예요. 안나 씨는 학생이에요?"},
    {"speaker": "안나", "avatar": "female", "text": "네. 학생이에요. 주노 씨는요?"},
    {"speaker": "주노", "avatar": "male", "text": "저는 회사원이에요."},
]
PROMPT = "1. Anna and Juno meet and greet each other for the first time."
SOURCE_PAGE = 44
SOURCE_BLOCK_INDEX = 6


def _load_backend_models():
    from app.db.session import SessionLocal
    from app.models.activity import Activity
    from app.models.content_source import ContentBlock, ContentSource
    from app.models.curriculum import Lesson, Unit
    from app.models.enums import ActivityType, CurationStatus, SourceType

    return {
        "SessionLocal": SessionLocal,
        "Activity": Activity,
        "ContentBlock": ContentBlock,
        "ContentSource": ContentSource,
        "Lesson": Lesson,
        "Unit": Unit,
        "ActivityType": ActivityType,
        "CurationStatus": CurationStatus,
        "SourceType": SourceType,
    }


def curate_unit1_wave6() -> dict[str, int]:
    m = _load_backend_models()
    db = m["SessionLocal"]()
    try:
        unit = db.query(m["Unit"]).filter_by(number="01").one()
        lesson = db.query(m["Lesson"]).filter_by(unit_id=unit.id).one()
        tb_source = db.query(m["ContentSource"]).filter_by(source_type=m["SourceType"].TEXTBOOK).one()
        source_block = (
            db.query(m["ContentBlock"])
            .filter_by(source_id=tb_source.id, page_number=SOURCE_PAGE, block_index=SOURCE_BLOCK_INDEX)
            .one()
        )

        existing = db.query(m["Activity"]).filter_by(lesson_id=lesson.id, prompt=PROMPT).one_or_none()
        if existing is not None:
            return {"activities": 0}

        db.add(
            m["Activity"](
                lesson_id=lesson.id,
                type=m["ActivityType"].READING,
                prompt=PROMPT,
                activity_metadata={"dialogue": DIALOGUE},
                source_block_id=source_block.id,
                curation_status=m["CurationStatus"].DRAFT,
                proposed_by=PROPOSED_BY,
            )
        )
        db.commit()
        return {"activities": 1}
    finally:
        db.close()


if __name__ == "__main__":
    result = curate_unit1_wave6()
    print(f"Unit 1 curation draft (wave 6, dialogue reading): {result}")
