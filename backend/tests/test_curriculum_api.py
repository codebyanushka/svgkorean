"""End-to-end tests for the student/teacher/curation API skeleton.

Runs against the disposable `hangugeo_test` database (see conftest.py) -
creates its own throwaway CANONICAL curriculum rows inside that test DB only,
never touches the dev database or data/verified/.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.session import get_db
from app.main import app
from app.models.activity import AcceptedAnswer, Activity, ActivityOption
from app.models.curriculum import GrammarPoint, Lesson, Unit, Vocabulary
from app.models.enums import ActivityType, CurationStatus
from app.models.group import Group, GroupMember
from app.models.user import Role, User


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    app.dependency_overrides.pop(get_db, None)


def _login(client, username: str, password: str) -> str:
    response = client.post("/api/v1/auth/login", data={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _make_user(db_session, username, password="pw12345", role=Role.STUDENT) -> User:
    user = User(username=username, hashed_password=hash_password(password), role=role)
    db_session.add(user)
    db_session.flush()
    return user


def _make_canonical_lesson(db_session) -> Lesson:
    unit = Unit(number="01", title_ko="1과", title_en="Unit 1")
    db_session.add(unit)
    db_session.flush()
    lesson = Lesson(unit_id=unit.id, title="Lesson 1")
    db_session.add(lesson)
    db_session.flush()
    return lesson


def test_student_units_and_lessons_visible(client, db_session):
    _make_user(db_session, "anna")
    _make_canonical_lesson(db_session)
    db_session.commit()

    token = _login(client, "anna", "pw12345")
    response = client.get("/api/v1/student/units", headers=_auth_headers(token))

    assert response.status_code == 200
    assert response.json()[0]["number"] == "01"


def test_student_lesson_detail_only_shows_canonical_rows(client, db_session):
    _make_user(db_session, "anna")
    lesson = _make_canonical_lesson(db_session)
    db_session.add_all(
        [
            Vocabulary(lesson_id=lesson.id, korean="안나", english="Anna", curation_status=CurationStatus.CANONICAL),
            Vocabulary(lesson_id=lesson.id, korean="draft", english="draft", curation_status=CurationStatus.DRAFT),
            GrammarPoint(
                lesson_id=lesson.id,
                name_ko="이에요/예요",
                name_en="to be",
                curation_status=CurationStatus.CANONICAL,
            ),
        ]
    )
    db_session.commit()

    token = _login(client, "anna", "pw12345")
    response = client.get(f"/api/v1/student/lessons/{lesson.id}", headers=_auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert [v["korean"] for v in body["vocabulary"]] == ["안나"]
    assert body["grammar_points"][0]["name_ko"] == "이에요/예요"


def test_teacher_cannot_access_student_routes(client, db_session):
    _make_user(db_session, "mr_kim", role=Role.TEACHER)
    db_session.commit()

    token = _login(client, "mr_kim", "pw12345")
    response = client.get("/api/v1/student/units", headers=_auth_headers(token))

    assert response.status_code == 403


def test_submit_attempt_grades_and_updates_progress(client, db_session):
    student = _make_user(db_session, "anna")
    lesson = _make_canonical_lesson(db_session)
    activity = Activity(
        lesson_id=lesson.id,
        type=ActivityType.MULTIPLE_CHOICE,
        prompt="저는 안나___.",
        curation_status=CurationStatus.CANONICAL,
    )
    db_session.add(activity)
    db_session.flush()
    db_session.add(ActivityOption(activity_id=activity.id, text="이에요", is_correct=True))
    db_session.add(ActivityOption(activity_id=activity.id, text="예요", is_correct=False))
    db_session.commit()

    token = _login(client, "anna", "pw12345")
    headers = _auth_headers(token)

    correct = client.post(
        "/api/v1/student/attempts",
        headers=headers,
        json={"activity_id": str(activity.id), "submitted_answer": "이에요"},
    )
    assert correct.status_code == 200, correct.text
    assert correct.json()["is_correct"] is True
    assert correct.json()["attempt_number"] == 1

    wrong = client.post(
        "/api/v1/student/attempts",
        headers=headers,
        json={"activity_id": str(activity.id), "submitted_answer": "예요"},
    )
    assert wrong.status_code == 200
    assert wrong.json()["is_correct"] is False
    assert wrong.json()["attempt_number"] == 2

    progress = client.get("/api/v1/student/progress", headers=headers)
    assert progress.status_code == 200
    assert len(progress.json()) == 1

    mistakes_check = client.get("/api/v1/teacher/students", headers=headers)
    assert mistakes_check.status_code == 403  # student, not teacher


def test_ungradable_activity_returns_422(client, db_session):
    _make_user(db_session, "anna")
    lesson = _make_canonical_lesson(db_session)
    activity = Activity(
        lesson_id=lesson.id,
        type=ActivityType.SPEAKING,
        prompt="Say hello",
        curation_status=CurationStatus.CANONICAL,
    )
    db_session.add(activity)
    db_session.commit()

    token = _login(client, "anna", "pw12345")
    response = client.post(
        "/api/v1/student/attempts",
        headers=_auth_headers(token),
        json={"activity_id": str(activity.id), "submitted_answer": "hello"},
    )

    assert response.status_code == 422


def test_teacher_sees_only_assigned_students(client, db_session):
    teacher = _make_user(db_session, "mr_kim", role=Role.TEACHER)
    other_teacher = _make_user(db_session, "ms_lee", role=Role.TEACHER)
    student_in_group = _make_user(db_session, "anna")
    student_not_in_group = _make_user(db_session, "bob")

    group = Group(name="Class A", teacher_id=teacher.id)
    other_group = Group(name="Class B", teacher_id=other_teacher.id)
    db_session.add_all([group, other_group])
    db_session.flush()
    db_session.add(GroupMember(group_id=group.id, user_id=student_in_group.id))
    db_session.add(GroupMember(group_id=other_group.id, user_id=student_not_in_group.id))
    db_session.commit()

    token = _login(client, "mr_kim", "pw12345")
    headers = _auth_headers(token)

    response = client.get("/api/v1/teacher/students", headers=headers)
    assert response.status_code == 200
    usernames = {s["username"] for s in response.json()}
    assert usernames == {"anna"}

    forbidden = client.get(f"/api/v1/teacher/students/{student_not_in_group.id}/progress", headers=headers)
    assert forbidden.status_code == 403

    allowed = client.get(f"/api/v1/teacher/students/{student_in_group.id}/progress", headers=headers)
    assert allowed.status_code == 200


def test_curation_workflow_draft_to_canonical(client, db_session):
    admin = _make_user(db_session, "root_admin", role=Role.ADMIN)
    lesson = _make_canonical_lesson(db_session)
    vocab = Vocabulary(lesson_id=lesson.id, korean="안나", english="Anna", curation_status=CurationStatus.DRAFT)
    db_session.add(vocab)
    db_session.commit()

    token = _login(client, "root_admin", "pw12345")
    headers = _auth_headers(token)

    queue = client.get("/api/v1/curation/vocabulary", headers=headers)
    assert queue.status_code == 200
    assert len(queue.json()) == 1

    approve = client.post(
        f"/api/v1/curation/vocabulary/{vocab.id}/transition",
        headers=headers,
        json={"to_status": "HUMAN_APPROVED"},
    )
    assert approve.status_code == 200
    assert approve.json()["curation_status"] == "HUMAN_APPROVED"
    assert approve.json()["reviewed_by"] == "root_admin"

    publish = client.post(
        f"/api/v1/curation/vocabulary/{vocab.id}/transition",
        headers=headers,
        json={"to_status": "CANONICAL"},
    )
    assert publish.status_code == 200
    assert publish.json()["curation_status"] == "CANONICAL"

    # Illegal transition: CANONICAL cannot jump straight to HUMAN_APPROVED again
    illegal = client.post(
        f"/api/v1/curation/vocabulary/{vocab.id}/transition",
        headers=headers,
        json={"to_status": "HUMAN_APPROVED"},
    )
    assert illegal.status_code == 400


def test_curation_requires_staff_role(client, db_session):
    _make_user(db_session, "anna")
    db_session.commit()

    token = _login(client, "anna", "pw12345")
    response = client.get("/api/v1/curation/vocabulary", headers=_auth_headers(token))

    assert response.status_code == 403
