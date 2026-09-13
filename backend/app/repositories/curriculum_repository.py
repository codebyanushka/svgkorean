import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.curriculum import GrammarPoint, Lesson, Unit, Vocabulary
from app.models.enums import CurationStatus


def list_units(db: Session) -> list[Unit]:
    return list(db.scalars(select(Unit).order_by(Unit.number)))


def get_unit_by_number(db: Session, number: str) -> Unit | None:
    return db.scalars(select(Unit).where(Unit.number == number)).one_or_none()


def list_lessons_for_unit(db: Session, unit_id: uuid.UUID) -> list[Lesson]:
    return list(db.scalars(select(Lesson).where(Lesson.unit_id == unit_id).order_by(Lesson.created_at)))


def get_lesson(db: Session, lesson_id: uuid.UUID) -> Lesson | None:
    return db.get(Lesson, lesson_id)


def list_canonical_vocabulary(db: Session, lesson_id: uuid.UUID) -> list[Vocabulary]:
    return list(
        db.scalars(
            select(Vocabulary).where(
                Vocabulary.lesson_id == lesson_id,
                Vocabulary.curation_status == CurationStatus.CANONICAL,
            )
        )
    )


def list_canonical_grammar(db: Session, lesson_id: uuid.UUID) -> list[GrammarPoint]:
    return list(
        db.scalars(
            select(GrammarPoint).where(
                GrammarPoint.lesson_id == lesson_id,
                GrammarPoint.curation_status == CurationStatus.CANONICAL,
            )
        )
    )
