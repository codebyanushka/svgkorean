import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audio import AudioAsset
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


def get_unit(db: Session, unit_id: uuid.UUID) -> Unit | None:
    return db.get(Unit, unit_id)


def create_unit(db: Session, title_ko: str, title_en: str | None, first_lesson_title: str | None = None) -> Unit:
    existing_numbers = db.scalars(select(Unit.number)).all()
    numeric = [int(n) for n in existing_numbers if n.isdigit()]
    next_number = f"{(max(numeric) + 1) if numeric else 1:02d}"
    unit = Unit(number=next_number, title_ko=title_ko, title_en=title_en)
    db.add(unit)
    db.flush()
    lesson = Lesson(unit_id=unit.id, title=first_lesson_title or title_ko)
    db.add(lesson)
    db.flush()
    return unit


def create_lesson(db: Session, unit_id: uuid.UUID, title: str) -> Lesson:
    lesson = Lesson(unit_id=unit_id, title=title)
    db.add(lesson)
    db.flush()
    return lesson


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


def list_audio_for_unit(db: Session, unit_id: uuid.UUID) -> list[AudioAsset]:
    return list(
        db.scalars(
            select(AudioAsset).where(AudioAsset.unit_id == unit_id).order_by(AudioAsset.source_type, AudioAsset.original_filename)
        )
    )


def get_vocabulary(db: Session, vocabulary_id: uuid.UUID) -> Vocabulary | None:
    return db.get(Vocabulary, vocabulary_id)


def list_all_vocabulary_for_unit(db: Session, unit_id: uuid.UUID) -> list[Vocabulary]:
    """Any curation_status - for teacher management, not student reads."""
    lesson_ids = db.scalars(select(Lesson.id).where(Lesson.unit_id == unit_id)).all()
    if not lesson_ids:
        return []
    return list(db.scalars(select(Vocabulary).where(Vocabulary.lesson_id.in_(lesson_ids)).order_by(Vocabulary.created_at)))


def create_vocabulary(db: Session, **fields) -> Vocabulary:
    row = Vocabulary(**fields)
    db.add(row)
    db.flush()
    return row


def _is_korean_query(query: str) -> bool:
    """Hangul syllables/jamo anywhere in the query -> treat as a Korean-word
    search; otherwise (Latin/English characters) -> an English-meaning
    search. Never mixes both fields in one query - see search_canonical_vocabulary."""
    for ch in query:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3 or 0x1100 <= code <= 0x11FF or 0x3130 <= code <= 0x318F:
            return True
    return False


def search_canonical_vocabulary(db: Session, query: str, limit: int = 30) -> list[Vocabulary]:
    """Language-aware search: a Korean-script query only matches `korean`, a
    Latin/English query only matches `english`. Never matches `romanization`
    (display-only field) and never cross-matches the other language's field."""
    like = f"%{query}%"
    field = Vocabulary.korean if _is_korean_query(query) else Vocabulary.english
    return list(
        db.scalars(
            select(Vocabulary)
            .where(
                Vocabulary.curation_status == CurationStatus.CANONICAL,
                field.ilike(like),
            )
            .limit(limit)
        )
    )


def get_vocabulary_by_ids(db: Session, vocabulary_ids: list[uuid.UUID]) -> list[Vocabulary]:
    if not vocabulary_ids:
        return []
    return list(db.scalars(select(Vocabulary).where(Vocabulary.id.in_(vocabulary_ids))))


def count_teacher_added_vocabulary(db: Session) -> int:
    return len(list(db.scalars(select(Vocabulary.id).where(Vocabulary.proposed_by.ilike("teacher:%")))))


def list_teacher_added_vocabulary(db: Session, limit: int = 20) -> list[Vocabulary]:
    return list(
        db.scalars(
            select(Vocabulary)
            .where(Vocabulary.proposed_by.ilike("teacher:%"))
            .order_by(Vocabulary.created_at.desc())
            .limit(limit)
        )
    )


def list_recent_published_teacher_vocabulary(db: Session, limit: int = 10) -> list[Vocabulary]:
    """Teacher-added words a student may actually see (CANONICAL only),
    newest-published first - powers the "New Vocabulary from your teacher"
    dashboard box."""
    return list(
        db.scalars(
            select(Vocabulary)
            .where(
                Vocabulary.curation_status == CurationStatus.CANONICAL,
                Vocabulary.proposed_by.ilike("teacher:%"),
            )
            .order_by(Vocabulary.reviewed_at.desc().nullslast(), Vocabulary.created_at.desc())
            .limit(limit)
        )
    )
