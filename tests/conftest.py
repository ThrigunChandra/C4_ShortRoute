import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.main import app
from app.database.database import get_db


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

test_url = os.environ["TEST_DATABASE_URL"]

if make_url(test_url).database != "onetwo_test":
    raise RuntimeError("Expected the onetwo_test database")


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(test_url)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    with test_engine.connect() as connection:
        transaction = connection.begin()

        try:
            with Session(
                bind=connection,
                join_transaction_mode="create_savepoint",
            ) as session:
                yield session
        finally:
            transaction.rollback()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)