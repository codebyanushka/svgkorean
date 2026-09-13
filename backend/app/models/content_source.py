"""Content sources and the atomic content-verification unit.

A ContentSource is one source PDF (textbook/workbook/vocab&grammar/additional
activities). A ContentBlock is a single OCR'd text span on one page of one
source - the unit the human verification workflow operates on. Nothing in
`verified_text` is trusted until `verification_status` is APPROVED or EDITED
by an operator; `draft_text` is never modified after OCR.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import SourceType, VerificationStatus


class ContentSource(Base):
    __tablename__ = "content_sources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    blocks: Mapped[list["ContentBlock"]] = relationship(back_populates="source", cascade="all, delete-orphan")


class ContentBlock(Base):
    __tablename__ = "content_blocks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_sources.id"), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    block_index: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False)  # "ko" | "en" | "mixed"
    bbox: Mapped[list[float] | None] = mapped_column(JSONB, nullable=True)

    ocr_engine: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ocr_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    draft_text: Mapped[str] = mapped_column(Text, nullable=False)

    block_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    unit_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("units.id"), nullable=True)
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("lessons.id"), nullable=True)

    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus), nullable=False, default=VerificationStatus.PENDING
    )
    verified_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    verified_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source: Mapped["ContentSource"] = relationship(back_populates="blocks")
