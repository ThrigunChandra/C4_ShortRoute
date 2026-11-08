from sqlalchemy import select

from app.models import Link, User
from tests.create_account import create_account


def test_visitor_with_custom_slug(client):
    # No account, just trying to create a custom link
    response = client.post(
        "/api/links",
        json={"given_url": "https://example.com", "custom_slug": "portfolio"}
    )
    assert response.status_code == 401, response.text


def test_free_user_with_custom_slug(client):
    # Free user should not get this feature
    create_account(client, "slug_free")
    response = client.post(
        "/api/links",
        json={"given_url": "https://example.com", "custom_slug": "portfolio"}
    )
    assert response.status_code == 403, response.text


def test_premium_user_with_custom_slug(client, db_session):
    create_account(client, "slug_premium")

    # Make this user premium for the test
    user = db_session.scalar(select(User).where(User.username == "slug_premium"))
    assert user is not None
    user.membership_tier = "premium"
    db_session.commit()

    response = client.post(
        "/api/links",
        json={"given_url": "https://example.com", "custom_slug": "portfolio"}
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["short_url"] == "http://127.0.0.1:8000/slug_premium/portfolio"
    assert len(body["short_code"]) == 8

    # Check what actually got saved
    link = db_session.scalar(select(Link).where(Link.short_code == body["short_code"]))
    assert link is not None
    assert link.owner_id == user.id
    assert link.custom_slug == "portfolio"
    assert link.expires_at is None


def test_same_user_same_slug(client, db_session):
    create_account(client, "slug_duplicate")
    user = db_session.scalar(select(User).where(User.username == "slug_duplicate"))
    assert user is not None
    user.membership_tier = "premium"
    db_session.commit()

    data = {"given_url": "https://example.com", "custom_slug": "portfolio"}
    first = client.post("/api/links", json=data)
    assert first.status_code == 201, first.text

    # Same user trying the same slug again
    second = client.post("/api/links", json=data)
    assert second.status_code == 409, second.text

    links = db_session.scalars(
        select(Link).where(Link.owner_id == user.id, Link.custom_slug == "portfolio")
    ).all()
    assert len(links) == 1


def test_different_users_same_slug(client, db_session):
    # Both users can have portfolio, their usernames make the URLs different
    for username in ("slug_user_a", "slug_user_b"):
        create_account(client, username)
        user = db_session.scalar(select(User).where(User.username == username))
        assert user is not None
        user.membership_tier = "premium"
        db_session.commit()

        response = client.post(
            "/api/links",
            json={"given_url": "https://example.com", "custom_slug": "portfolio"}
        )
        assert response.status_code == 201, response.text
        assert response.json()["short_url"] == f"http://127.0.0.1:8000/{username}/portfolio"

        logout = client.post("/auth/logout")
        assert logout.status_code == 200, logout.text


def test_invalid_custom_slug(client, db_session):
    create_account(client, "slug_invalid")
    user = db_session.scalar(select(User).where(User.username == "slug_invalid"))
    assert user is not None
    user.membership_tier = "premium"
    db_session.commit()

    # Spaces and special characters are not allowed
    response = client.post(
        "/api/links",
        json={"given_url": "https://example.com", "custom_slug": "my slug!"}
    )
    assert response.status_code == 422, response.text


def test_custom_slug_redirect(client, db_session):
    create_account(client, "slug_redirect")
    user = db_session.scalar(select(User).where(User.username == "slug_redirect"))
    assert user is not None
    user.membership_tier = "premium"
    db_session.commit()

    created = client.post(
        "/api/links",
        json={"given_url": "https://example.com", "custom_slug": "portfolio"}
    )
    assert created.status_code == 201, created.text
    link = db_session.scalar(
        select(Link).where(Link.short_code == created.json()["short_code"])
    )
    assert link is not None
    assert link.click_count == 0

    # Anyone can open the link, no login needed
    logout = client.post("/auth/logout")
    assert logout.status_code == 200, logout.text
    assert client.cookies.get("session_token") is None

    for count in (1, 2):
        response = client.get("/slug_redirect/portfolio", follow_redirects=False)
        assert response.status_code == 302, response.text
        assert response.headers["location"] == "https://example.com/"
        db_session.refresh(link)
        assert link.click_count == count


def test_custom_slug_unknown_user(client, db_session):
    # Username itself does not exist
    assert db_session.scalar(
        select(User).where(User.username == "slug_missing")
    ) is None
    response = client.get("/slug_missing/portfolio", follow_redirects=False)
    assert response.status_code == 404, response.text


def test_custom_slug_unknown_slug(client):
    # User exists but this slug does not
    create_account(client, "slug_no_links")
    logout = client.post("/auth/logout")
    assert logout.status_code == 200, logout.text

    response = client.get("/slug_no_links/missing", follow_redirects=False)
    assert response.status_code == 404, response.text
