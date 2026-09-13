"""Curriculum-row publishing workflow. The only place `curation_status` is
allowed to change - never set directly by API handlers or content-pipeline
code."""

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.curriculum import GrammarPoint, Vocabulary
from app.models.enums import CurationStatus

CURATION_MODELS: dict[str, type[Vocabulary] | type[GrammarPoint] | type[Activity]] = {
    "vocabulary": Vocabulary,
    "grammar": GrammarPoint,
    "activity": Activity,
}

# Only a human reviewer calls this (route-guarded by require_staff) - AI
# tooling may only ever create rows as DRAFT, never call this transition.
_ALLOWED_TRANSITIONS: dict[CurationStatus, set[CurationStatus]] = {
    CurationStatus.DRAFT: {CurationStatus.NEEDS_REVIEW, CurationStatus.HUMAN_APPROVED, CurationStatus.REJECTED},
    CurationStatus.NEEDS_REVIEW: {CurationStatus.HUMAN_APPROVED, CurationStatus.REJECTED},
    CurationStatus.HUMAN_APPROVED: {CurationStatus.CANONICAL, CurationStatus.NEEDS_REVIEW, CurationStatus.REJECTED},
    CurationStatus.REJECTED: {CurationStatus.DRAFT},
    CurationStatus.CANONICAL: {CurationStatus.NEEDS_REVIEW},
}


def get_curation_model(item_type: str) -> type[Vocabulary] | type[GrammarPoint] | type[Activity]:
    model = CURATION_MODELS.get(item_type)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown curriculum item type '{item_type}'")
    return model


def list_queue(db: Session, item_type: str, statuses: list[CurationStatus]) -> list[Vocabulary | GrammarPoint | Activity]:
    model = get_curation_model(item_type)
    return list(db.query(model).filter(model.curation_status.in_(statuses)).all())


def transition(
    db: Session,
    item_type: str,
    item_id: uuid.UUID,
    to_status: CurationStatus,
    reviewer_username: str,
) -> Vocabulary | GrammarPoint | Activity:
    model = get_curation_model(item_type)
    row = db.get(model, item_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{item_type} {item_id} not found")

    allowed = _ALLOWED_TRANSITIONS.get(row.curation_status, set())
    if to_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition {item_type} from {row.curation_status.value} to {to_status.value}",
        )

    row.curation_status = to_status
    row.reviewed_by = reviewer_username
    row.reviewed_at = datetime.now(timezone.utc)
    db.flush()
    return row
