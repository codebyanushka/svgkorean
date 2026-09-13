"""Tests for JWT auth: login, current-user resolution, and role guards.

Runs against the disposable `hangugeo_test` database via the `db_session`
fixture (see conftest.py) - never the dev `hangugeo` database.
"""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.session import get_db
from app.main import app
from app.models.user import Role, User


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    app.dependency_overrides.pop(get_db, None)


def _make_user(db_session, username="anna", password="pw12345", role=Role.STUDENT) -> User:
    user = User(username=username, hashed_password=hash_password(password), role=role)
    db_session.add(user)
    db_session.flush()
    return user


def test_login_success_returns_jwt(client, db_session):
    _make_user(db_session, username="anna", password="pw12345")
    db_session.commit()

    response = client.post("/api/v1/auth/login", data={"username": "anna", "password": "pw12345"})

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_rejected(client, db_session):
    _make_user(db_session, username="anna", password="pw12345")
    db_session.commit()

    response = client.post("/api/v1/auth/login", data={"username": "anna", "password": "wrong"})

    assert response.status_code == 401


def test_login_unknown_user_rejected(client):
    response = client.post("/api/v1/auth/login", data={"username": "ghost", "password": "x"})

    assert response.status_code == 401


def test_current_user_resolved_from_token(client, db_session):
    _make_user(db_session, username="anna", password="pw12345", role=Role.TEACHER)
    db_session.commit()

    token = client.post("/api/v1/auth/login", data={"username": "anna", "password": "pw12345"}).json()["access_token"]
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"username": "anna", "role": "TEACHER", "id": response.json()["id"]}


def test_current_user_rejects_missing_token(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_current_user_rejects_garbage_token(client):
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer garbage.token.value"})

    assert response.status_code == 401


def test_role_guard_allows_matching_role():
    from app.api.deps import require_roles

    student = User(username="s", hashed_password="x", role=Role.STUDENT)
    checker = require_roles(Role.STUDENT)

    assert checker(current_user=student) is student


def test_role_guard_rejects_wrong_role():
    from app.api.deps import require_roles

    checker = require_roles(Role.STUDENT)
    teacher = User(username="t", hashed_password="x", role=Role.TEACHER)

    with pytest.raises(HTTPException) as exc_info:
        checker(current_user=teacher)

    assert exc_info.value.status_code == 403
