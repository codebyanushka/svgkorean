import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_student
from app.db.session import get_db
from app.models.user import User
from app.models.content_source import ContentBlock, ContentSource
from app.repositories import activity_repository, attempt_repository, curriculum_repository, progress_repository
from app.schemas.activity import ActivityOptionRead, ActivityRead
from app.schemas.curriculum import AudioAssetRead, GrammarPointRead, LessonDetailRead, UnitRead, VocabularyRead
from app.schemas.progress import (
    AttemptCreate,
    AttemptResult,
    GrammarProgressRead,
    ProgressRead,
    StreakRead,
    VocabularyProgressRead,
)
from app.services.grading_service import (
    NotAutoGradableError,
    grade_submission,
    resolve_grammar_point_id,
    resolve_mistake_category,
    resolve_practice_mode,
    resolve_vocabulary_id,
)

router = APIRouter(prefix="/student", tags=["student"], dependencies=[Depends(require_student)])


def _image_url(image_path: str | None) -> str | None:
    if image_path is None:
        return None
    return f"/media/images/{image_path.removeprefix('data/extracted/media/')}"


@router.get("/units", response_model=list[UnitRead])
def list_units(db: Session = Depends(get_db)) -> list[UnitRead]:
    # No lesson locking - all 10 units are always returned unlocked.
    return list(curriculum_repository.list_units(db))


@router.get("/units/{unit_number}/lessons", response_model=list[dict])
def list_unit_lessons(unit_number: str, db: Session = Depends(get_db)):
    unit = curriculum_repository.get_unit_by_number(db, unit_number)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    lessons = curriculum_repository.list_lessons_for_unit(db, unit.id)
    return [{"id": lesson.id, "unit_id": lesson.unit_id, "title": lesson.title} for lesson in lessons]


@router.get("/units/{unit_number}/audio", response_model=list[AudioAssetRead])
def list_unit_audio(unit_number: str, db: Session = Depends(get_db)) -> list[AudioAssetRead]:
    unit = curriculum_repository.get_unit_by_number(db, unit_number)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    assets = curriculum_repository.list_audio_for_unit(db, unit.id)
    return [
        AudioAssetRead(
            id=a.id,
            original_filename=a.original_filename,
            source_type=a.source_type,
            duration_seconds=a.duration_seconds,
            verification_status=a.verification_status,
            url=f"/media/audio/{a.file_path.removeprefix('data/raw/audio/')}",
        )
        for a in assets
    ]


@router.get("/lessons/{lesson_id}", response_model=LessonDetailRead)
def get_lesson_detail(lesson_id: uuid.UUID, db: Session = Depends(get_db)) -> LessonDetailRead:
    lesson = curriculum_repository.get_lesson(db, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    vocabulary = curriculum_repository.list_canonical_vocabulary(db, lesson.id)
    grammar_points = curriculum_repository.list_canonical_grammar(db, lesson.id)
    return LessonDetailRead(
        id=lesson.id,
        unit_id=lesson.unit_id,
        title=lesson.title,
        vocabulary=[
            VocabularyRead(
                id=v.id,
                korean=v.korean,
                english=v.english,
                part_of_speech=v.part_of_speech,
                notes=v.notes,
                image_url=_image_url(v.image_path),
            )
            for v in vocabulary
        ],
        grammar_points=[GrammarPointRead.model_validate(g) for g in grammar_points],
    )


@router.get("/lessons/{lesson_id}/activities", response_model=list[ActivityRead])
def list_lesson_activities(lesson_id: uuid.UUID, db: Session = Depends(get_db)) -> list[ActivityRead]:
    activities = activity_repository.list_canonical_activities(db, lesson_id)

    block_ids = [a.source_block_id for a in activities if a.source_block_id is not None]
    source_by_block: dict[uuid.UUID, str] = {}
    if block_ids:
        rows = (
            db.query(ContentBlock.id, ContentSource.source_type)
            .join(ContentSource, ContentBlock.source_id == ContentSource.id)
            .filter(ContentBlock.id.in_(block_ids))
            .all()
        )
        source_by_block = {block_id: source_type.value for block_id, source_type in rows}

    return [
        ActivityRead(
            id=a.id,
            lesson_id=a.lesson_id,
            type=a.type,
            prompt=a.prompt,
            metadata=a.activity_metadata,
            options=[ActivityOptionRead(id=o.id, text=o.text) for o in a.options],
            image_url=_image_url(a.image_path),
            source=source_by_block.get(a.source_block_id) if a.source_block_id else None,
        )
        for a in activities
    ]


@router.post("/attempts", response_model=AttemptResult)
def submit_attempt(
    payload: AttemptCreate, db: Session = Depends(get_db), current_user: User = Depends(require_student)
) -> AttemptResult:
    activity = activity_repository.get_canonical_activity(db, payload.activity_id)
    if activity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    try:
        is_correct = grade_submission(activity, payload.submitted_answer)
    except NotAutoGradableError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="This activity type cannot be auto-graded yet",
        )

    prior_attempts = attempt_repository.count_prior_attempts(db, current_user.id, activity.id)
    attempt = attempt_repository.create_attempt(
        user_id=current_user.id,
        activity_id=activity.id,
        lesson_id=activity.lesson_id,
        vocabulary_id=resolve_vocabulary_id(activity),
        grammar_point_id=resolve_grammar_point_id(activity),
        practice_mode=resolve_practice_mode(activity),
        submitted_answer=payload.submitted_answer,
        normalized_answer=payload.submitted_answer.strip().lower(),
        is_correct=is_correct,
        score=1.0 if is_correct else 0.0,
        hints_used=payload.hints_used,
        attempt_number=prior_attempts + 1,
        response_time_ms=payload.response_time_ms,
        db=db,
    )

    if not is_correct:
        attempt_repository.create_mistake(
            db=db,
            attempt_id=attempt.id,
            user_id=current_user.id,
            category=resolve_mistake_category(activity),
            vocabulary_id=resolve_vocabulary_id(activity),
            grammar_point_id=resolve_grammar_point_id(activity),
        )

    vocabulary_id = resolve_vocabulary_id(activity)
    practice_mode = resolve_practice_mode(activity)
    if vocabulary_id is not None and practice_mode is not None:
        vocab_progress = progress_repository.get_or_create_vocabulary_progress(
            db, current_user.id, vocabulary_id, practice_mode
        )
        progress_repository.record_mastery_result(vocab_progress, is_correct)

    grammar_point_id = resolve_grammar_point_id(activity)
    if grammar_point_id is not None:
        grammar_progress = progress_repository.get_or_create_grammar_progress(db, current_user.id, grammar_point_id)
        progress_repository.record_mastery_result(grammar_progress, is_correct)

    progress_repository.get_or_create_progress(db, current_user.id, activity.lesson_id)
    streak = progress_repository.get_or_create_streak(db, current_user.id)
    progress_repository.record_activity_today(streak)

    db.commit()

    return AttemptResult(
        attempt_id=attempt.id, is_correct=is_correct, score=attempt.score, attempt_number=attempt.attempt_number
    )


@router.get("/progress", response_model=list[ProgressRead])
def get_progress(db: Session = Depends(get_db), current_user: User = Depends(require_student)) -> list[ProgressRead]:
    return list(progress_repository.list_progress_for_user(db, current_user.id))


@router.get("/progress/vocabulary", response_model=list[VocabularyProgressRead])
def get_vocabulary_progress(
    db: Session = Depends(get_db), current_user: User = Depends(require_student)
) -> list[VocabularyProgressRead]:
    return list(progress_repository.list_vocabulary_progress_for_user(db, current_user.id))


@router.get("/progress/grammar", response_model=list[GrammarProgressRead])
def get_grammar_progress(
    db: Session = Depends(get_db), current_user: User = Depends(require_student)
) -> list[GrammarProgressRead]:
    return list(progress_repository.list_grammar_progress_for_user(db, current_user.id))


@router.get("/progress/streak", response_model=StreakRead)
def get_streak(db: Session = Depends(get_db), current_user: User = Depends(require_student)) -> StreakRead:
    return progress_repository.get_or_create_streak(db, current_user.id)
