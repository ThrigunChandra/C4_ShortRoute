# I didn't do it Check again 
# 🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.models import Link
from app.services.all_services import generate_short_code
from tests.create_account import create_account


def test_successful_redirect(client, db_session):
    # Visitor links redirect successfully without counting clicks.
    created = client.post(
        "/api/links",
        json={"given_url": "https://example.com"}
    )
    assert created.status_code == 201, created.text
    code = created.json()["short_code"]

    link = db_session.scalar(select(Link).where(Link.short_code == code))
    assert link is not None
    assert link.owner_id is None
    assert link.click_count == 0

    for _ in range(2):
        response = client.get(f"/{code}", follow_redirects=False)
        assert response.status_code == 302, response.text
        assert response.headers["location"] == "https://example.com/"

        db_session.refresh(link)
        assert link.click_count == 0


def test_expired_link(client, db_session):
    now = datetime.now(timezone.utc)
    link = Link(
        destination_url="https://example.com/",
        short_code=generate_short_code(),
        owner_id=None,
        created_at=now - timedelta(days=31),
        expires_at=now - timedelta(days=1),
        click_count=0
    )
    db_session.add(link)
    db_session.commit()

    response = client.get(f"/{link.short_code}", follow_redirects=False)
    assert response.status_code == 410, response.text
    assert response.json()["detail"] == "Link Expired"
    assert "location" not in response.headers

    db_session.refresh(link)
    assert link.click_count == 0


def test_redirect_counts_clicks(client, db_session):
    create_account(client, "redirect_owner")

    created = client.post(
        "/api/links",
        json={"given_url": "https://example.com"}
    )
    assert created.status_code == 201, created.text
    code = created.json()["short_code"]

    link = db_session.scalar(select(Link).where(Link.short_code == code))
    assert link is not None
    assert link.owner_id is not None
    assert link.expires_at is None
    assert link.click_count == 0

    # People clicking an owned link do not need to be logged in.
    logout = client.post("/auth/logout")
    assert logout.status_code == 200, logout.text
    assert client.cookies.get("session_token") is None

    for expected_count in (1, 2):
        response = client.get(f"/{code}", follow_redirects=False)
        assert response.status_code == 302, response.text
        assert response.headers["location"] == "https://example.com/"

        db_session.refresh(link)
        assert link.click_count == expected_count


def test_missing_link(client, db_session):
    code = generate_short_code()
    assert db_session.scalar(
        select(Link).where(Link.short_code == code)
    ) is None

    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Not Found"
    assert "location" not in response.headers
