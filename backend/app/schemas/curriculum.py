import uuid

from pydantic import BaseModel


class UnitRead(BaseModel):
    id: uuid.UUID
    number: str
    title_ko: str | None
    title_en: str | None

    model_config = {"from_attributes": True}


class LessonRead(BaseModel):
    id: uuid.UUID
    unit_id: uuid.UUID
    title: str

    model_config = {"from_attributes": True}


class VocabularyRead(BaseModel):
    id: uuid.UUID
    korean: str
    english: str
    part_of_speech: str | None
    notes: str | None

    model_config = {"from_attributes": True}


class GrammarPointRead(BaseModel):
    id: uuid.UUID
    name_ko: str
    name_en: str | None
    explanation_en: str | None

    model_config = {"from_attributes": True}


class LessonDetailRead(BaseModel):
    id: uuid.UUID
    unit_id: uuid.UUID
    title: str
    vocabulary: list[VocabularyRead]
    grammar_points: list[GrammarPointRead]
