import uuid

from pydantic import BaseModel


class UnitVocabStatsRead(BaseModel):
    unit_id: uuid.UUID
    unit_number: str
    title_ko: str | None
    title_en: str | None
    word_count: int
    mastered_count: int
    learning_count: int
    needs_review_count: int


class VocabWordRead(BaseModel):
    id: uuid.UUID
    korean: str
    english: str
    romanization: str | None
    notes: str | None
    image_url: str | None
    attempt_count: int
    correct_count: int
    mastery_score: float
    status: str
    last_attempt_at: str | None
    is_teacher_added: bool = False


class VocabQuestionRead(BaseModel):
    vocabulary_id: uuid.UUID
    question_type: str
    prompt: str
    options: list[str] | None
    image_url: str | None


class FlashcardReviewRequest(BaseModel):
    rating: str  # "again" | "hard" | "good" | "easy"


class FlashcardReviewResult(BaseModel):
    status: str
    mastery_score: float


class VocabAttemptRequest(BaseModel):
    question_type: str
    submitted_answer: str
    ui_mode: str | None = None


class VocabAttemptResult(BaseModel):
    is_correct: bool
    correct_answer: str


class QuickRecallResultRequest(BaseModel):
    total: int
    correct: int
    missed_vocabulary_ids: list[uuid.UUID]


class VocabSearchResultRead(BaseModel):
    id: uuid.UUID
    korean: str
    english: str
    romanization: str | None
    notes: str | None
    image_url: str | None
    unit_number: str
    unit_title_ko: str | None
    is_teacher_added: bool = False


class NewVocabularyItemRead(BaseModel):
    id: uuid.UUID
    korean: str
    english: str
    romanization: str | None
    notes: str | None
    image_url: str | None
    unit_number: str
    unit_title_ko: str | None
