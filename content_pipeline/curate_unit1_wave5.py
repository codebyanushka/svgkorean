"""Unit 1 curation, wave 5: workbook pp.28-33 and additional_activities
pp.8-11, done page-by-page against the rendered images (not a bulk
mechanical pass) - see /memories/repo/hangugeo-backend-facts.md for the
page-by-page review notes.

Same rules as previous waves: DRAFT only, nothing invented. A few items
here cite a ContentBlock whose `verification_status` is still NEEDS_REVIEW
in the DB, but whose text was re-confirmed directly against the rendered
page image during this session (typeset info-card/caption text, not
handwriting) - this is the same AI-vision-preliminary-review precedent
already used once before in this project (see phase1-scaffold.md's textbook
p.40 demo pass), NOT a claim of certified human sign-off. Each such case is
called out in a comment. Genuinely ambiguous items (jumbled reading order,
garbled captions, picture-dependent facts with no caption text at all) were
left out entirely, same as prior waves.

Run with backend/.venv active:
    cd backend && source .venv/bin/activate && cd ..
    python -m content_pipeline.curate_unit1_wave5
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

PROPOSED_BY = "assistant:curate_unit1_wave5"

COUNTRY_POOL = ["한국", "캐나다", "베트남", "미국", "프랑스", "태국", "인도네시아", "중국", "일본", "러시아", "케냐"]
JOB_POOL = ["회사원", "대학생", "의사", "경찰", "선생님", "가수", "요리사", "학생"]
NAME_POOL = ["안나", "주노", "웨이", "유나", "마리", "민호", "서유리", "이서준", "박지윤", "김진우"]


def has_batchim(word: str) -> bool:
    last = word[-1]
    cp = ord(last)
    if not (0xAC00 <= cp <= 0xD7A3):
        return False
    return (cp - 0xAC00) % 28 != 0


def echo_answer(word: str) -> str:
    return f"{word}{'이에요' if has_batchim(word) else '예요'}"


# --- additional_activities p.8: nationality captions given verbatim next to
# 3 numbered pictures (2. 그림을 보고 친구와 이야기해 보세요) - all APPROVED.
AA_P8_NATIONALITY: list[tuple[str, str, int]] = [
    ("1번 그림 속 사람의 국적은 어디예요?", "캐나다", 34),
    ("2번 그림 속 사람의 국적은 어디예요?", "인도네시아", 35),
    ("3번 그림 속 사람의 국적은 어디예요?", "태국", 44),
]

# --- additional_activities p.9 section 2: "가:누구예요? 나:[subject]예요."
# + a (subject, role) caption, following the page's own worked example
# ("재민 씨는 회사원이에요."). Re-confirmed directly against the rendered
# image (block statuses: only item 2's caption is APPROVED; items 1/3/4 are
# NEEDS_REVIEW in the DB but clearly legible typeset text in the image).
AA_P9_WHO_IS_THIS: list[tuple[str, str, int]] = [
    ("가: 누구예요? 나: 제 친구예요. 제 친구는 ___", "대학생", 34),
    ("가: 누구예요? 나: 유나예요. 유나 씨는 ___", "가수", 39),
    ("가: 누구예요? 나: 선생님이에요. 선생님은 ___", "한국 사람", 44),
    ("가: 누구예요? 나: 누나예요. 누나는 ___", "의사", 50),
]

# --- additional_activities p.10 section 2: 이름/국적/직업 info cards.
# 마리's job ("회사원") was already curated in wave 2 from a different page -
# only her NEW nationality fact is added here. 민호 is a new name entirely.
# Re-confirmed directly against the rendered image (block statuses: 직업:학생
# is APPROVED; the rest are NEEDS_REVIEW in the DB but clearly legible
# typeset text).
AA_P10_PROFILE: list[tuple[str, str, str, int]] = [
    ("민호 씨는 어느 나라 사람이에요?", "한국", "country", 24),
    ("민호 씨는 직업이 뭐예요?", "학생", "job", 22),
    ("마리 씨는 어느 나라 사람이에요?", "일본", "country", 28),
]

# --- additional_activities p.11: a complete 4-sentence reading passage,
# APPROVED except the combined name+nationality sentence (block 8, NEEDS_
# REVIEW in the DB but clearly legible in the image - re-confirmed).
AA_P11_PASSAGE = "이 사람은 제 친구예요. 이름은 김진우예요. 한국 사람이에요. 진우 씨는 경찰이에요."
AA_P11_QUESTIONS: list[tuple[str, str, str, int]] = [
    ("이 사람의 이름이 뭐예요?", "김진우", "name", 8),
    ("이 사람은 어느 나라 사람이에요?", "한국", "country", 8),
    ("이 사람의 직업은 뭐예요?", "경찰", "job", 9),
]

# --- workbook p.28 item 3: compound question, both APPROVED.
WB_P28_QA = ("가: 학생이에요? 어느 나라 사람이에요? 나: 아니요. ___", "저는 케냐 사람이에요", 37)

# --- workbook p.29 section 2: choose 이에요 vs 예요 - both APPROVED.
WB_P29_CHOICE: list[tuple[str, str, int]] = [
    ("선생님( 이에요 / 예요 ).", "선생님", 25),
    ("모자( 이에요 / 예요 ).", "모자", 27),
]

# --- workbook p.30 section 3 item 4: both APPROVED.
WB_P30_QA = ("제 동생 / 학생 -> ___", "제 동생은 학생이에요", 46)

# --- workbook p.32: reading passage (all APPROVED) + comprehension.
WB_P32_PASSAGE = (
    "저는 박재민이에요. 이 사람은 제 동생이에요. 한국 사람이에요. "
    "이름은 박지은이에요. 저는 회사원이에요. 제 동생은 한국어 선생님이에요."
)
WB_P32_JOB_Q = ("지은 씨의 직업이 뭐예요?", "한국어 선생님", 11)
# The statement to evaluate is block 21 ("재민 씨는 대학생이에요") but the
# fact that GROUNDS the false verdict is block 10 ("저는 회사원이에요.").
WB_P32_STATEMENT = "재민 씨는 대학생이에요."
WB_P32_GROUNDING_BLOCK = 10


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


def curate_unit1_wave5() -> dict[str, int]:
    m = _load_backend_models()
    db = m["SessionLocal"]()
    try:
        unit = db.query(m["Unit"]).filter_by(number="01").one()
        lesson = db.query(m["Lesson"]).filter_by(unit_id=unit.id).one()
        aa_source = db.query(m["ContentSource"]).filter_by(source_type=m["SourceType"].ADDITIONAL_ACTIVITIES).one()
        wb_source = db.query(m["ContentSource"]).filter_by(source_type=m["SourceType"].WORKBOOK).one()
        rng = random.Random(20260913)

        created = {"activities": 0}

        def block_id(source_id, page: int, index: int):
            return db.query(m["ContentBlock"]).filter_by(source_id=source_id, page_number=page, block_index=index).one().id

        def add_fill_blank(prompt: str, answer: str, source_id, page: int, idx: int) -> None:
            if db.query(m["Activity"]).filter_by(lesson_id=lesson.id, prompt=prompt).one_or_none() is not None:
                return
            activity = m["Activity"](
                lesson_id=lesson.id,
                type=m["ActivityType"].GRAMMAR_PRACTICE,
                prompt=prompt,
                source_block_id=block_id(source_id, page, idx),
                curation_status=m["CurationStatus"].DRAFT,
                proposed_by=PROPOSED_BY,
            )
            db.add(activity)
            db.flush()
            db.add(m["AcceptedAnswer"](activity_id=activity.id, answer_text=answer, is_primary=True))
            created["activities"] += 1

        def add_mc(prompt: str, correct: str, distractor_pool: list[str], source_id, page: int, idx: int) -> None:
            if db.query(m["Activity"]).filter_by(lesson_id=lesson.id, prompt=prompt).one_or_none() is not None:
                return
            distractors = rng.sample([d for d in distractor_pool if d != correct], k=min(3, len(distractor_pool) - 1))
            options = [(correct, True)] + [(d, False) for d in distractors]
            rng.shuffle(options)
            activity = m["Activity"](
                lesson_id=lesson.id,
                type=m["ActivityType"].MULTIPLE_CHOICE,
                prompt=prompt,
                source_block_id=block_id(source_id, page, idx),
                curation_status=m["CurationStatus"].DRAFT,
                proposed_by=PROPOSED_BY,
            )
            db.add(activity)
            db.flush()
            for text, is_correct in options:
                db.add(m["ActivityOption"](activity_id=activity.id, text=text, is_correct=is_correct))
            created["activities"] += 1

        # additional_activities p.8
        for prompt, correct, idx in AA_P8_NATIONALITY:
            add_mc(prompt, correct, COUNTRY_POOL, aa_source.id, 8, idx)

        # additional_activities p.9
        for prompt, word, idx in AA_P9_WHO_IS_THIS:
            add_fill_blank(prompt, echo_answer(word), aa_source.id, 9, idx)

        # additional_activities p.10
        for prompt, correct, kind, idx in AA_P10_PROFILE:
            pool = COUNTRY_POOL if kind == "country" else JOB_POOL
            add_mc(prompt, correct, pool, aa_source.id, 10, idx)

        # additional_activities p.11
        for prompt, correct, kind, idx in AA_P11_QUESTIONS:
            full_prompt = f"{AA_P11_PASSAGE} - {prompt}"
            pool = {"name": NAME_POOL, "country": COUNTRY_POOL, "job": JOB_POOL}[kind]
            add_mc(full_prompt, correct, pool, aa_source.id, 11, idx)

        # workbook p.28
        prompt, answer, idx = WB_P28_QA
        add_fill_blank(prompt, answer, wb_source.id, 28, idx)

        # workbook p.29
        for prompt, word, idx in WB_P29_CHOICE:
            correct = echo_answer(word).removeprefix(word)  # "이에요" or "예요"
            wrong = "예요" if correct == "이에요" else "이에요"
            add_mc(prompt, correct, [correct, wrong], wb_source.id, 29, idx)

        # workbook p.30
        prompt, answer, idx = WB_P30_QA
        add_fill_blank(prompt, answer, wb_source.id, 30, idx)

        # workbook p.32
        job_prompt = f"{WB_P32_PASSAGE} - {WB_P32_JOB_Q[0]}"
        add_mc(job_prompt, WB_P32_JOB_Q[1], JOB_POOL + ["한국어 선생님"], wb_source.id, 32, WB_P32_JOB_Q[2])

        tf_prompt = f"{WB_P32_PASSAGE} - 다음 문장이 맞으면 O, 틀리면 X: \"{WB_P32_STATEMENT}\""
        add_mc(tf_prompt, "X (틀려요)", ["O (맞아요)", "X (틀려요)"], wb_source.id, 32, WB_P32_GROUNDING_BLOCK)

        db.commit()
        return created
    finally:
        db.close()


if __name__ == "__main__":
    result = curate_unit1_wave5()
    print(f"Unit 1 curation draft (wave 5, workbook + additional_activities): {result}")
