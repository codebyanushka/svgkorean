"""Tests for the language-aware vocabulary search endpoint
(GET /api/v1/student/vocab-lab/search) - see
curriculum_repository.search_canonical_vocabulary()/_is_korean_query().

Runs against the disposable `hangugeo_test` database (see conftest.py).
"""

import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.session import get_db
from app.main import app
from app.models.curriculum import Lesson, Unit, Vocabulary
from app.models.enums import CurationStatus
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


def _make_student(db_session, username="anna", password="pw12345") -> User:
    user = User(username=username, hashed_password=hash_password(password), role=Role.STUDENT)
    db_session.add(user)
    db_session.flush()
    return user


def _make_lesson(db_session) -> Lesson:
    unit = Unit(number="01", title_ko="1과", title_en="Unit 1")
    db_session.add(unit)
    db_session.flush()
    lesson = Lesson(unit_id=unit.id, title="Lesson 1")
    db_session.add(lesson)
    db_session.flush()
    return lesson


def _seed_words(db_session, lesson):
    db_session.add_all(
        [
            Vocabulary(lesson_id=lesson.id, korean="한국", english="Korea", romanization="hanguk", curation_status=CurationStatus.CANONICAL),
            Vocabulary(lesson_id=lesson.id, korean="사람", english="person", romanization="saram", curation_status=CurationStatus.CANONICAL),
            Vocabulary(lesson_id=lesson.id, korean="한복", english="Hanbok", romanization="hanbok", curation_status=CurationStatus.CANONICAL),
        ]
    )


def _search(client, token, query):
    return client.get("/api/v1/student/vocab-lab/search", params={"q": query}, headers=_auth_headers(token))


def test_english_exact_search_matches_only_english_field(client, db_session):
    _make_student(db_session)
    lesson = _make_lesson(db_session)
    _seed_words(db_session, lesson)
    db_session.commit()

    token = _login(client, "anna", "pw12345")
    response = _search(client, token, "Korea")

    assert response.status_code == 200
    results = response.json()
    assert [r["korean"] for r in results] == ["한국"]


def test_english_partial_search_matches_substring(client, db_session):
    _make_student(db_session)
    lesson = _make_lesson(db_session)
    _seed_words(db_session, lesson)
    db_session.commit()

    token = _login(client, "anna", "pw12345")
    response = _search(client, token, "Kor")

    assert response.status_code == 200
    results = response.json()
    assert [r["korean"] for r in results] == ["한국"]


def test_korean_exact_search_matches_only_korean_field(client, db_session):
    _make_student(db_session)
    lesson = _make_lesson(db_session)
    _seed_words(db_session, lesson)
    db_session.commit()

    token = _login(client, "anna", "pw12345")
    response = _search(client, token, "사람")

    assert response.status_code == 200
    results = response.json()
    assert [r["english"] for r in results] == ["person"]


def test_korean_partial_search_matches_substring(client, db_session):
    _make_student(db_session)
    lesson = _make_lesson(db_session)
    _seed_words(db_session, lesson)
    db_session.commit()

    token = _login(client, "anna", "pw12345")
    response = _search(client, token, "한")

    assert response.status_code == 200
    results = response.json()
    assert {r["korean"] for r in results} == {"한국", "한복"}


def test_no_cross_language_false_matches(client, db_session):
    """An English query must never match korean/romanization, and a Korean
    query must never match english - even when the romanization field would
    otherwise coincidentally contain the query text."""
    _make_student(db_session)
    lesson = _make_lesson(db_session)
    _seed_words(db_session, lesson)
    db_session.commit()

    token = _login(client, "anna", "pw12345")

    # "hanguk" is the romanization of 한국, but romanization is never
    # searched - an English-script query for it should match nothing.
    response = _search(client, token, "hanguk")
    assert response.status_code == 200
    assert response.json() == []

    # A Korean-script query must not match the English "person" field.
    response = _search(client, token, "사람이 아닌")
    assert response.status_code == 200
    assert response.json() == []
