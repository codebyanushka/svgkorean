import uuid

from sqlalchemy import select
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


def list_attempts_for_user(db: Session, user_id: uuid.UUID) -> list[Attempt]:
    return list(db.scalars(select(Attempt).where(Attempt.user_id == user_id).order_by(Attempt.created_at.desc())))


def list_mistakes_for_user(db: Session, user_id: uuid.UUID) -> list[Mistake]:
    return list(db.scalars(select(Mistake).where(Mistake.user_id == user_id).order_by(Mistake.created_at.desc())))
