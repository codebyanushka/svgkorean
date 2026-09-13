"""Vocabulary Memory Lab: question generation, lenient answer grading, and
mastery-tracking for the vocabulary Learn/Recall/Apply/Smart-Revision flows.

Reuses the existing `VocabularyProgress`/`Attempt`/`Mistake`/`Streak` schema
and `progress_repository.record_mastery_result` mastery math unchanged -
this module only adds question generation + grading on top, it does not
introduce a parallel progress-tracking system.

Every question is generated from real `CurationStatus.CANONICAL` Vocabulary
rows only - nothing here invents a word, meaning, or example sentence.
"""

from __future__ import annotations

import random
import re
import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.curriculum import Vocabulary
from app.models.enums import MasteryStatus, MistakeCategory, PracticeMode
from app.models.progress import VocabularyProgress
from app.repositories import attempt_repository, progress_repository

QUESTION_TYPES = (
    "ko_to_en_written",
    "en_to_ko_written",
    "multiple_choice",
    "context_to_word",
)

_QUESTION_TYPE_TO_PRACTICE_MODE: dict[str, PracticeMode] = {
    "ko_to_en_written": PracticeMode.RECALL_KO_TO_EN,
    "en_to_ko_written": PracticeMode.RECALL_EN_TO_KO,
    "multiple_choice": PracticeMode.RECOGNITION,
    "context_to_word": PracticeMode.CONTEXT,
}

_MISTAKE_CATEGORY_BY_QUESTION_TYPE: dict[str, MistakeCategory] = {
    "ko_to_en_written": MistakeCategory.VOCABULARY_RECALL,
    "en_to_ko_written": MistakeCategory.SPELLING,
    "multiple_choice": MistakeCategory.RECOGNITION,
    "context_to_word": MistakeCategory.COMPREHENSION,
}


@dataclass
class WordMastery:
    vocabulary: Vocabulary
    attempt_count: int = 0
    correct_count: int = 0
    mastery_score: float = 0.0
    status: str = "NOT_STARTED"
    last_attempt_at: datetime | None = None


@dataclass
class UnitVocabStats:
    unit_number: str
    title_ko: str | None
    title_en: str | None
    word_count: int
    mastered_count: int
    learning_count: int
    needs_review_count: int


def _word_mastery_map(vocabulary: list[Vocabulary], progress_rows: list[VocabularyProgress]) -> dict[uuid.UUID, WordMastery]:
    by_word: dict[uuid.UUID, list[VocabularyProgress]] = {}
    for row in progress_rows:
        by_word.setdefault(row.vocabulary_id, []).append(row)

    result: dict[uuid.UUID, WordMastery] = {}
    for word in vocabulary:
        rows = by_word.get(word.id, [])
        attempt_count = sum(r.attempt_count for r in rows)
        correct_count = sum(r.correct_count for r in rows)
        last_attempt_at = max((r.last_attempt_at for r in rows if r.last_attempt_at), default=None)
        if attempt_count == 0:
            status = "NEEDS_REVIEW"  # never attempted - counted with needs-review for the overview buckets
            mastery_score = 0.0
        else:
            mastery_score = correct_count / attempt_count
            if attempt_count >= 3 and mastery_score >= 0.8:
                status = MasteryStatus.MASTERED.value
            elif mastery_score < 0.5:
                status = "NEEDS_REVIEW"
            else:
                status = MasteryStatus.LEARNING.value
        result[word.id] = WordMastery(
            vocabulary=word,
            attempt_count=attempt_count,
            correct_count=correct_count,
            mastery_score=mastery_score,
            status=status,
            last_attempt_at=last_attempt_at,
        )
    return result


def word_mastery_for_words(db: Session, user_id: uuid.UUID, vocabulary: list[Vocabulary]) -> dict[uuid.UUID, WordMastery]:
    progress_rows = progress_repository.list_vocabulary_progress_for_words(db, user_id, [v.id for v in vocabulary])
    return _word_mastery_map(vocabulary, progress_rows)


def unit_stats(db: Session, user_id: uuid.UUID, unit, vocabulary: list[Vocabulary]) -> UnitVocabStats:
    mastery = word_mastery_for_words(db, user_id, vocabulary)
    mastered = sum(1 for m in mastery.values() if m.status == MasteryStatus.MASTERED.value)
    learning = sum(1 for m in mastery.values() if m.status == MasteryStatus.LEARNING.value)
    needs_review = len(vocabulary) - mastered - learning
    return UnitVocabStats(
        unit_number=unit.number,
        title_ko=unit.title_ko,
        title_en=unit.title_en,
        word_count=len(vocabulary),
        mastered_count=mastered,
        learning_count=learning,
        needs_review_count=needs_review,
    )


def _normalize(text: str, *, korean: bool) -> str:
    text = text.strip()
    if korean:
        text = re.sub(r"\s+", "", text)
    else:
        text = text.lower()
        text = re.sub(r"[.,!?]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
    return text


def _acceptable_answers(raw: str, *, korean: bool) -> set[str]:
    parts = re.split(r"[/,]", raw)
    return {_normalize(p, korean=korean) for p in parts if p.strip()}


def generate_questions(vocabulary: list[Vocabulary], *, count: int, seed: int, only_types: list[str] | None = None) -> list[dict]:
    """Build a shuffled batch of recall/apply questions from real canonical
    vocabulary. Image/context question types are only generated for words
    that actually have a verified image/example - never fabricated."""
    rng = random.Random(seed)
    allowed_types = only_types or list(QUESTION_TYPES)
    all_english = [v.english for v in vocabulary]
    all_korean = [v.korean for v in vocabulary]

    candidates: list[dict] = []
    for word in vocabulary:
        if "ko_to_en_written" in allowed_types:
            candidates.append({"vocabulary_id": str(word.id), "question_type": "ko_to_en_written", "prompt": word.korean, "options": None, "image_url": None})
        if "en_to_ko_written" in allowed_types:
            candidates.append({"vocabulary_id": str(word.id), "question_type": "en_to_ko_written", "prompt": word.english, "options": None, "image_url": None})
        if "multiple_choice" in allowed_types:
            distractor_pool = [e for e in all_english if e != word.english]
            if len(distractor_pool) >= 1:
                distractors = rng.sample(distractor_pool, k=min(3, len(distractor_pool)))
                options = [word.english] + distractors
                rng.shuffle(options)
                candidates.append(
                    {
                        "vocabulary_id": str(word.id),
                        "question_type": "multiple_choice",
                        "prompt": word.korean,
                        "options": options,
                        "image_url": None,
                    }
                )
        if "context_to_word" in allowed_types and word.notes and word.korean in word.notes:
            distractor_pool = [k for k in all_korean if k != word.korean]
            if len(distractor_pool) >= 1:
                distractors = rng.sample(distractor_pool, k=min(3, len(distractor_pool)))
                options = [word.korean] + distractors
                rng.shuffle(options)
                blanked = word.notes.replace(word.korean, "ـ_____ـ", 1)
                candidates.append(
                    {
                        "vocabulary_id": str(word.id),
                        "question_type": "context_to_word",
                        "prompt": blanked,
                        "options": options,
                        "image_url": None,
                    }
                )

    rng.shuffle(candidates)
    return candidates[:count] if count else candidates


def grade_answer(word: Vocabulary, question_type: str, submitted_answer: str) -> bool:
    submitted = submitted_answer.strip()
    if question_type == "ko_to_en_written":
        accepted = _acceptable_answers(word.english, korean=False)
        return _normalize(submitted, korean=False) in accepted
    if question_type == "multiple_choice":
        return _normalize(submitted, korean=False) in _acceptable_answers(word.english, korean=False)
    if question_type in ("en_to_ko_written", "context_to_word"):
        return _normalize(submitted, korean=True) == _normalize(word.korean, korean=True)
    return False


def record_attempt(
    db: Session, user_id: uuid.UUID, word: Vocabulary, question_type: str, submitted_answer: str, ui_mode: str | None = None
) -> dict:
    is_correct = grade_answer(word, question_type, submitted_answer)
    practice_mode = _QUESTION_TYPE_TO_PRACTICE_MODE[question_type]

    prior = attempt_repository.count_prior_vocab_attempts(db, user_id, word.id, practice_mode)
    attempt = attempt_repository.create_attempt(
        db=db,
        user_id=user_id,
        activity_id=None,
        lesson_id=word.lesson_id,
        vocabulary_id=word.id,
        practice_mode=practice_mode,
        ui_mode=ui_mode,
        submitted_answer=submitted_answer,
        normalized_answer=_normalize(submitted_answer, korean=question_type != "ko_to_en_written"),
        is_correct=is_correct,
        score=1.0 if is_correct else 0.0,
        attempt_number=prior + 1,
    )
    if not is_correct:
        attempt_repository.create_mistake(
            db=db,
            attempt_id=attempt.id,
            user_id=user_id,
            category=_MISTAKE_CATEGORY_BY_QUESTION_TYPE[question_type],
            vocabulary_id=word.id,
            grammar_point_id=None,
        )

    vocab_progress = progress_repository.get_or_create_vocabulary_progress(db, user_id, word.id, practice_mode)
    progress_repository.record_mastery_result(vocab_progress, is_correct)
    streak = progress_repository.get_or_create_streak(db, user_id)
    progress_repository.record_activity_today(streak)
    db.commit()

    correct_answer = word.korean if question_type in ("en_to_ko_written", "context_to_word") else word.english
    return {"is_correct": is_correct, "correct_answer": correct_answer}


_RATING_TO_CORRECT = {"again": False, "hard": True, "good": True, "easy": True}


def record_flashcard_review(db: Session, user_id: uuid.UUID, word: Vocabulary, rating: str) -> dict:
    if rating not in _RATING_TO_CORRECT:
        raise ValueError(f"Unknown flashcard rating '{rating}'")
    is_correct = _RATING_TO_CORRECT[rating]
    practice_mode = PracticeMode.RECOGNITION

    prior = attempt_repository.count_prior_vocab_attempts(db, user_id, word.id, practice_mode)
    attempt = attempt_repository.create_attempt(
        db=db,
        user_id=user_id,
        activity_id=None,
        lesson_id=word.lesson_id,
        vocabulary_id=word.id,
        practice_mode=practice_mode,
        ui_mode="flashcards",
        submitted_answer=rating,
        normalized_answer=rating,
        is_correct=is_correct,
        score=1.0 if is_correct else 0.0,
        attempt_number=prior + 1,
    )
    if not is_correct:
        attempt_repository.create_mistake(
            db=db,
            attempt_id=attempt.id,
            user_id=user_id,
            category=MistakeCategory.RECOGNITION,
            vocabulary_id=word.id,
            grammar_point_id=None,
        )
    vocab_progress = progress_repository.get_or_create_vocabulary_progress(db, user_id, word.id, practice_mode)
    progress_repository.record_mastery_result(vocab_progress, is_correct)
    streak = progress_repository.get_or_create_streak(db, user_id)
    progress_repository.record_activity_today(streak)
    db.commit()
    return {"status": vocab_progress.status.value, "mastery_score": vocab_progress.mastery_score}


def sort_by_priority(vocabulary: list[Vocabulary], mastery: dict[uuid.UUID, WordMastery]) -> list[Vocabulary]:
    """Weakest/least-recently-seen words first - the "smart revision" order."""

    def key(word: Vocabulary):
        m = mastery.get(word.id)
        if m is None:
            return (0.0, 0)
        return (m.mastery_score, m.attempt_count)

    return sorted(vocabulary, key=key)
