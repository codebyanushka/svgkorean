"""Student learning-interaction and mastery tracking.

Nothing here stores curriculum content - only what a specific user did
(Attempt), what went wrong (Mistake), and rollups derived from those raw
events (VocabularyProgress/GrammarProgress/Progress/Streak). Rollups are
recomputed by services/ from Attempt rows - never hand-edited, never the
source of truth themselves.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import MasteryStatus, MistakeCategory, PracticeMode


class Attempt(Base):
    """Every submitted answer, unabridged. This is the raw event log that
    every mastery/analytics rollup is computed from."""

    __tablename__ = "attempts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    activity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("activities.id"), nullable=False)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    vocabulary_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("vocabulary.id"), nullable=True)
    grammar_point_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("grammar_points.id"), nullable=True)
    practice_mode: Mapped[PracticeMode | None] = mapped_column(Enum(PracticeMode), nullable=True)

    submitted_answer: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # 0.0-1.0, partial credit allowed
    hints_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    mistakes: Mapped[list["Mistake"]] = relationship(back_populates="attempt", cascade="all, delete-orphan")


class Mistake(Base):
    """A structured, categorized mistake derived from one Attempt. An
    incorrect Attempt may produce zero (e.g. simple typo already captured by
    score) or more than one Mistake row (e.g. both a grammar and a spacing
    issue in the same sentence-construction attempt)."""

    __tablename__ = "mistakes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("attempts.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    category: Mapped[MistakeCategory] = mapped_column(Enum(MistakeCategory), nullable=False)
    vocabulary_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("vocabulary.id"), nullable=True)
    grammar_point_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("grammar_points.id"), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    attempt: Mapped["Attempt"] = relationship(back_populates="mistakes")


class VocabularyProgress(Base):
    """Per-user, per-word, per-cognitive-mode mastery rollup. A word is
    tracked separately for recognition vs. recall vs. listening vs. context
    use - so a student who recognizes 학교 but can't recall it unprompted
    shows up accurately rather than as one blended "80% mastered" number."""

    __tablename__ = "vocabulary_progress"
    __table_args__ = (UniqueConstraint("user_id", "vocabulary_id", "practice_mode", name="uq_vocab_progress_mode"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    vocabulary_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vocabulary.id"), nullable=False)
    practice_mode: Mapped[PracticeMode] = mapped_column(Enum(PracticeMode), nullable=False)

    correct_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mastery_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # 0.0-1.0
    status: Mapped[MasteryStatus] = mapped_column(Enum(MasteryStatus), nullable=False, default=MasteryStatus.NEEDS_REVIEW)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class GrammarProgress(Base):
    """Per-user, per-grammar-point mastery rollup."""

    __tablename__ = "grammar_progress"
    __table_args__ = (UniqueConstraint("user_id", "grammar_point_id", name="uq_grammar_progress"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    grammar_point_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("grammar_points.id"), nullable=False)

    correct_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mastery_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[MasteryStatus] = mapped_column(Enum(MasteryStatus), nullable=False, default=MasteryStatus.NEEDS_REVIEW)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Progress(Base):
    """Per-user, per-lesson rollup - what the student Home/Progress screens
    render directly. Recomputed from VocabularyProgress/GrammarProgress/
    Attempt, not maintained independently."""

    __tablename__ = "progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_progress_lesson"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id"), nullable=False)

    vocabulary_mastery: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    grammar_mastery: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    listening_mastery: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recall_mastery: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    completion_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Streak(Base):
    """Per-user daily-activity streak, one row per user."""

    __tablename__ = "streaks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    current_streak_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    longest_streak_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
