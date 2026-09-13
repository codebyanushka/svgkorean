"""Vocabulary Memory Lab: Learn (flashcards) / Recall / Apply / Smart
Revision endpoints, built on top of the existing canonical Vocabulary +
VocabularyProgress data - see app/services/vocab_lab_service.py."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_student
from app.db.session import get_db
from app.models.enums import CurationStatus
from app.models.user import User
from app.repositories import curriculum_repository
from app.schemas.vocab_lab import (
    FlashcardReviewRequest,
    FlashcardReviewResult,
    NewVocabularyItemRead,
    UnitVocabStatsRead,
    VocabAttemptRequest,
    VocabAttemptResult,
    VocabQuestionRead,
    VocabSearchResultRead,
    VocabWordRead,
)
from app.services import vocab_lab_service

router = APIRouter(prefix="/student/vocab-lab", tags=["vocab-lab"], dependencies=[Depends(require_student)])


def _image_url(image_path: str | None) -> str | None:
    if image_path is None:
        return None
    return f"/media/images/{image_path.removeprefix('data/extracted/media/')}"


def _is_teacher_added(proposed_by: str | None) -> bool:
    return bool(proposed_by and proposed_by.startswith("teacher:"))


def _unit_vocabulary(db: Session, unit_number: str):
    unit = curriculum_repository.get_unit_by_number(db, unit_number)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    lessons = curriculum_repository.list_lessons_for_unit(db, unit.id)
    vocabulary = []
    for lesson in lessons:
        vocabulary.extend(curriculum_repository.list_canonical_vocabulary(db, lesson.id))
    return unit, vocabulary


@router.get("/units-overview", response_model=list[UnitVocabStatsRead])
def units_overview(
    db: Session = Depends(get_db), current_user: User = Depends(require_student)
) -> list[UnitVocabStatsRead]:
    units = curriculum_repository.list_units(db)
    results = []
    for unit in units:
        lessons = curriculum_repository.list_lessons_for_unit(db, unit.id)
        vocabulary = []
        for lesson in lessons:
            vocabulary.extend(curriculum_repository.list_canonical_vocabulary(db, lesson.id))
        if not vocabulary:
            continue
        stats = vocab_lab_service.unit_stats(db, current_user.id, unit, vocabulary)
        results.append(
            UnitVocabStatsRead(
                unit_id=unit.id,
                unit_number=stats.unit_number,
                title_ko=stats.title_ko,
                title_en=stats.title_en,
                word_count=stats.word_count,
                mastered_count=stats.mastered_count,
                learning_count=stats.learning_count,
                needs_review_count=stats.needs_review_count,
            )
        )
    return results


@router.get("/units/{unit_number}/words", response_model=list[VocabWordRead])
def unit_words(
    unit_number: str, db: Session = Depends(get_db), current_user: User = Depends(require_student)
) -> list[VocabWordRead]:
    _, vocabulary = _unit_vocabulary(db, unit_number)
    mastery = vocab_lab_service.word_mastery_for_words(db, current_user.id, vocabulary)
    return [
        VocabWordRead(
            id=word.id,
            korean=word.korean,
            english=word.english,
            romanization=word.romanization,
            notes=word.notes,
            image_url=_image_url(word.image_path),
            attempt_count=mastery[word.id].attempt_count,
            correct_count=mastery[word.id].correct_count,
            mastery_score=mastery[word.id].mastery_score,
            status=mastery[word.id].status,
            last_attempt_at=mastery[word.id].last_attempt_at.isoformat() if mastery[word.id].last_attempt_at else None,
            is_teacher_added=_is_teacher_added(word.proposed_by),
        )
        for word in vocabulary
    ]


@router.get("/search", response_model=list[VocabSearchResultRead])
def search_vocabulary(
    q: str = Query(min_length=1), db: Session = Depends(get_db), current_user: User = Depends(require_student)
) -> list[VocabSearchResultRead]:
    results = curriculum_repository.search_canonical_vocabulary(db, q)
    return [
        VocabSearchResultRead(
            id=word.id,
            korean=word.korean,
            english=word.english,
            romanization=word.romanization,
            notes=word.notes,
            image_url=_image_url(word.image_path),
            unit_number=word.lesson.unit.number,
            unit_title_ko=word.lesson.unit.title_ko,
            is_teacher_added=_is_teacher_added(word.proposed_by),
        )
        for word in results
    ]


@router.get("/new-vocabulary", response_model=list[NewVocabularyItemRead])
def new_vocabulary(
    db: Session = Depends(get_db), current_user: User = Depends(require_student)
) -> list[NewVocabularyItemRead]:
    """Recently-published words added by a teacher (not the AI content
    pipeline) - powers the dashboard's "New Vocabulary" box."""
    results = curriculum_repository.list_recent_published_teacher_vocabulary(db)
    return [
        NewVocabularyItemRead(
            id=word.id,
            korean=word.korean,
            english=word.english,
            romanization=word.romanization,
            notes=word.notes,
            image_url=_image_url(word.image_path),
            unit_number=word.lesson.unit.number,
            unit_title_ko=word.lesson.unit.title_ko,
        )
        for word in results
    ]


@router.post("/words/{vocabulary_id}/flashcard-review", response_model=FlashcardReviewResult)
def flashcard_review(
    vocabulary_id: uuid.UUID,
    payload: FlashcardReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student),
) -> FlashcardReviewResult:
    word = curriculum_repository.get_vocabulary(db, vocabulary_id)
    if word is None or word.curation_status != CurationStatus.CANONICAL:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vocabulary not found")
    try:
        result = vocab_lab_service.record_flashcard_review(db, current_user.id, word, payload.rating)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return FlashcardReviewResult(**result)



@router.get("/units/{unit_number}/session", response_model=list[VocabQuestionRead])
def recall_session(
    unit_number: str,
    mode: str = Query(default="recall", pattern="^(recall|apply|quick)$"),
    count: int = Query(default=10, ge=1, le=50),
    types: str | None = Query(default=None, description="Optional comma-separated question_type override"),
    seed: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student),
) -> list[VocabQuestionRead]:
    _, vocabulary = _unit_vocabulary(db, unit_number)
    if not vocabulary:
        return []
    if types:
        only_types = [t.strip() for t in types.split(",") if t.strip()]
    else:
        only_types = ["context_to_word"] if mode == "apply" else None
    import random as _random

    questions = vocab_lab_service.generate_questions(
        vocabulary, count=count, seed=seed if seed is not None else _random.randint(0, 1_000_000), only_types=only_types
    )
    return [VocabQuestionRead(**q) for q in questions]


@router.get("/units/{unit_number}/smart-revision", response_model=list[VocabQuestionRead])
def smart_revision(
    unit_number: str,
    count: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student),
) -> list[VocabQuestionRead]:
    _, vocabulary = _unit_vocabulary(db, unit_number)
    if not vocabulary:
        return []
    mastery = vocab_lab_service.word_mastery_for_words(db, current_user.id, vocabulary)
    priority_words = vocab_lab_service.sort_by_priority(vocabulary, mastery)[:count]
    questions = vocab_lab_service.generate_questions(priority_words, count=count, seed=42)
    return [VocabQuestionRead(**q) for q in questions]


@router.post("/words/{vocabulary_id}/attempt", response_model=VocabAttemptResult)
def submit_vocab_attempt(
    vocabulary_id: uuid.UUID,
    payload: VocabAttemptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student),
) -> VocabAttemptResult:
    word = curriculum_repository.get_vocabulary(db, vocabulary_id)
    if word is None or word.curation_status != CurationStatus.CANONICAL:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vocabulary not found")
    if payload.question_type not in vocab_lab_service.QUESTION_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown question type")
    result = vocab_lab_service.record_attempt(
        db, current_user.id, word, payload.question_type, payload.submitted_answer, payload.ui_mode
    )
    return VocabAttemptResult(**result)
