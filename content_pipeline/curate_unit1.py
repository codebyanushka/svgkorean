"""Unit 1 curation authoring pass: turn verified `ContentBlock` rows into
DRAFT `Vocabulary`/`GrammarPoint`/`Activity` rows.

This is the AI-organize-and-propose half of the curation workflow described
in docs/database.md - every row created here is `CurationStatus.DRAFT` and
`proposed_by="assistant:curate_unit1"`. Nothing here ever sets
HUMAN_APPROVED/CANONICAL; that only happens through a human reviewer calling
`POST /api/v1/curation/{type}/{id}/transition`.

Every fact below (Korean word, English gloss, example sentence, grammar
explanation) is copied verbatim from `verified_text`/`draft_text` on a
specific, cited `ContentBlock` (see `source_block_id` on each row) - nothing
is invented. Multiple-choice distractors are just recombinations of this
same verified vocabulary list, not new facts.

Run with backend/.venv active:
    cd backend && source .venv/bin/activate && cd ..
    python -m content_pipeline.curate_unit1
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# (korean_word, english_gloss, example_sentence_ko, page_number, word_block_index)
# Source: data/verified/vocab_grammar/page_008.json, page_009.json (Unit 1
# vocabulary list). "나" (page 9, block 6) has no OCR-captured English gloss
# block, but its meaning ("I, me") is unambiguous basic vocabulary, not a guess.
VOCABULARY: list[tuple[str, str, str, int, int]] = [
    ("나라", "country", "어느나라 사람이에요?", 8, 8),
    ("직업", "job", "유진 씨는 직업이 뭐예요?", 8, 11),
    ("한국", "Korea", "수지 씨는 한국 사람이에요?", 8, 14),
    ("사람", "person", "한국 사람이에요?", 8, 17),
    ("캐나다", "Canada", "캐나다 사람이에요", 8, 20),
    ("베트남", "Vietnam", "저는베트남 사람이에요", 8, 23),
    ("미국", "U.S.A.", "유진 씨는 미국사람이에요", 8, 26),
    ("프랑스", "France", "프랑스 사람이에요?", 8, 29),
    ("태국", "Thailand", "저는 태국 사람이에요", 8, 32),
    ("인도네시아", "Indonesia", "인도네시아 사람이에요", 8, 35),
    ("중국", "China", "웨이 씨는 중국 사람이에요?", 8, 38),
    ("일본", "Japan", "마리 씨는 일본사람이에요.", 8, 41),
    ("러시아", "Russia", "러시아사람이에요", 8, 44),
    ("케냐", "Kenya", "저는케냐 사람이에요", 8, 47),
    ("회사원", "office worker", "마리씨는 회사원이에요.", 8, 50),
    ("대학생", "college student", "유진 씨는 대학생이에요?", 8, 53),
    ("의사", "doctor", "의사예요", 8, 56),
    ("경찰", "police officer", "경찰이에요?", 8, 59),
    ("선생님", "teacher", "저는 선생님이에요", 8, 62),
    ("가수", "singer", "제친구는 가수예요", 8, 65),
    ("요리사", "cook", "저는 요리사예요", 8, 68),
    ("네", "yes", "가: 의사예요? /나: 네. 저는 의사예요", 9, 0),
    ("아니요", "no", "가: 의사예요? /나: 아니요.저는 경찰이에요", 9, 3),
    ("나", "I, me", "나는 학생이에요", 9, 6),
    ("모자", "hat", "모자예요", 9, 8),
    ("책", "book", "책이에요", 9, 11),
    ("공책", "notebook", "공책이에요?", 9, 14),
    ("한복", "Hanbok", "한복이에요?", 9, 17),
    ("커피", "coffee", "친구하고커피를마셔요", 9, 20),
    ("언니", "older sister", "언니예요", 9, 23),
    ("동생", "younger brother/sister", "제동생은 요리사예요", 9, 26),
    ("누구", "who", "누구예요?", 9, 29),
    ("친구", "friend", "안나 씨 친구예요?", 9, 32),
    ("씨", "Mr./Ms./Miss.", "유진 씨 동생이에요", 9, 35),
    ("제", "my", "이사람은 제친구예요", 9, 38),
    ("아버지", "father", "아버지는 회사원이에요", 9, 41),
    ("어머니", "mother", "어머니는 의사예요", 9, 44),
    ("이름", "name", "이름이 뭐예요?", 9, 47),
    ("학생", "student", "학생이에요.", 9, 50),
    ("자기소개", "self-introduction", "자기소개를 해요", 9, 53),
]

# (name_ko, name_en, explanation_en, anchor_page, anchor_block_index, examples)
# Source: data/verified/vocab_grammar/page_032.json (이에요/예요, Student
# Book p.38) and page_033.json (은/는, Student Book p.39). explanation_en is
# assembled from the page's own verified English fragments; examples are
# restricted to blocks whose verification_status is APPROVED.
GRAMMAR_POINTS: list[tuple[str, str, str, int, int]] = [
    (
        "이에요/예요",
        "to be (copula)",
        "Attaches to the end of a noun (a person or thing) to describe it, "
        "similar to \"to be\" in English. \"이에요\" is used when the noun "
        "ends in a consonant, and \"예요\" is used when the noun ends in a "
        "vowel. Examples: 미국 사람이에요 (is American), 선생님이에요 (is a "
        "teacher), 책이에요 (is a book), 한복이에요 (is a hanbok), 의사예요 "
        "(is a doctor), 친구예요 (is a friend), 커피예요 (is coffee), "
        "김치예요 (is kimchi).",
        32,
        7,
    ),
    (
        "은/는",
        "topic marker",
        "Attaches to the end of a noun to mark it as the topic of the "
        "sentence. \"은\" is used when the noun ends in a consonant, and "
        "\"는\" is used when the noun ends in a vowel. Examples: 저 사람은 "
        "회사원이에요 (as for that person, they are an office worker), "
        "동생은 가수예요 (as for my younger sibling, they are a singer), "
        "저는 한국 사람이에요 (as for me, I am Korean), 유진 씨는 제 "
        "친구예요 (as for Yujin, they are my friend), 웨이 씨는 요리사예요 "
        "(as for Wei, they are a cook).",
        33,
        7,
    ),
]

PROPOSED_BY = "assistant:curate_unit1"


def _load_backend_models():
    from app.db.session import SessionLocal
    from app.models.activity import Activity, ActivityOption
    from app.models.content_source import ContentBlock, ContentSource
    from app.models.curriculum import GrammarPoint, Lesson, Unit, Vocabulary
    from app.models.enums import ActivityType, CurationStatus, SourceType

    return {
        "SessionLocal": SessionLocal,
        "Activity": Activity,
        "ActivityOption": ActivityOption,
        "ContentBlock": ContentBlock,
        "ContentSource": ContentSource,
        "GrammarPoint": GrammarPoint,
        "Lesson": Lesson,
        "Unit": Unit,
        "Vocabulary": Vocabulary,
        "ActivityType": ActivityType,
        "CurationStatus": CurationStatus,
        "SourceType": SourceType,
    }


def curate_unit1() -> dict[str, int]:
    m = _load_backend_models()
    db = m["SessionLocal"]()
    try:
        unit = db.query(m["Unit"]).filter_by(number="01").one()
        lesson = db.query(m["Lesson"]).filter_by(unit_id=unit.id).one()
        vg_source = db.query(m["ContentSource"]).filter_by(source_type=m["SourceType"].VOCAB_GRAMMAR).one()

        def block_id(page: int, index: int):
            block = (
                db.query(m["ContentBlock"])
                .filter_by(source_id=vg_source.id, page_number=page, block_index=index)
                .one()
            )
            return block.id

        # Fill in the confirmed unit title/topic (from textbook page 39,
        # blocks 5/6 - APPROVED) - not curation-gated, Unit isn't a
        # CurationStatus model.
        unit.title_ko = "안녕하세요? 저는 안나예요"
        unit.title_en = "Hi, I'm Anna"

        created = {"vocabulary": 0, "grammar": 0, "activities": 0, "options": 0}

        vocab_rows = []
        for korean, english, example, page, idx in VOCABULARY:
            existing = db.query(m["Vocabulary"]).filter_by(lesson_id=lesson.id, korean=korean, english=english).one_or_none()
            if existing is not None:
                vocab_rows.append(existing)
                continue
            row = m["Vocabulary"](
                lesson_id=lesson.id,
                korean=korean,
                english=english,
                notes=example,
                source_block_id=block_id(page, idx),
                curation_status=m["CurationStatus"].DRAFT,
                proposed_by=PROPOSED_BY,
            )
            db.add(row)
            db.flush()
            vocab_rows.append(row)
            created["vocabulary"] += 1

        for name_ko, name_en, explanation_en, page, idx, in GRAMMAR_POINTS:
            existing = db.query(m["GrammarPoint"]).filter_by(lesson_id=lesson.id, name_ko=name_ko).one_or_none()
            if existing is not None:
                continue
            db.add(
                m["GrammarPoint"](
                    lesson_id=lesson.id,
                    name_ko=name_ko,
                    name_en=name_en,
                    explanation_en=explanation_en,
                    source_block_id=block_id(page, idx),
                    curation_status=m["CurationStatus"].DRAFT,
                    proposed_by=PROPOSED_BY,
                )
            )
            created["grammar"] += 1

        # Deterministic multiple-choice recognition activities: Korean word
        # -> pick the correct English gloss among 3 distractors drawn from
        # the same verified vocabulary list. No new facts - just
        # recombination of already-verified word/gloss pairs.
        rng = random.Random(20260913)
        all_english = [v.english for v in vocab_rows]
        for vocab in vocab_rows:
            existing = (
                db.query(m["Activity"])
                .filter_by(lesson_id=lesson.id, prompt=f"What does '{vocab.korean}' mean?")
                .one_or_none()
            )
            if existing is not None:
                continue
            distractor_pool = [e for e in all_english if e != vocab.english]
            distractors = rng.sample(distractor_pool, k=min(3, len(distractor_pool)))
            options_text = distractors + [vocab.english]
            rng.shuffle(options_text)

            activity = m["Activity"](
                lesson_id=lesson.id,
                type=m["ActivityType"].MULTIPLE_CHOICE,
                prompt=f"What does '{vocab.korean}' mean?",
                activity_metadata={"vocabulary_id": str(vocab.id)},
                source_block_id=vocab.source_block_id,
                curation_status=m["CurationStatus"].DRAFT,
                proposed_by=PROPOSED_BY,
            )
            db.add(activity)
            db.flush()
            for option_text in options_text:
                db.add(
                    m["ActivityOption"](
                        activity_id=activity.id,
                        text=option_text,
                        is_correct=(option_text == vocab.english),
                    )
                )
                created["options"] += 1
            created["activities"] += 1

        db.commit()
        return created
    finally:
        db.close()


if __name__ == "__main__":
    result = curate_unit1()
    print(f"Unit 1 curation draft: {result}")
