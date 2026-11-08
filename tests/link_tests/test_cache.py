import json
from datetime import datetime, timedelta, timezone

from redis.exceptions import ConnectionError
from sqlalchemy import select, event

from app.models import Link, User
from app.services.all_services import generate_short_code
from tests.create_account import create_account


def test_cache_miss(client, db_session, cache_client):
    # First request should get the link from DB and save it in Redis
    created = client.post("/api/links", json={"given_url": "https://example.com"})
    assert created.status_code == 201, created.text
    code = created.json()["short_code"]
    key = f"redirect:code:{code}"
    assert cache_client.get(key) is None

    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 302, response.text
    assert response.headers["location"] == "https://example.com/"

    cached = json.loads(cache_client.get(key))
    assert cached["destination_url"] == "https://example.com/"
    assert cached["owner_id"] is None
    assert 0 < cache_client.ttl(key) <= 300


def test_cache_hit_counts_clicks(client, db_session, cache_client):
    create_account(client, "cache_owner")
    created = client.post("/api/links", json={"given_url": "https://example.com"})
    assert created.status_code == 201, created.text
    code = created.json()["short_code"]
    link = db_session.scalar(select(Link).where(Link.short_code == code))
    assert link is not None

    # First request fills the cache
    first = client.get(f"/{code}", follow_redirects=False)
    assert first.status_code == 302, first.text
    assert cache_client.get(f"redirect:code:{code}") is not None
    db_session.refresh(link)
    assert link.click_count == 1

    # Watch SQL to check the cache hit does not SELECT the destination again
    statements = []
    connection = db_session.get_bind()

    def record_sql(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement.strip().upper())

    event.listen(connection, "before_cursor_execute", record_sql)
    try:
        response = client.get(f"/{code}", follow_redirects=False)
    finally:
        event.remove(connection, "before_cursor_execute", record_sql)

    assert response.status_code == 302, response.text
    assert response.headers["location"] == "https://example.com/"
    assert not any(sql.startswith("SELECT") for sql in statements)
    assert any(sql.startswith("UPDATE") for sql in statements)
    db_session.refresh(link)
    assert link.click_count == 2


def test_cached_visitor_link_no_count(client, db_session, cache_client):
    created = client.post("/api/links", json={"given_url": "https://example.com"})
    assert created.status_code == 201, created.text
    code = created.json()["short_code"]
    link = db_session.scalar(select(Link).where(Link.short_code == code))
    assert link is not None

    for _ in range(2):
        response = client.get(f"/{code}", follow_redirects=False)
        assert response.status_code == 302, response.text
        assert cache_client.get(f"redirect:code:{code}") is not None
        db_session.refresh(link)
        assert link.click_count == 0


def test_expired_cached_link(client, db_session, cache_client):
    now = datetime.now(timezone.utc)
    link = Link(
        destination_url="https://example.com/",
        short_code=generate_short_code(), owner_id=None,
        created_at=now - timedelta(days=31),
        expires_at=now - timedelta(days=1), click_count=0
    )
    db_session.add(link)
    db_session.commit()
    key = f"redirect:code:{link.short_code}"

    # Even if Redis still has it, an expired link must not redirect
    cache_client.set(key, json.dumps({
        "id": link.id, "destination_url": link.destination_url,
        "owner_id": None, "expires_at": link.expires_at.isoformat()
    }), ex=300)
    response = client.get(f"/{link.short_code}", follow_redirects=False)
    assert response.status_code == 410, response.text
    assert cache_client.get(key) is None
    db_session.refresh(link)
    assert link.click_count == 0


def test_delete_clears_both_cached_links(client, db_session, cache_client):
    create_account(client, "cache_premium")
    user = db_session.scalar(select(User).where(User.username == "cache_premium"))
    user.membership_tier = "premium"
    db_session.commit()

    created = client.post("/api/links", json={
        "given_url": "https://example.com", "custom_slug": "portfolio"
    })
    assert created.status_code == 201, created.text
    code = created.json()["short_code"]
    link = db_session.scalar(select(Link).where(Link.short_code == code))
    assert link is not None
    paths = [f"/{code}", "/cache_premium/portfolio"]
    keys = [f"redirect:code:{code}", "redirect:slug:cache_premium:portfolio"]

    # Fill both caches, then use them again
    for _ in range(2):
        for path, key in zip(paths, keys):
            response = client.get(path, follow_redirects=False)
            assert response.status_code == 302, response.text
            assert response.headers["location"] == "https://example.com/"
            assert cache_client.get(key) is not None

    db_session.refresh(link)
    assert link.click_count == 4
    deleted = client.delete(f"/api/links/{link.id}")
    assert deleted.status_code == 204, deleted.text

    for path, key in zip(paths, keys):
        assert cache_client.get(key) is None
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 404, response.text


def test_redis_unavailable(client, db_session, cache_client, monkeypatch):
    create_account(client, "cache_fallback")
    user = db_session.scalar(select(User).where(User.username == "cache_fallback"))
    user.membership_tier = "premium"
    db_session.commit()
    created = client.post("/api/links", json={
        "given_url": "https://example.com", "custom_slug": "portfolio"
    })
    assert created.status_code == 201, created.text
    code = created.json()["short_code"]
    link = db_session.scalar(select(Link).where(Link.short_code == code))

    # Fake a Redis outage, do not stop the actual container
    def unavailable(*args, **kwargs):
        raise ConnectionError("Redis unavailable for this test")

    monkeypatch.setattr(cache_client, "get", unavailable)
    monkeypatch.setattr(cache_client, "set", unavailable)
    monkeypatch.setattr(cache_client, "delete", unavailable)

    for path in (f"/{code}", "/cache_fallback/portfolio"):
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 302, response.text
        assert response.headers["location"] == "https://example.com/"

    db_session.refresh(link)
    assert link.click_count == 2
    deleted = client.delete(f"/api/links/{link.id}")
    assert deleted.status_code == 204, deleted.text


def test_cache_ttl_respects_link_expiry(client, db_session, cache_client):
    now = datetime.now(timezone.utc)
    link = Link(
        destination_url="https://example.com/", short_code=generate_short_code(),
        owner_id=None, created_at=now, expires_at=now + timedelta(seconds=60),
        click_count=0
    )
    db_session.add(link)
    db_session.commit()
    response = client.get(f"/{link.short_code}", follow_redirects=False)
    assert response.status_code == 302, response.text
    assert 0 < cache_client.ttl(f"redirect:code:{link.short_code}") <= 60
