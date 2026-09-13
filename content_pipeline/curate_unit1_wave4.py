"""Unit 1 curation, wave 4: textbook pages 41-43 (the two grammar-explanation
pages plus the vocabulary listen&repeat page), done one page at a time with
each dialogue's source block re-confirmed against the rendered page image
before use - see /memories/repo/hangugeo-backend-facts.md for the
page-by-page review notes.

Same rules as previous waves: DRAFT only, every Korean form copied verbatim
from a cited APPROVED/EDITED ContentBlock, nothing invented. Two safe,
mechanical patterns used here (both already validated in wave 2/3):
1. A "네" (yes) answer in this textbook always echoes the exact word from
   the question - the correct 이에요/예요 suffix is picked by `has_batchim()`
   (same deterministic Hangul-batchim rule as wave 2), never guessed.
2. Several picture-based fill-in-the-blank items on page 42 include the
   picture's identifying word in parentheses right next to the dialogue
   (e.g. "가: 언니예요? 나: 아니요. (동생)") - used ONLY where both the
   question and the parenthetical answer word are APPROVED and unambiguous.
   Items where the parenthetical/answer was NEEDS_REVIEW, duplicated, or
   its pairing to a specific numbered item was genuinely ambiguous (most of
   page 43's picture grid) were deliberately left out - not guessed.

Run with backend/.venv active:
    cd backend && source .venv/bin/activate && cd ..
    python -m content_pipeline.curate_unit1_wave4
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

PROPOSED_BY = "assistant:curate_unit1_wave4"


def has_batchim(word: str) -> bool:
    """Same deterministic Hangul-batchim rule as wave 2's has_batchim()."""
    last = word[-1]
    cp = ord(last)
    if not (0xAC00 <= cp <= 0xD7A3):
        return False
    return (cp - 0xAC00) % 28 != 0


def echo_answer(word: str) -> str:
    suffix = "이에요" if has_batchim(word) else "예요"
    return f"{word}{suffix}"


# (prompt_question, echoed_word, source page, source block_index of the
# fact grounding the answer) - "네" (yes) answers, safe to construct
# mechanically since this textbook's yes-answers always echo the question's
# own word (already validated in wave 3).
ECHO_QA: list[tuple[str, str, int, int]] = [
    # p.41 section 3 item 1) - APPROVED throughout.
    ("가: 학생이에요? 나: 네. ___", "학생", 41, 39),
    # p.42 section 1 items 1)/2) - both question+parenthetical APPROVED.
    ("가: 한복이에요? 나: 네. ___", "한복", 42, 19),
    ("가: 커피예요? 나: 네. ___", "커피", 42, 23),
]

# (prompt_question, answer_word, source page, source block_index) - "아니요"
# (no) answers where the picture's identifying word is given verbatim in an
# APPROVED parenthetical right next to the dialogue - not guessed from the
# picture itself, read directly from the page's own text.
CORRECTION_QA: list[tuple[str, str, int, int]] = [
    ("가: 언니예요? 나: 아니요. ___", "동생", 42, 28),
    ("가: 프랑스 사람이에요? 나: 아니요. ___", "미국 사람", 42, 33),
]

# (prompt, accepted_answer, source page, source block_index) - fully given
# Q&A pairs (both sides APPROVED) copied verbatim, no suffix computation.
VERBATIM_QA: list[tuple[str, str, int, int]] = [
    ("가: 유진 씨 동생은 대학생이에요? 나: ___", "네. 제 동생은 대학생이에요", 43, 9),
    ("가: 아버지는 요리사예요? 나: ___", "네. 아버지는 요리사예요", 43, 11),
]

# Reading comprehension: p.42's sample dialogue ("가: 누구예요? 나: 친구예요.
# 가: 한국 사람이에요? 나: 아니요. 태국 사람이에요.") - all 4 lines APPROVED.
READING_PROMPT = (
    "가: 누구예요? 나: 친구예요. 가: 한국 사람이에요? 나: 아니요. 태국 사람이에요. "
    "- 친구는 어느 나라 사람이에요?"
)
READING_CORRECT = "태국"
READING_DISTRACTOR_POOL = ["한국", "캐나다", "베트남", "미국", "프랑스", "인도네시아", "중국", "일본", "러시아", "케냐"]
READING_SOURCE = (42, 45)


def _load_backend_models():
    from app.db.session import SessionLocal
    from app.models.activity import AcceptedAnswer, Activity, ActivityOption
    from app.models.content_source import ContentBlock, ContentSource
    from app.models.curriculum import Lesson, Unit
    from app.models.enums import ActivityType, CurationStatus, SourceType

    return {
        "SessionLocal": SessionLocal,
        "AcceptedAnswer": AcceptedAnswer,
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


def curate_unit1_wave4() -> dict[str, int]:
    m = _load_backend_models()
    db = m["SessionLocal"]()
    try:
        unit = db.query(m["Unit"]).filter_by(number="01").one()
        lesson = db.query(m["Lesson"]).filter_by(unit_id=unit.id).one()
        tb_source = db.query(m["ContentSource"]).filter_by(source_type=m["SourceType"].TEXTBOOK).one()

        def block_id(page: int, index: int):
            block = db.query(m["ContentBlock"]).filter_by(source_id=tb_source.id, page_number=page, block_index=index).one()
            return block.id

        created = {"activities": 0}

        def add_fill_blank(prompt: str, answer: str, page: int, idx: int) -> None:
            existing = db.query(m["Activity"]).filter_by(lesson_id=lesson.id, prompt=prompt).one_or_none()
            if existing is not None:
                return
            activity = m["Activity"](
                lesson_id=lesson.id,
                type=m["ActivityType"].GRAMMAR_PRACTICE,
                prompt=prompt,
                source_block_id=block_id(page, idx),
                curation_status=m["CurationStatus"].DRAFT,
                proposed_by=PROPOSED_BY,
            )
            db.add(activity)
            db.flush()
            db.add(m["AcceptedAnswer"](activity_id=activity.id, answer_text=answer, is_primary=True))
            created["activities"] += 1

        for prompt, word, page, idx in ECHO_QA:
            add_fill_blank(prompt, echo_answer(word), page, idx)

        for prompt, word, page, idx in CORRECTION_QA:
            add_fill_blank(prompt, echo_answer(word), page, idx)

        for prompt, answer, page, idx in VERBATIM_QA:
            add_fill_blank(prompt, answer, page, idx)

        # Reading comprehension multiple-choice.
        existing = db.query(m["Activity"]).filter_by(lesson_id=lesson.id, prompt=READING_PROMPT).one_or_none()
        if existing is None:
            rng = random.Random(20260913)
            distractors = rng.sample(READING_DISTRACTOR_POOL, k=3)
            options = [(READING_CORRECT, True)] + [(d, False) for d in distractors]
            rng.shuffle(options)
            activity = m["Activity"](
                lesson_id=lesson.id,
                type=m["ActivityType"].MULTIPLE_CHOICE,
                prompt=READING_PROMPT,
                source_block_id=block_id(*READING_SOURCE),
                curation_status=m["CurationStatus"].DRAFT,
                proposed_by=PROPOSED_BY,
            )
            db.add(activity)
            db.flush()
            for text, is_correct in options:
                db.add(m["ActivityOption"](activity_id=activity.id, text=text, is_correct=is_correct))
            created["activities"] += 1

        db.commit()
        return created
    finally:
        db.close()


if __name__ == "__main__":
    result = curate_unit1_wave4()
    print(f"Unit 1 curation draft (wave 4, textbook pp.41-43): {result}")
