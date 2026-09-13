import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.progress import Attempt, Mistake


def create_attempt(db: Session, **fields) -> Attempt:
    attempt = Attempt(**fields)
    db.add(attempt)
    db.flush()
    return attempt


def create_mistake(db: Session, **fields) -> Mistake:
    mistake = Mistake(**fields)
    db.add(mistake)
    db.flush()
    return mistake


def count_prior_attempts(db: Session, user_id: uuid.UUID, activity_id: uuid.UUID) -> int:
    return len(
        list(
            db.scalars(
                select(Attempt.id).where(Attempt.user_id == user_id, Attempt.activity_id == activity_id)
            )
        )
    )


def count_prior_vocab_attempts(
    db: Session, user_id: uuid.UUID, vocabulary_id: uuid.UUID, practice_mode
) -> int:
    return len(
        list(
            db.scalars(
                select(Attempt.id).where(
                    Attempt.user_id == user_id,
                    Attempt.vocabulary_id == vocabulary_id,
                    Attempt.practice_mode == practice_mode,
                )
            )
        )
    )


def list_attempts_for_user(db: Session, user_id: uuid.UUID) -> list[Attempt]:
    return list(db.scalars(select(Attempt).where(Attempt.user_id == user_id).order_by(Attempt.created_at.desc())))


def list_mistakes_for_user(db: Session, user_id: uuid.UUID) -> list[Mistake]:
    return list(db.scalars(select(Mistake).where(Mistake.user_id == user_id).order_by(Mistake.created_at.desc())))


def list_frequently_missed_vocabulary(db: Session, user_ids: list[uuid.UUID], limit: int = 10) -> list[tuple[uuid.UUID, int]]:
    """(vocabulary_id, miss_count) pairs, most-missed first, across the given users."""
    if not user_ids:
        return []
    rows = db.execute(
        select(Mistake.vocabulary_id, func.count(Mistake.id))
        .where(Mistake.user_id.in_(user_ids), Mistake.vocabulary_id.isnot(None))
        .group_by(Mistake.vocabulary_id)
        .order_by(func.count(Mistake.id).desc())
        .limit(limit)
    ).all()
    return [(r[0], r[1]) for r in rows]


def list_recently_practiced_vocabulary(db: Session, user_ids: list[uuid.UUID], limit: int = 10) -> list[uuid.UUID]:
    """Vocabulary ids most recently attempted (by last-attempt time), across the given users."""
    if not user_ids:
        return []
    rows = db.execute(
        select(Attempt.vocabulary_id, func.max(Attempt.created_at))
        .where(Attempt.user_id.in_(user_ids), Attempt.vocabulary_id.isnot(None))
        .group_by(Attempt.vocabulary_id)
        .order_by(func.max(Attempt.created_at).desc())
        .limit(limit)
    ).all()
    return [r[0] for r in rows]
