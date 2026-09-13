import uuid

from pydantic import BaseModel

from app.models.enums import ActivityType


class ActivityOptionRead(BaseModel):
    """`is_correct` is intentionally never included - never leak answers to
    the client before grading."""

    id: uuid.UUID
    text: str


class ActivityRead(BaseModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    type: ActivityType
    prompt: str
    metadata: dict | None = None
    options: list[ActivityOptionRead] = []
    image_url: str | None = None
    source: str | None = None
