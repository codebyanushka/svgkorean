import uuid
from datetime import datetime

from pydantic import BaseModel


class StudentSummary(BaseModel):
    id: uuid.UUID
    username: str

    model_config = {"from_attributes": True}


class StudentCreateRequest(BaseModel):
    username: str
    password: str


class MissedVocabularyItem(BaseModel):
    vocabulary_id: uuid.UUID
    korean: str
    english: str
    miss_count: int


class RecentVocabularyItem(BaseModel):
    vocabulary_id: uuid.UUID
    korean: str
    english: str


class TeacherAddedVocabularyItem(BaseModel):
    vocabulary_id: uuid.UUID
    korean: str
    english: str
    unit_number: str
    curation_status: str
    proposed_by: str | None


class TeacherOverviewRead(BaseModel):
    student_count: int
    frequently_missed: list[MissedVocabularyItem]
    recently_practiced: list[RecentVocabularyItem]
    teacher_added_vocabulary: list[TeacherAddedVocabularyItem]
    teacher_added_count: int


class LessonBrief(BaseModel):
    id: uuid.UUID
    title: str


class UnitWithLessonsRead(BaseModel):
    id: uuid.UUID
    number: str
    title_ko: str | None
    title_en: str | None
    lessons: list[LessonBrief]


class UnitCreateRequest(BaseModel):
    title_ko: str
    title_en: str | None = None
    first_lesson_title: str | None = None


class LessonCreateRequest(BaseModel):
    title: str


class StudentOverviewItem(BaseModel):
    id: uuid.UUID
    username: str
    current_unit_number: str | None
    current_unit_title_ko: str | None
    current_lesson_title: str | None
    progress_pct: float
    last_activity_text: str
    last_activity_at: datetime | None
    last_login_at: datetime | None
    status: str  # "ACTIVE" | "INACTIVE" | "NEW"


class AttemptDetailRead(BaseModel):
    id: uuid.UUID
    created_at: datetime
    practice_mode: str | None
    ui_mode: str | None
    is_correct: bool
    submitted_answer: str
    vocabulary_korean: str | None
    vocabulary_english: str | None
    unit_number: str | None
    lesson_title: str | None


class ActivityFeedItem(BaseModel):
    id: uuid.UUID
    created_at: datetime
    student_id: uuid.UUID
    student_username: str
    ui_mode: str | None
    mode_label: str
    practice_mode: str | None
    is_correct: bool
    vocabulary_korean: str | None
    vocabulary_english: str | None
    unit_number: str | None


class MistakeAggregateItem(BaseModel):
    vocabulary_id: uuid.UUID | None
    korean: str | None
    english: str | None
    miss_count: int
    student_count: int


class MistakeCategoryBreakdownItem(BaseModel):
    category: str
    count: int


class StudentMistakeCount(BaseModel):
    student_id: uuid.UUID
    username: str
    mistake_count: int


class ClassMistakesOverview(BaseModel):
    total_mistakes: int
    top_missed_words: list[MistakeAggregateItem]
    category_breakdown: list[MistakeCategoryBreakdownItem]
    most_mistakes_students: list[StudentMistakeCount]


class ModeBreakdownItem(BaseModel):
    ui_mode: str | None
    label: str
    count: int


class ClassAnalytics(BaseModel):
    student_count: int
    active_count: int
    inactive_count: int
    new_count: int
    avg_mastery_pct: float
    total_attempts: int
    total_mistakes: int
    most_practiced_unit_number: str | None
    mode_breakdown: list[ModeBreakdownItem]
