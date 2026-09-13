import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_teacher
from app.db.session import get_db
from app.models.user import User
from app.repositories import attempt_repository, group_repository, progress_repository
from app.schemas.progress import MistakeRead, ProgressRead
from app.schemas.teacher import StudentSummary

router = APIRouter(prefix="/teacher", tags=["teacher"], dependencies=[Depends(require_teacher)])


def _assert_assigned(db: Session, teacher_id: uuid.UUID, student_id: uuid.UUID) -> None:
    if not group_repository.is_student_assigned_to_teacher(db, teacher_id, student_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student is not assigned to you")


@router.get("/students", response_model=list[StudentSummary])
def list_students(
    db: Session = Depends(get_db), current_user: User = Depends(require_teacher)
) -> list[StudentSummary]:
    return list(group_repository.list_students_for_teacher(db, current_user.id))


@router.get("/students/{student_id}/progress", response_model=list[ProgressRead])
def get_student_progress(
    student_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)
) -> list[ProgressRead]:
    _assert_assigned(db, current_user.id, student_id)
    return list(progress_repository.list_progress_for_user(db, student_id))


@router.get("/students/{student_id}/mistakes", response_model=list[MistakeRead])
def get_student_mistakes(
    student_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)
) -> list[MistakeRead]:
    _assert_assigned(db, current_user.id, student_id)
    return list(attempt_repository.list_mistakes_for_user(db, student_id))
