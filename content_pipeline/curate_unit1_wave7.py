"""Unit 1 curation, wave 7: extend the illustrated "Listen and read" dialogue
treatment (see wave 6) to the rest of Unit 1's dialogue/reading passages
across all 4 source books - reusing the same 2 character portraits
(female_student.png / male_student.png) for every card, per the user's own
character-consistency spec. Every line of text here was already verified
and used in an earlier wave (3/4/5) for a quiz activity - this wave adds a
READ-ONLY display companion for the SAME cited facts, not new claims.

Speaker-to-portrait assignment: named characters use their established
identity (안나/유나/지은 -> female; 주노/웨이/재민/진우 -> male). Anonymous
"가"/"나" dialogue-drill lines (no named speaker) alternate female/나 male
for visual variety only - the book itself never assigns a specific gender
to "가"/"나", so this is a presentation choice, not a claimed fact.

Run with backend/.venv active:
    cd backend && source .venv/bin/activate && cd ..
    python -m content_pipeline.curate_unit1_wave7
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

PROPOSED_BY = "assistant:curate_unit1_wave7"

F, M = "female", "male"

# (prompt, dialogue_lines, source_type, page, block_index)
CARDS: list[tuple[str, list[dict], str, int, int]] = [
    (
        "textbook p.41 - Look at the pictures and complete the conversations.",
        [
            {"speaker": "가", "avatar": F, "text": "학생이에요?"},
            {"speaker": "나", "avatar": M, "text": "네. 학생이에요."},
        ],
        "TEXTBOOK",
        41,
        39,
    ),
    (
        "textbook p.42 - Look at the pictures and talk with a partner. (1: 한복)",
        [
            {"speaker": "가", "avatar": F, "text": "한복이에요?"},
            {"speaker": "나", "avatar": M, "text": "네. 한복이에요."},
        ],
        "TEXTBOOK",
        42,
        19,
    ),
    (
        "textbook p.42 - Look at the pictures and talk with a partner. (2: 커피)",
        [
            {"speaker": "가", "avatar": M, "text": "커피예요?"},
            {"speaker": "나", "avatar": F, "text": "네. 커피예요."},
        ],
        "TEXTBOOK",
        42,
        23,
    ),
    (
        "textbook p.42 - Look at the pictures and talk with a partner. (3: 동생)",
        [
            {"speaker": "가", "avatar": F, "text": "언니예요?"},
            {"speaker": "나", "avatar": M, "text": "아니요. 동생이에요."},
        ],
        "TEXTBOOK",
        42,
        28,
    ),
    (
        "textbook p.42 - Look at the pictures and talk with a partner. (4: 미국 사람)",
        [
            {"speaker": "가", "avatar": M, "text": "프랑스 사람이에요?"},
            {"speaker": "나", "avatar": F, "text": "아니요. 미국 사람이에요."},
        ],
        "TEXTBOOK",
        42,
        33,
    ),
    (
        "textbook p.43 - 은/는 grammar practice dialogue. (1: 동생/대학생)",
        [
            {"speaker": "가", "avatar": F, "text": "유진 씨 동생은 대학생이에요?"},
            {"speaker": "나", "avatar": M, "text": "네. 제 동생은 대학생이에요."},
        ],
        "TEXTBOOK",
        43,
        9,
    ),
    (
        "textbook p.43 - 은/는 grammar practice dialogue. (2: 아버지/요리사)",
        [
            {"speaker": "가", "avatar": M, "text": "아버지는 요리사예요?"},
            {"speaker": "나", "avatar": F, "text": "네. 아버지는 요리사예요."},
        ],
        "TEXTBOOK",
        43,
        11,
    ),
    (
        "textbook p.45 - Read the following self-introductions.",
        [
            {"speaker": "웨이", "avatar": M, "text": "안녕하세요? 저는 웨이예요. 저는 중국 사람이에요. 요리사예요."},
        ],
        "TEXTBOOK",
        45,
        9,
    ),
    (
        "textbook p.45 - Read the following self-introductions.",
        [
            {"speaker": "유나", "avatar": F, "text": "안녕하세요? 저는 유나예요. 저는 한국 사람이에요. 가수예요."},
        ],
        "TEXTBOOK",
        45,
        10,
    ),
    (
        "workbook p.32 - 읽기 (Reading): 소개 1.",
        [
            {
                "speaker": "재민",
                "avatar": M,
                "text": (
                    "저는 박재민이에요. 이 사람은 제 동생이에요. 한국 사람이에요. "
                    "이름은 박지은이에요. 저는 회사원이에요. 제 동생은 한국어 선생님이에요."
                ),
            },
        ],
        "WORKBOOK",
        32,
        11,
    ),
    (
        "additional_activities p.11 - 읽고 쓰기: 친구 소개.",
        [
            {"speaker": "가", "avatar": F, "text": "이 사람은 제 친구예요. 이름은 김진우예요. 한국 사람이에요. 진우 씨는 경찰이에요."},
        ],
        "ADDITIONAL_ACTIVITIES",
        11,
        9,
    ),
    (
        "additional_activities p.9 - 가:누구예요? completion practice. (1: 친구)",
        [
            {"speaker": "가", "avatar": M, "text": "누구예요?"},
            {"speaker": "나", "avatar": F, "text": "제 친구예요. 제 친구는 대학생이에요."},
        ],
        "ADDITIONAL_ACTIVITIES",
        9,
        34,
    ),
    (
        "additional_activities p.9 - 가:누구예요? completion practice. (2: 유나)",
        [
            {"speaker": "가", "avatar": F, "text": "누구예요?"},
            {"speaker": "나", "avatar": M, "text": "유나예요. 유나 씨는 가수예요."},
        ],
        "ADDITIONAL_ACTIVITIES",
        9,
        39,
    ),
]


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


def curate_unit1_wave7() -> dict[str, int]:
    m = _load_backend_models()
    db = m["SessionLocal"]()
    try:
        unit = db.query(m["Unit"]).filter_by(number="01").one()
        lesson = db.query(m["Lesson"]).filter_by(unit_id=unit.id).one()
        source_cache = {}

        def get_source(source_type: str):
            if source_type not in source_cache:
                source_cache[source_type] = db.query(m["ContentSource"]).filter_by(source_type=m["SourceType"][source_type]).one()
            return source_cache[source_type]

        created = 0
        for prompt, dialogue, source_type, page, idx in CARDS:
            existing = db.query(m["Activity"]).filter_by(lesson_id=lesson.id, prompt=prompt).one_or_none()
            if existing is not None:
                continue
            src = get_source(source_type)
            block = db.query(m["ContentBlock"]).filter_by(source_id=src.id, page_number=page, block_index=idx).one()
            db.add(
                m["Activity"](
                    lesson_id=lesson.id,
                    type=m["ActivityType"].READING,
                    prompt=prompt,
                    activity_metadata={"dialogue": dialogue},
                    source_block_id=block.id,
                    curation_status=m["CurationStatus"].DRAFT,
                    proposed_by=PROPOSED_BY,
                )
            )
            created += 1

        db.commit()
        return {"activities": created}
    finally:
        db.close()


if __name__ == "__main__":
    result = curate_unit1_wave7()
    print(f"Unit 1 curation draft (wave 7, dialogue cards): {result}")
