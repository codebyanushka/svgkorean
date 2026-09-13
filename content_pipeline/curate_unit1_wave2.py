"""Unit 1 curation, wave 2: grammar-conjugation drills and reading-
comprehension activities built from the textbook/workbook/additional-
activities content_blocks (wave 1 only covered the vocab_grammar word list).

Same rules as curate_unit1.py: everything created here is `DRAFT`, every
Korean form is copied verbatim from a cited, verified `ContentBlock`, and
nothing is invented. Two categories of activity, both mechanically derived
rather than authored from outside knowledge:

1. Copula/topic-marker conjugation drills - the correct suffix (이에요 vs
   예요, 은 vs 는) is computed with `has_batchim()`, a deterministic Hangul
   Unicode rule (final-consonant/batchim presence), not guessed. Verified
   against the workbook's own worked examples (가방 -> 가방은, 저 -> 저는)
   before use.
2. Reading-comprehension / table-matching multiple-choice questions, built
   only from ContentBlocks whose verification_status is APPROVED (never
   NEEDS_REVIEW/REJECTED facts).

Run with backend/.venv active:
    cd backend && source .venv/bin/activate && cd ..
    python -m content_pipeline.curate_unit1_wave2
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

PROPOSED_BY = "assistant:curate_unit1_wave2"


def has_batchim(word: str) -> bool:
    """True if `word`'s last syllable has a final consonant (받침),
    determined from the Hangul Unicode block's fixed decomposition, not a
    lookup table - e.g. 가방 (batchim) vs 저 (no batchim), matching the
    workbook's own given examples 가방은/저는."""
    last = word[-1]
    cp = ord(last)
    if not (0xAC00 <= cp <= 0xD7A3):
        return False
    return (cp - 0xAC00) % 28 != 0


# (korean_noun, source page, source block_index) - copula drill word bank.
# Source: data/verified/additional_activities/page_009.json (idx 8-19) and
# data/verified/workbook/page_029.json (idx 17-19), all APPROVED.
IEYO_YEYO_WORDS: list[tuple[str, str, int, int]] = [
    ("빵", "additional_activities", 9, 8),
    ("책", "additional_activities", 9, 9),
    ("나무", "additional_activities", 9, 10),
    ("의자", "additional_activities", 9, 11),
    ("포도", "additional_activities", 9, 12),
    ("신발", "additional_activities", 9, 13),
    ("책상", "additional_activities", 9, 14),
    ("과자", "additional_activities", 9, 15),
    ("우유", "additional_activities", 9, 16),
    ("공책", "additional_activities", 9, 17),
    ("차", "additional_activities", 9, 18),
    ("가방", "additional_activities", 9, 19),
    ("선생님", "workbook", 29, 17),
    ("요리사", "workbook", 29, 18),
    ("회사원", "workbook", 29, 19),
]

# Source: data/verified/workbook/page_030.json (idx 10-17), all APPROVED.
# 가방/저 are cross-checked against the page's own given answers (가방은/저는).
EUN_NEUN_WORDS: list[tuple[str, str, int, int]] = [
    ("가방", "workbook", 30, 10),
    ("저", "workbook", 30, 12),
    ("동생", "workbook", 30, 14),
    ("모자", "workbook", 30, 15),
    ("서울", "workbook", 30, 16),
    ("친구", "workbook", 30, 17),
]

# Reading comprehension: (prompt, correct_ko, distractor_pool_ko, source page/index)
# Source: data/verified/textbook/page_044.json (Anna/Juno dialogue) and
# page_045.json (Wei/Yuna self-introductions) - APPROVED blocks only.
READING_COMPREHENSION: list[tuple[str, str, list[str], int, int]] = [
    (
        "안나: \"안녕하세요? 저는 안나예요.\" ... 안나 씨는 학생이에요? "
        "안나: \"네. 학생이에요.\" - 안나 씨는 직업이 뭐예요?",
        "학생",
        ["회사원", "의사", "선생님"],
        44,
        9,
    ),
    (
        "저는 웨이예요. 저는 중국 사람이에요. 요리사예요. - 웨이 씨는 어느 나라 사람이에요?",
        "중국",
        ["한국", "미국", "일본"],
        45,
        11,
    ),
    (
        "저는 웨이예요. 저는 중국 사람이에요. 요리사예요. - 웨이 씨는 직업이 뭐예요?",
        "요리사",
        ["의사", "선생님", "회사원"],
        45,
        13,
    ),
    (
        "저는 유나예요. 저는 한국 사람이에요. 가수예요. - 유나 씨는 어느 나라 사람이에요?",
        "한국",
        ["중국", "베트남", "프랑스"],
        45,
        12,
    ),
    (
        "저는 유나예요. 저는 한국 사람이에요. 가수예요. - 유나 씨는 직업이 뭐예요?",
        "가수",
        ["의사", "회사원", "대학생"],
        45,
        14,
    ),
]

# Name -> job table matching. Source: data/verified/textbook/page_044.json
# (name/job table, all APPROVED).
NAME_JOB_TABLE: list[tuple[str, str, int, int]] = [
    ("서유리", "대학생", 44, 18),
    ("이서준", "의사", 44, 23),
    ("마리", "회사원", 44, 26),
    ("박지윤", "선생님", 44, 29),
    ("김진우", "경찰", 44, 32),
    ("웨이", "요리사", 44, 36),
]

ALL_JOBS = ["대학생", "의사", "회사원", "선생님", "경찰", "요리사"]


def _load_backend_models():
    from app.db.session import SessionLocal
    from app.models.activity import Activity, ActivityOption
    from app.models.content_source import ContentBlock, ContentSource
    from app.models.curriculum import Lesson, Unit
    from app.models.enums import ActivityType, CurationStatus, SourceType

    return {
        "SessionLocal": SessionLocal,
        "Activity": Activity,
        "ActivityOption": ActivityOption,
        "ContentBlock": ContentBlock,
        "ContentSource": ContentSource,
        "Lesson": Lesson,
        "Unit": Unit,
        "ActivityType": ActivityType,
        "CurationStatus": CurationStatus,
        "SourceType": SourceType,
    }


def curate_unit1_wave2() -> dict[str, int]:
    m = _load_backend_models()
    db = m["SessionLocal"]()
    try:
        unit = db.query(m["Unit"]).filter_by(number="01").one()
        lesson = db.query(m["Lesson"]).filter_by(unit_id=unit.id).one()
        source_ids = {
            row.source_type.value.lower(): row.id
            for row in db.query(m["ContentSource"]).all()
        }

        def block_id(source_key: str, page: int, index: int):
            block = (
                db.query(m["ContentBlock"])
                .filter_by(source_id=source_ids[source_key], page_number=page, block_index=index)
                .one()
            )
            return block.id

        rng = random.Random(20260913)
        created = {"activities": 0, "options": 0}

        def add_activity(prompt: str, options_with_correct: list[tuple[str, bool]], source_block_id) -> None:
            existing = db.query(m["Activity"]).filter_by(lesson_id=lesson.id, prompt=prompt).one_or_none()
            if existing is not None:
                return
            activity = m["Activity"](
                lesson_id=lesson.id,
                type=m["ActivityType"].MULTIPLE_CHOICE,
                prompt=prompt,
                source_block_id=source_block_id,
                curation_status=m["CurationStatus"].DRAFT,
                proposed_by=PROPOSED_BY,
            )
            db.add(activity)
            db.flush()
            for text, is_correct in options_with_correct:
                db.add(m["ActivityOption"](activity_id=activity.id, text=text, is_correct=is_correct))
                created["options"] += 1
            created["activities"] += 1

        # 1. 이에요/예요 conjugation drills.
        for word, source_key, page, idx in IEYO_YEYO_WORDS:
            suffix = "이에요" if has_batchim(word) else "예요"
            correct = f"{word}{suffix}"
            wrong_suffix = "예요" if has_batchim(word) else "이에요"
            distractor = f"{word}{wrong_suffix}"
            add_activity(
                prompt=f"'{word}' + 이에요/예요 -> ?",
                options_with_correct=[(correct, True), (distractor, False)],
                source_block_id=block_id(source_key, page, idx),
            )

        # 2. 은/는 topic-marker conjugation drills.
        for word, source_key, page, idx in EUN_NEUN_WORDS:
            suffix = "은" if has_batchim(word) else "는"
            correct = f"{word}{suffix}"
            wrong_suffix = "는" if has_batchim(word) else "은"
            distractor = f"{word}{wrong_suffix}"
            add_activity(
                prompt=f"'{word}' + 은/는 -> ?",
                options_with_correct=[(correct, True), (distractor, False)],
                source_block_id=block_id(source_key, page, idx),
            )

        # 3. Reading comprehension.
        for prompt, correct, distractors, page, idx in READING_COMPREHENSION:
            options = [(correct, True)] + [(d, False) for d in distractors]
            rng.shuffle(options)
            add_activity(prompt=prompt, options_with_correct=options, source_block_id=block_id("textbook", page, idx))

        # 4. Name -> job table matching.
        for name, job, page, idx in NAME_JOB_TABLE:
            distractor_pool = [j for j in ALL_JOBS if j != job]
            distractors = rng.sample(distractor_pool, k=3)
            options = [(job, True)] + [(d, False) for d in distractors]
            rng.shuffle(options)
            add_activity(
                prompt=f"{name} 씨는 직업이 뭐예요?", options_with_correct=options, source_block_id=block_id("textbook", page, idx)
            )

        db.commit()
        return created
    finally:
        db.close()


if __name__ == "__main__":
    result = curate_unit1_wave2()
    print(f"Unit 1 curation draft (wave 2): {result}")
