"""Curriculum structure and vocabulary/grammar curriculum entries.

Vocabulary and GrammarPoint rows are proposed from already-reviewed OCR
content (see content_source.ContentBlock) - their `source_block_id` is the
provenance link back to the exact block a row was drafted from. A row's own
`curation_status` (see enums.CurationStatus) is a SEPARATE, later gate: a row
starts as DRAFT/NEEDS_REVIEW even when its source block was APPROVED, and
only becomes CANONICAL (visible to students) after explicit human review -
never automatically upgraded by AI tooling.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CurationStatus


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    number: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)  # "00" (intro), "01".."10"
    title_ko: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lessons: Mapped[list["Lesson"]] = relationship(back_populates="unit", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    unit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("units.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    unit: Mapped["Unit"] = relationship(back_populates="lessons")
    vocabulary: Mapped[list["Vocabulary"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
    grammar_points: Mapped[list["GrammarPoint"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")


class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    korean: Mapped[str] = mapped_column(String(255), nullable=False)
    english: Mapped[str] = mapped_column(String(255), nullable=False)
    romanization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    part_of_speech: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source_block_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_blocks.id"), nullable=True)
    curation_status: Mapped[CurationStatus] = mapped_column(
        Enum(CurationStatus), nullable=False, default=CurationStatus.DRAFT
    )
    proposed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lesson: Mapped["Lesson"] = relationship(back_populates="vocabulary")


class GrammarPoint(Base):
    __tablename__ = "grammar_points"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    name_ko: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    explanation_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_block_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_blocks.id"), nullable=True)
    curation_status: Mapped[CurationStatus] = mapped_column(
        Enum(CurationStatus), nullable=False, default=CurationStatus.DRAFT
    )
    proposed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lesson: Mapped["Lesson"] = relationship(back_populates="grammar_points")