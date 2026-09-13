import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_staff
from app.db.session import get_db
from app.models.activity import Activity
from app.models.curriculum import GrammarPoint, Vocabulary
from app.models.enums import CurationStatus
from app.models.user import User
from app.schemas.curation import CurationItemRead, CurationTransitionRequest
from app.services import curation_service

router = APIRouter(prefix="/curation", tags=["curation"], dependencies=[Depends(require_staff)])


def _summarize(item_type: str, row: Vocabulary | GrammarPoint | Activity) -> str:
    if isinstance(row, Vocabulary):
        return f"{row.korean} / {row.english}"
    if isinstance(row, GrammarPoint):
        return row.name_ko if not row.name_en else f"{row.name_ko} ({row.name_en})"
    return row.prompt


def _to_read(item_type: str, row: Vocabulary | GrammarPoint | Activity) -> CurationItemRead:
    return CurationItemRead(
        id=row.id,
        item_type=item_type,
        summary=_summarize(item_type, row),
        curation_status=row.curation_status,
        proposed_by=row.proposed_by,
        reviewed_by=row.reviewed_by,
        reviewed_at=row.reviewed_at,
    )


@router.get("/{item_type}", response_model=list[CurationItemRead])
def list_queue(
    item_type: str,
    statuses: list[CurationStatus] = Query(default=[CurationStatus.DRAFT, CurationStatus.NEEDS_REVIEW]),
    db: Session = Depends(get_db),
) -> list[CurationItemRead]:
    rows = curation_service.list_queue(db, item_type, statuses)
    return [_to_read(item_type, row) for row in rows]


@router.post("/{item_type}/{item_id}/transition", response_model=CurationItemRead)
def transition_item(
    item_type: str,
    item_id: uuid.UUID,
    payload: CurationTransitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
) -> CurationItemRead:
    row = curation_service.transition(db, item_type, item_id, payload.to_status, current_user.username)
    db.commit()
    return _to_read(item_type, row)
