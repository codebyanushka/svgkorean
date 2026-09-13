import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_teacher
from app.core.security import hash_password
from app.db.session import get_db
from app.models.enums import PracticeMode
from app.models.user import Role, User
from app.repositories import (
    attempt_repository,
    curriculum_repository,
    group_repository,
    progress_repository,
    user_repository,
)
from app.schemas.progress import MistakeRead, ProgressRead
from app.schemas.teacher import (
    ActivityFeedItem,
    AttemptDetailRead,
    ClassAnalytics,
    ClassMistakesOverview,
    LessonBrief,
    LessonCreateRequest,
    MissedVocabularyItem,
    MistakeAggregateItem,
    MistakeCategoryBreakdownItem,
    ModeBreakdownItem,
    RecentVocabularyItem,
    StudentCreateRequest,
    StudentMistakeCount,
    StudentOverviewItem,
    StudentSummary,
    TeacherAddedVocabularyItem,
    TeacherOverviewRead,
    UnitCreateRequest,
    UnitWithLessonsRead,
)
from app.schemas.teacher_vocabulary import StudentVocabInsights
from app.services import vocab_lab_service

router = APIRouter(prefix="/teacher", tags=["teacher"], dependencies=[Depends(require_teacher)])


def _assert_assigned(db: Session, teacher_id: uuid.UUID, student_id: uuid.UUID) -> None:
    if not group_repository.is_student_assigned_to_teacher(db, teacher_id, student_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student is not assigned to you")


@router.get("/students", response_model=list[StudentSummary])
def list_students(
    db: Session = Depends(get_db), current_user: User = Depends(require_teacher)
) -> list[StudentSummary]:
    return list(group_repository.list_students_for_teacher(db, current_user.id))


_ACTIVITY_TEXT_BY_MODE: dict[PracticeMode, str] = {
    PracticeMode.RECALL_KO_TO_EN: "Practiced Korean \u2192 English recall",
    PracticeMode.RECALL_EN_TO_KO: "Practiced English \u2192 Korean recall",
    PracticeMode.CONTEXT: "Practiced vocabulary in context",
    PracticeMode.LISTENING: "Practiced listening",
}
_FLASHCARD_RATINGS = {"again", "hard", "good", "easy"}

UI_MODE_LABELS: dict[str, str] = {
    "flashcards": "Flashcards",
    "multiple_choice": "Multiple Choice",
    "matching": "Matching",
    "fill_blank": "Fill in the Blank",
    "ko_to_en": "Korean \u2192 English",
    "en_to_ko": "English \u2192 Korean",
    "recall": "Recall (mixed)",
    "apply": "Apply in Context",
    "quick_recall": "Quick Recall",
    "smart_revision": "Smart Revision",
    "test": "Test",
}


def _describe_last_activity(latest) -> str:
    ui_label = UI_MODE_LABELS.get(latest.ui_mode) if latest.ui_mode else None
    if ui_label is not None:
        return f"Practiced with {ui_label}"
    if latest.practice_mode == PracticeMode.RECOGNITION and latest.submitted_answer in _FLASHCARD_RATINGS:
        return "Reviewed flashcards"
    if latest.practice_mode == PracticeMode.RECOGNITION:
        return "Took a vocabulary quiz"
    return _ACTIVITY_TEXT_BY_MODE.get(latest.practice_mode, "Practiced vocabulary")


def _build_overview_item(db: Session, student: User) -> StudentOverviewItem:
    attempts = attempt_repository.list_attempts_for_user(db, student.id)
    latest = attempts[0] if attempts else None

    current_unit_number = current_unit_title_ko = current_lesson_title = None
    progress_pct = 0.0
    last_activity_text = "No activity yet"
    last_activity_at = None
    status_label = "NEW"

    if latest is not None:
        lesson = curriculum_repository.get_lesson(db, latest.lesson_id)
        if lesson is not None:
            unit = curriculum_repository.get_unit(db, lesson.unit_id)
            current_unit_number = unit.number if unit else None
            current_unit_title_ko = unit.title_ko if unit else None
            current_lesson_title = lesson.title
            progress_rows = progress_repository.list_progress_for_user(db, student.id)
            matching = next((p for p in progress_rows if p.lesson_id == lesson.id), None)
            progress_pct = matching.completion_pct if matching else 0.0
        last_activity_text = _describe_last_activity(latest)
        last_activity_at = latest.created_at
        days_since = (datetime.now(timezone.utc) - latest.created_at).days
        status_label = "ACTIVE" if days_since <= 7 else "INACTIVE"

    return StudentOverviewItem(
        id=student.id,
        username=student.username,
        current_unit_number=current_unit_number,
        current_unit_title_ko=current_unit_title_ko,
        current_lesson_title=current_lesson_title,
        progress_pct=progress_pct,
        last_activity_text=last_activity_text,
        last_activity_at=last_activity_at,
        last_login_at=student.last_login_at,
        status=status_label,
    )


@router.get("/students-overview", response_model=list[StudentOverviewItem])
def students_overview(
    db: Session = Depends(get_db), current_user: User = Depends(require_teacher)
) -> list[StudentOverviewItem]:
    students = group_repository.list_students_for_teacher(db, current_user.id)
    return [_build_overview_item(db, student) for student in students]


@router.post("/students", response_model=StudentSummary, status_code=status.HTTP_201_CREATED)
def create_student(
    payload: StudentCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)
) -> StudentSummary:
    if user_repository.get_by_username(db, payload.username) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
    if len(payload.password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters")

    student = User(username=payload.username, hashed_password=hash_password(payload.password), role=Role.STUDENT)
    db.add(student)
    db.flush()

    group = group_repository.get_or_create_teacher_group(db, current_user)
    group_repository.add_student_to_group(db, group.id, student.id)
    db.commit()

    return StudentSummary(id=student.id, username=student.username)


@router.get("/units", response_model=list[UnitWithLessonsRead])
def list_units(db: Session = Depends(get_db), current_user: User = Depends(require_teacher)) -> list[UnitWithLessonsRead]:
    units = curriculum_repository.list_units(db)
    return [
        UnitWithLessonsRead(
            id=unit.id,
            number=unit.number,
            title_ko=unit.title_ko,
            title_en=unit.title_en,
            lessons=[LessonBrief(id=lesson.id, title=lesson.title) for lesson in curriculum_repository.list_lessons_for_unit(db, unit.id)],
        )
        for unit in units
    ]


@router.post("/units", response_model=UnitWithLessonsRead, status_code=status.HTTP_201_CREATED)
def create_unit(
    payload: UnitCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)
) -> UnitWithLessonsRead:
    unit = curriculum_repository.create_unit(db, payload.title_ko, payload.title_en, payload.first_lesson_title)
    db.commit()
    lessons = curriculum_repository.list_lessons_for_unit(db, unit.id)
    return UnitWithLessonsRead(
        id=unit.id,
        number=unit.number,
        title_ko=unit.title_ko,
        title_en=unit.title_en,
        lessons=[LessonBrief(id=lesson.id, title=lesson.title) for lesson in lessons],
    )


@router.post("/units/{unit_id}/lessons", response_model=LessonBrief, status_code=status.HTTP_201_CREATED)
def create_lesson(
    unit_id: uuid.UUID, payload: LessonCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)
) -> LessonBrief:
    unit = curriculum_repository.get_unit(db, unit_id)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    lesson = curriculum_repository.create_lesson(db, unit_id, payload.title)
    db.commit()
    return LessonBrief(id=lesson.id, title=lesson.title)


@router.get("/overview", response_model=TeacherOverviewRead)
def get_overview(
    db: Session = Depends(get_db), current_user: User = Depends(require_teacher)
) -> TeacherOverviewRead:
    students = group_repository.list_students_for_teacher(db, current_user.id)
    student_ids = [s.id for s in students]

    missed_pairs = attempt_repository.list_frequently_missed_vocabulary(db, student_ids)
    missed_words = {w.id: w for w in curriculum_repository.get_vocabulary_by_ids(db, [p[0] for p in missed_pairs])}
    frequently_missed = [
        MissedVocabularyItem(vocabulary_id=vid, korean=missed_words[vid].korean, english=missed_words[vid].english, miss_count=count)
        for vid, count in missed_pairs
        if vid in missed_words
    ]

    recent_ids = attempt_repository.list_recently_practiced_vocabulary(db, student_ids)
    recent_words = {w.id: w for w in curriculum_repository.get_vocabulary_by_ids(db, recent_ids)}
    recently_practiced = [
        RecentVocabularyItem(vocabulary_id=vid, korean=recent_words[vid].korean, english=recent_words[vid].english)
        for vid in recent_ids
        if vid in recent_words
    ]

    teacher_added = curriculum_repository.list_teacher_added_vocabulary(db)
    teacher_added_vocabulary = [
        TeacherAddedVocabularyItem(
            vocabulary_id=w.id,
            korean=w.korean,
            english=w.english,
            unit_number=w.lesson.unit.number,
            curation_status=w.curation_status.value,
            proposed_by=w.proposed_by,
        )
        for w in teacher_added
    ]

    return TeacherOverviewRead(
        student_count=len(students),
        frequently_missed=frequently_missed,
        recently_practiced=recently_practiced,
        teacher_added_vocabulary=teacher_added_vocabulary,
        teacher_added_count=curriculum_repository.count_teacher_added_vocabulary(db),
    )


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


@router.get("/students/{student_id}/overview", response_model=StudentOverviewItem)
def get_student_overview(
    student_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)
) -> StudentOverviewItem:
    _assert_assigned(db, current_user.id, student_id)
    student = user_repository.get_by_id(db, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return _build_overview_item(db, student)


@router.get("/students/{student_id}/attempts", response_model=list[AttemptDetailRead])
def get_student_attempts(
    student_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher),
) -> list[AttemptDetailRead]:
    _assert_assigned(db, current_user.id, student_id)
    attempts = attempt_repository.list_attempts_for_user(db, student_id)[:limit]

    vocab_ids = {a.vocabulary_id for a in attempts if a.vocabulary_id is not None}
    vocab_by_id = {v.id: v for v in curriculum_repository.get_vocabulary_by_ids(db, list(vocab_ids))}
    lesson_by_id = {}
    unit_by_id = {}
    results: list[AttemptDetailRead] = []
    for attempt in attempts:
        lesson = lesson_by_id.get(attempt.lesson_id)
        if lesson is None:
            lesson = curriculum_repository.get_lesson(db, attempt.lesson_id)
            lesson_by_id[attempt.lesson_id] = lesson
        unit = None
        if lesson is not None:
            unit = unit_by_id.get(lesson.unit_id)
            if unit is None:
                unit = curriculum_repository.get_unit(db, lesson.unit_id)
                unit_by_id[lesson.unit_id] = unit
        vocab = vocab_by_id.get(attempt.vocabulary_id) if attempt.vocabulary_id else None
        results.append(
            AttemptDetailRead(
                id=attempt.id,
                created_at=attempt.created_at,
                practice_mode=attempt.practice_mode.value if attempt.practice_mode else None,
                ui_mode=attempt.ui_mode,
                is_correct=attempt.is_correct,
                submitted_answer=attempt.submitted_answer,
                vocabulary_korean=vocab.korean if vocab else None,
                vocabulary_english=vocab.english if vocab else None,
                unit_number=unit.number if unit else None,
                lesson_title=lesson.title if lesson else None,
            )
        )
    return results


@router.get("/students/{student_id}/vocabulary-insights", response_model=StudentVocabInsights)
def get_student_vocabulary_insights(
    student_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)
) -> StudentVocabInsights:
    _assert_assigned(db, current_user.id, student_id)

    units = curriculum_repository.list_units(db)
    all_vocabulary = []
    for unit in units:
        for lesson in curriculum_repository.list_lessons_for_unit(db, unit.id):
            all_vocabulary.extend(curriculum_repository.list_canonical_vocabulary(db, lesson.id))

    mastery = vocab_lab_service.word_mastery_for_words(db, student_id, all_vocabulary)
    tracked = [m for m in mastery.values() if m.attempt_count > 0]
    mastered = [m.vocabulary.korean for m in tracked if m.status == "MASTERED"]
    weak = [m.vocabulary.korean for m in tracked if m.status == "NEEDS_REVIEW"]
    mastery_pct = round(100 * len(mastered) / len(tracked), 1) if tracked else 0.0
    recent_attempts = attempt_repository.list_attempts_for_user(db, student_id)

    return StudentVocabInsights(
        mastery_pct=mastery_pct,
        words_tracked=len(tracked),
        weak_words=weak,
        mastered_words=mastered,
        recent_attempt_count=len(recent_attempts),
    )


@router.get("/activity", response_model=list[ActivityFeedItem])
def get_class_activity(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher),
) -> list[ActivityFeedItem]:
    students = group_repository.list_students_for_teacher(db, current_user.id)
    student_by_id = {s.id: s for s in students}

    pairs: list[tuple[uuid.UUID, object]] = []
    for student in students:
        for attempt in attempt_repository.list_attempts_for_user(db, student.id):
            pairs.append((student.id, attempt))
    pairs.sort(key=lambda pair: pair[1].created_at, reverse=True)
    pairs = pairs[:limit]

    vocab_ids = {a.vocabulary_id for _, a in pairs if a.vocabulary_id is not None}
    vocab_by_id = {v.id: v for v in curriculum_repository.get_vocabulary_by_ids(db, list(vocab_ids))}
    lesson_by_id: dict[uuid.UUID, object] = {}
    unit_by_id: dict[uuid.UUID, object] = {}

    results: list[ActivityFeedItem] = []
    for student_id, attempt in pairs:
        lesson = lesson_by_id.get(attempt.lesson_id)
        if attempt.lesson_id not in lesson_by_id:
            lesson = curriculum_repository.get_lesson(db, attempt.lesson_id)
            lesson_by_id[attempt.lesson_id] = lesson
        unit = None
        if lesson is not None:
            unit = unit_by_id.get(lesson.unit_id)
            if lesson.unit_id not in unit_by_id:
                unit = curriculum_repository.get_unit(db, lesson.unit_id)
                unit_by_id[lesson.unit_id] = unit
        vocab = vocab_by_id.get(attempt.vocabulary_id) if attempt.vocabulary_id else None
        mode_label = UI_MODE_LABELS.get(attempt.ui_mode) if attempt.ui_mode else None
        if mode_label is None:
            mode_label = attempt.practice_mode.value if attempt.practice_mode else "Unknown"
        results.append(
            ActivityFeedItem(
                id=attempt.id,
                created_at=attempt.created_at,
                student_id=student_id,
                student_username=student_by_id[student_id].username,
                ui_mode=attempt.ui_mode,
                mode_label=mode_label,
                practice_mode=attempt.practice_mode.value if attempt.practice_mode else None,
                is_correct=attempt.is_correct,
                vocabulary_korean=vocab.korean if vocab else None,
                vocabulary_english=vocab.english if vocab else None,
                unit_number=unit.number if unit else None,
            )
        )
    return results


@router.get("/mistakes-overview", response_model=ClassMistakesOverview)
def get_class_mistakes_overview(
    db: Session = Depends(get_db), current_user: User = Depends(require_teacher)
) -> ClassMistakesOverview:
    students = group_repository.list_students_for_teacher(db, current_user.id)

    all_mistakes = []
    per_student_count: dict[uuid.UUID, int] = {}
    for student in students:
        mistakes = attempt_repository.list_mistakes_for_user(db, student.id)
        per_student_count[student.id] = len(mistakes)
        all_mistakes.extend(mistakes)

    vocab_ids = {m.vocabulary_id for m in all_mistakes if m.vocabulary_id is not None}
    vocab_by_id = {v.id: v for v in curriculum_repository.get_vocabulary_by_ids(db, list(vocab_ids))}

    word_counts: dict[uuid.UUID, dict] = {}
    category_counts: dict[str, int] = {}
    for m in all_mistakes:
        category_counts[m.category.value] = category_counts.get(m.category.value, 0) + 1
        if m.vocabulary_id is not None:
            entry = word_counts.setdefault(m.vocabulary_id, {"count": 0, "students": set()})
            entry["count"] += 1
            entry["students"].add(m.user_id)

    top_missed = sorted(word_counts.items(), key=lambda kv: kv[1]["count"], reverse=True)[:15]
    top_missed_words = [
        MistakeAggregateItem(
            vocabulary_id=vid,
            korean=vocab_by_id[vid].korean if vid in vocab_by_id else None,
            english=vocab_by_id[vid].english if vid in vocab_by_id else None,
            miss_count=data["count"],
            student_count=len(data["students"]),
        )
        for vid, data in top_missed
    ]
    category_breakdown = [
        MistakeCategoryBreakdownItem(category=k, count=v)
        for k, v in sorted(category_counts.items(), key=lambda kv: kv[1], reverse=True)
    ]
    most_mistakes_students = sorted(
        (StudentMistakeCount(student_id=s.id, username=s.username, mistake_count=per_student_count[s.id]) for s in students),
        key=lambda x: x.mistake_count,
        reverse=True,
    )[:10]

    return ClassMistakesOverview(
        total_mistakes=len(all_mistakes),
        top_missed_words=top_missed_words,
        category_breakdown=category_breakdown,
        most_mistakes_students=most_mistakes_students,
    )


@router.get("/analytics", response_model=ClassAnalytics)
def get_class_analytics(
    db: Session = Depends(get_db), current_user: User = Depends(require_teacher)
) -> ClassAnalytics:
    students = group_repository.list_students_for_teacher(db, current_user.id)

    units = curriculum_repository.list_units(db)
    all_vocabulary = []
    for unit in units:
        for lesson in curriculum_repository.list_lessons_for_unit(db, unit.id):
            all_vocabulary.extend(curriculum_repository.list_canonical_vocabulary(db, lesson.id))

    active = inactive = new = 0
    total_attempts = 0
    total_mistakes = 0
    mastery_pcts: list[float] = []
    unit_counts: dict[str, int] = {}
    mode_counts: dict[str, int] = {}

    for student in students:
        overview_item = _build_overview_item(db, student)
        if overview_item.status == "ACTIVE":
            active += 1
        elif overview_item.status == "INACTIVE":
            inactive += 1
        else:
            new += 1

        attempts = attempt_repository.list_attempts_for_user(db, student.id)
        total_attempts += len(attempts)
        total_mistakes += len(attempt_repository.list_mistakes_for_user(db, student.id))

        lesson_by_id: dict[uuid.UUID, object] = {}
        for attempt in attempts:
            label = attempt.ui_mode or (attempt.practice_mode.value if attempt.practice_mode else "unknown")
            mode_counts[label] = mode_counts.get(label, 0) + 1
            lesson = lesson_by_id.get(attempt.lesson_id)
            if attempt.lesson_id not in lesson_by_id:
                lesson = curriculum_repository.get_lesson(db, attempt.lesson_id)
                lesson_by_id[attempt.lesson_id] = lesson
            if lesson is not None:
                unit = curriculum_repository.get_unit(db, lesson.unit_id)
                if unit is not None:
                    unit_counts[unit.number] = unit_counts.get(unit.number, 0) + 1

        mastery = vocab_lab_service.word_mastery_for_words(db, student.id, all_vocabulary)
        tracked = [m for m in mastery.values() if m.attempt_count > 0]
        if tracked:
            mastered = len([m for m in tracked if m.status == "MASTERED"])
            mastery_pcts.append(100 * mastered / len(tracked))

    avg_mastery_pct = round(sum(mastery_pcts) / len(mastery_pcts), 1) if mastery_pcts else 0.0
    most_practiced_unit_number = max(unit_counts, key=lambda k: unit_counts[k]) if unit_counts else None
    mode_breakdown = [
        ModeBreakdownItem(ui_mode=k, label=UI_MODE_LABELS.get(k, k), count=v)
        for k, v in sorted(mode_counts.items(), key=lambda kv: kv[1], reverse=True)
    ]

    return ClassAnalytics(
        student_count=len(students),
        active_count=active,
        inactive_count=inactive,
        new_count=new,
        avg_mastery_pct=avg_mastery_pct,
        total_attempts=total_attempts,
        total_mistakes=total_mistakes,
        most_practiced_unit_number=most_practiced_unit_number,
        mode_breakdown=mode_breakdown,
    )
