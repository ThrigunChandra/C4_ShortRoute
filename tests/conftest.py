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
from app.dependencies.rate_limit import limit_link_creation

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

    def skip_rate_limit():
        pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[limit_link_creation] = skip_rate_limit

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(limit_link_creation, None)

@pytest.fixture(autouse=True)
def cache_client(monkeypatch):
    # Every test gets its own Redis keys, separate from the app cache
    from types import SimpleNamespace
    from uuid import uuid4
    from urllib.parse import urlsplit, urlunsplit
    from redis import Redis
    from app.services import link_cache
    from app.config import REDIS_URL

    parts = urlsplit(os.environ.get("TEST_REDIS_URL", REDIS_URL))
    test_redis_url = urlunsplit(parts._replace(path="/1"))
    raw = Redis.from_url(
        test_redis_url, decode_responses=True,
        socket_connect_timeout=1, socket_timeout=1
    )
    prefix = f"test:{uuid4().hex}:"
    keys_used = set()

    def key_for(key):
        full_key = prefix + key
        keys_used.add(full_key)
        return full_key

    cache = SimpleNamespace(
        get=lambda key: raw.get(key_for(key)),
        set=lambda key, value, **kwargs: raw.set(key_for(key), value, **kwargs),
        delete=lambda *keys: raw.delete(*(key_for(key) for key in keys)),
        ttl=lambda key: raw.ttl(key_for(key)),
        exists=lambda key: raw.exists(key_for(key)),
    )
    monkeypatch.setattr(link_cache, "redis_client", cache)
    try:
        yield cache
    finally:
        # Delete only keys used by this test
        try:
            if keys_used:
                raw.delete(*keys_used)
        finally:
            raw.close()
