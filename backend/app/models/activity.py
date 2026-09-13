"""Data-driven learning activities. The frontend renders these purely based
on `type` - no curriculum text is ever hardcoded into a component.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ActivityType, CurationStatus


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    type: Mapped[ActivityType] = mapped_column(Enum(ActivityType), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    activity_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    source_block_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_blocks.id"), nullable=True)
    curation_status: Mapped[CurationStatus] = mapped_column(
        Enum(CurationStatus), nullable=False, default=CurationStatus.DRAFT
    )
    proposed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    options: Mapped[list["ActivityOption"]] = relationship(back_populates="activity", cascade="all, delete-orphan")
    accepted_answers: Mapped[list["AcceptedAnswer"]] = relationship(
        back_populates="activity", cascade="all, delete-orphan"
    )


class ActivityOption(Base):
    __tablename__ = "activity_options"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    activity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("activities.id"), nullable=False)
    text: Mapped[str] = mapped_column(String(255), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    activity: Mapped["Activity"] = relationship(back_populates="options")


class AcceptedAnswer(Base):
    __tablename__ = "accepted_answers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    activity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("activities.id"), nullable=False)
    answer_text: Mapped[str] = mapped_column(String(255), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    activity: Mapped["Activity"] = relationship(back_populates="accepted_answers")
