import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.enums import MasteryStatus, MistakeCategory, PracticeMode


class ProgressRead(BaseModel):
    lesson_id: uuid.UUID
    vocabulary_mastery: float
    grammar_mastery: float
    listening_mastery: float
    recall_mastery: float
    completion_pct: float
    time_spent_seconds: int

    model_config = {"from_attributes": True}


class VocabularyProgressRead(BaseModel):
    vocabulary_id: uuid.UUID
    practice_mode: PracticeMode
    correct_count: int
    attempt_count: int
    mastery_score: float
    status: MasteryStatus

    model_config = {"from_attributes": True}


class GrammarProgressRead(BaseModel):
    grammar_point_id: uuid.UUID
    correct_count: int
    attempt_count: int
    mastery_score: float
    status: MasteryStatus

    model_config = {"from_attributes": True}


class StreakRead(BaseModel):
    current_streak_days: int
    longest_streak_days: int
    last_active_date: date | None

    model_config = {"from_attributes": True}


class AttemptCreate(BaseModel):
    activity_id: uuid.UUID
    submitted_answer: str
    hints_used: int = 0
    response_time_ms: int | None = None


class AttemptResult(BaseModel):
    attempt_id: uuid.UUID
    is_correct: bool
    score: float
    attempt_number: int


class MistakeRead(BaseModel):
    id: uuid.UUID
    attempt_id: uuid.UUID
    category: MistakeCategory
    vocabulary_id: uuid.UUID | None
    grammar_point_id: uuid.UUID | None
    detail: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
