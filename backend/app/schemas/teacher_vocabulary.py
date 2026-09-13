import uuid

from pydantic import BaseModel

from app.models.enums import CurationStatus


class VocabularyManageRead(BaseModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    korean: str
    english: str
    romanization: str | None
    part_of_speech: str | None
    notes: str | None
    image_url: str | None
    curation_status: CurationStatus


class VocabularyCreateRequest(BaseModel):
    unit_number: str
    korean: str
    english: str
    romanization: str | None = None
    part_of_speech: str | None = None
    notes: str | None = None
    lesson_id: uuid.UUID | None = None


class VocabularyUpdateRequest(BaseModel):
    korean: str | None = None
    english: str | None = None
    romanization: str | None = None
    part_of_speech: str | None = None
    notes: str | None = None


class StudentVocabInsights(BaseModel):
    mastery_pct: float
    words_tracked: int
    weak_words: list[str]
    mastered_words: list[str]
    recent_attempt_count: int
