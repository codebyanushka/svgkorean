import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.enums import CurationStatus


def list_canonical_activities(db: Session, lesson_id: uuid.UUID) -> list[Activity]:
    return list(
        db.scalars(
            select(Activity).where(
                Activity.lesson_id == lesson_id,
                Activity.curation_status == CurationStatus.CANONICAL,
            )
        )
    )


def get_canonical_activity(db: Session, activity_id: uuid.UUID) -> Activity | None:
    activity = db.get(Activity, activity_id)
    if activity is None or activity.curation_status != CurationStatus.CANONICAL:
        return None
    return activity
