"""Shared data structures passed between content pipeline stages.

These describe the shape of data as it moves through render -> ocr ->
reconstruct -> compare -> verify -> seed. No curriculum content lives here.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PageImage:
    source_key: str  # "textbook" | "workbook" | "vocab_grammar" | "additional_activities"
    source_pdf: Path
    page_number: int
    image_path: Path


@dataclass
class TextBlock:
    text: str
    confidence: float
    bbox: tuple[float, float, float, float]
    language: str  # "ko" | "en"


@dataclass
class PageExtraction:
    page: PageImage
    blocks: list[TextBlock] = field(default_factory=list)
    engine: str = ""


@dataclass
class VerificationFlag:
    page_number: int
    reason: str
    block_index: int | None = None


@dataclass
class VerifiedPage:
    """A human-approved page. Only content that reached this stage may be
    imported into the database as canonical curriculum content."""

    page_number: int
    blocks: list[TextBlock]
    approved_by: str
    source_pdf: Path


@dataclass
class VerificationRecord:
    """One block's verification decision. Mirrors the ContentBlock DB model
    fields 1:1 so this can be loaded straight into Postgres once approved."""

    source_key: str
    source_pdf: str
    page_number: int
    block_index: int
    bbox: tuple[float, float, float, float]
    language: str
    ocr_engine: str
    ocr_confidence: float
    draft_text: str  # original OCR output - never modified
    verification_status: str  # APPROVED | EDITED | REJECTED | NEEDS_REVIEW
    verified_text: str | None  # None for REJECTED/unresolved NEEDS_REVIEW
    verified_by: str
    notes: str | None = None
