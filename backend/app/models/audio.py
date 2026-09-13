"""Canonical audio asset registry. File paths are never scattered directly
into lesson/activity rows - everything about an audio file, including its
unit/lesson mapping and how that mapping was verified, lives here.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import SourceType, VerificationStatus


class AudioAsset(Base):
    __tablename__ = "audio_assets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    source_archive: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    format: Mapped[str] = mapped_column(String(16), nullable=False)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    unit_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("units.id"), nullable=True)
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("lessons.id"), nullable=True)
    activity_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("activities.id"), nullable=True)

    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus), nullable=False, default=VerificationStatus.PENDING
    )
    verified_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_ref: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    unit: Mapped["Unit | None"] = relationship()
    lesson: Mapped["Lesson | None"] = relationship()
    activity: Mapped["Activity | None"] = relationship()
