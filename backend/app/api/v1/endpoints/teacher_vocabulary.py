"""Teacher-facing vocabulary management: create/edit DRAFT vocabulary and
publish it (transition to CANONICAL) - the actual publishing state machine
still lives in curation_service, this module just adds the CRUD that was
missing (previously vocabulary could only be created by content_pipeline
scripts, never by a teacher through the app)."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import require_staff
from app.db.session import get_db
from app.models.enums import CurationStatus
from app.models.user import User
from app.repositories import curriculum_repository
from app.schemas.teacher_vocabulary import VocabularyCreateRequest, VocabularyManageRead, VocabularyUpdateRequest
from app.services import curation_service
from app.services.romanization import romanize

router = APIRouter(prefix="/teacher/vocabulary", tags=["teacher-vocabulary"], dependencies=[Depends(require_staff)])

REPO_ROOT = Path(__file__).resolve().parents[5]
TEACHER_UPLOADS_DIR = REPO_ROOT / "data" / "extracted" / "media" / "teacher_uploads"
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _image_url(image_path: str | None) -> str | None:
    if image_path is None:
        return None
    return f"/media/images/{image_path.removeprefix('data/extracted/media/')}"


def _to_read(row) -> VocabularyManageRead:
    return VocabularyManageRead(
        id=row.id,
        lesson_id=row.lesson_id,
        korean=row.korean,
        english=row.english,
        romanization=row.romanization,
        part_of_speech=row.part_of_speech,
        notes=row.notes,
        image_url=_image_url(row.image_path),
        curation_status=row.curation_status,
    )


@router.get("", response_model=list[VocabularyManageRead])
def list_vocabulary(unit_number: str = Query(...), db: Session = Depends(get_db)) -> list[VocabularyManageRead]:
    unit = curriculum_repository.get_unit_by_number(db, unit_number)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    rows = curriculum_repository.list_all_vocabulary_for_unit(db, unit.id)
    return [_to_read(r) for r in rows]


@router.post("", response_model=VocabularyManageRead, status_code=status.HTTP_201_CREATED)
def create_vocabulary(
    payload: VocabularyCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(require_staff)
) -> VocabularyManageRead:
    unit = curriculum_repository.get_unit_by_number(db, payload.unit_number)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    if payload.lesson_id is not None:
        lesson = curriculum_repository.get_lesson(db, payload.lesson_id)
        if lesson is None or lesson.unit_id != unit.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lesson does not belong to this unit")
    else:
        lessons = curriculum_repository.list_lessons_for_unit(db, unit.id)
        if not lessons:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unit has no lesson to attach vocabulary to")
        lesson = lessons[0]
    row = curriculum_repository.create_vocabulary(
        db,
        lesson_id=lesson.id,
        korean=payload.korean,
        english=payload.english,
        romanization=payload.romanization or romanize(payload.korean),
        part_of_speech=payload.part_of_speech,
        notes=payload.notes,
        curation_status=CurationStatus.DRAFT,
        proposed_by=f"teacher:{current_user.username}",
    )
    db.commit()
    return _to_read(row)


@router.put("/{vocabulary_id}", response_model=VocabularyManageRead)
def update_vocabulary(
    vocabulary_id: uuid.UUID, payload: VocabularyUpdateRequest, db: Session = Depends(get_db)
) -> VocabularyManageRead:
    row = curriculum_repository.get_vocabulary(db, vocabulary_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vocabulary not found")
    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field_name, value)
    if payload.korean is not None and payload.romanization is None:
        row.romanization = romanize(payload.korean)
    db.commit()
    return _to_read(row)


@router.post("/{vocabulary_id}/publish", response_model=VocabularyManageRead)
def publish_vocabulary(
    vocabulary_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_staff)
) -> VocabularyManageRead:
    row = curriculum_repository.get_vocabulary(db, vocabulary_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vocabulary not found")
    if row.curation_status == CurationStatus.CANONICAL:
        return _to_read(row)
    if row.curation_status != CurationStatus.HUMAN_APPROVED:
        curation_service.transition(db, "vocabulary", vocabulary_id, CurationStatus.HUMAN_APPROVED, current_user.username)
    row = curation_service.transition(db, "vocabulary", vocabulary_id, CurationStatus.CANONICAL, current_user.username)
    db.commit()
    return _to_read(row)


@router.post("/{vocabulary_id}/image", response_model=VocabularyManageRead)
async def upload_vocabulary_image(
    vocabulary_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
) -> VocabularyManageRead:
    row = curriculum_repository.get_vocabulary(db, vocabulary_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vocabulary not found")
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image type")
    TEACHER_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{vocabulary_id}{ext}"
    dest_path = TEACHER_UPLOADS_DIR / filename
    contents = await file.read()
    dest_path.write_bytes(contents)
    row.image_path = f"data/extracted/media/teacher_uploads/{filename}"
    db.commit()
    return _to_read(row)


@router.delete("/{vocabulary_id}/image", response_model=VocabularyManageRead)
def remove_vocabulary_image(
    vocabulary_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_staff)
) -> VocabularyManageRead:
    row = curriculum_repository.get_vocabulary(db, vocabulary_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vocabulary not found")
    if row.image_path is not None:
        existing_path = REPO_ROOT / row.image_path
        existing_path.unlink(missing_ok=True)
        row.image_path = None
        db.commit()
    return _to_read(row)
