import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import CurationStatus


class CurationItemRead(BaseModel):
    id: uuid.UUID
    item_type: str
    summary: str
    curation_status: CurationStatus
    proposed_by: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None


class CurationTransitionRequest(BaseModel):
    to_status: CurationStatus
