import uuid

from pydantic import BaseModel


class StudentSummary(BaseModel):
    id: uuid.UUID
    username: str

    model_config = {"from_attributes": True}
