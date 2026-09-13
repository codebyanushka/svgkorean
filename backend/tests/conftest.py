import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app import models  # noqa: F401 - ensure all models are registered on Base
from app.core.config import get_settings
from app.db.base import Base

TEST_DB_NAME = "hangugeo_test"


def _admin_url() -> str:
    base = get_settings().database_url.rsplit("/", 1)[0]
    return f"{base}/postgres"


def _test_db_url() -> str:
    base = get_settings().database_url.rsplit("/", 1)[0]
    return f"{base}/{TEST_DB_NAME}"


@pytest.fixture(scope="session")
def db_engine():
    admin_engine = sa.create_engine(_admin_url(), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.execute(sa.text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"'))
        conn.execute(sa.text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    admin_engine.dispose()

    engine = sa.create_engine(_test_db_url())
    Base.metadata.create_all(engine)

    yield engine

    engine.dispose()
    admin_engine = sa.create_engine(_admin_url(), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.execute(sa.text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"'))
    admin_engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()
