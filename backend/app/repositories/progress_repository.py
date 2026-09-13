import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import MasteryStatus, PracticeMode
from app.models.progress import GrammarProgress, Progress, Streak, VocabularyProgress


def get_or_create_progress(db: Session, user_id: uuid.UUID, lesson_id: uuid.UUID) -> Progress:
    row = db.scalars(
        select(Progress).where(Progress.user_id == user_id, Progress.lesson_id == lesson_id)
    ).one_or_none()
    if row is None:
        row = Progress(user_id=user_id, lesson_id=lesson_id)
        db.add(row)
        db.flush()
    return row


def list_progress_for_user(db: Session, user_id: uuid.UUID) -> list[Progress]:
    return list(db.scalars(select(Progress).where(Progress.user_id == user_id)))


def get_or_create_vocabulary_progress(
    db: Session, user_id: uuid.UUID, vocabulary_id: uuid.UUID, practice_mode: PracticeMode
) -> VocabularyProgress:
    row = db.scalars(
        select(VocabularyProgress).where(
            VocabularyProgress.user_id == user_id,
            VocabularyProgress.vocabulary_id == vocabulary_id,
            VocabularyProgress.practice_mode == practice_mode,
        )
    ).one_or_none()
    if row is None:
        row = VocabularyProgress(user_id=user_id, vocabulary_id=vocabulary_id, practice_mode=practice_mode)
        db.add(row)
        db.flush()
    return row


def get_or_create_grammar_progress(db: Session, user_id: uuid.UUID, grammar_point_id: uuid.UUID) -> GrammarProgress:
    row = db.scalars(
        select(GrammarProgress).where(
            GrammarProgress.user_id == user_id, GrammarProgress.grammar_point_id == grammar_point_id
        )
    ).one_or_none()
    if row is None:
        row = GrammarProgress(user_id=user_id, grammar_point_id=grammar_point_id)
        db.add(row)
        db.flush()
    return row


def list_vocabulary_progress_for_user(db: Session, user_id: uuid.UUID) -> list[VocabularyProgress]:
    return list(db.scalars(select(VocabularyProgress).where(VocabularyProgress.user_id == user_id)))


def list_grammar_progress_for_user(db: Session, user_id: uuid.UUID) -> list[GrammarProgress]:
    return list(db.scalars(select(GrammarProgress).where(GrammarProgress.user_id == user_id)))


def record_mastery_result(row: VocabularyProgress | GrammarProgress, is_correct: bool) -> None:
    """Bumps counters/mastery_score/status/last_attempt_at from one graded attempt.

    Baseline heuristic - running-average score with simple mastery
    thresholds; a smarter spaced-repetition model can replace this later
    without changing the schema or API surface.
    """
    row.attempt_count += 1
    if is_correct:
        row.correct_count += 1
    row.mastery_score = row.correct_count / row.attempt_count
    if row.attempt_count >= 3 and row.mastery_score >= 0.8:
        row.status = MasteryStatus.MASTERED
    elif row.mastery_score < 0.5:
        row.status = MasteryStatus.NEEDS_REVIEW
    else:
        row.status = MasteryStatus.LEARNING
    row.last_attempt_at = datetime.now(timezone.utc)


def get_or_create_streak(db: Session, user_id: uuid.UUID) -> Streak:
    row = db.scalars(select(Streak).where(Streak.user_id == user_id)).one_or_none()
    if row is None:
        row = Streak(user_id=user_id)
        db.add(row)
        db.flush()
    return row


def record_activity_today(streak: Streak) -> None:
    today = datetime.now(timezone.utc).date()
    if streak.last_active_date == today:
        return
    if streak.last_active_date is not None and (today - streak.last_active_date).days == 1:
        streak.current_streak_days += 1
    else:
        streak.current_streak_days = 1
    streak.longest_streak_days = max(streak.longest_streak_days, streak.current_streak_days)
    streak.last_active_date = today
