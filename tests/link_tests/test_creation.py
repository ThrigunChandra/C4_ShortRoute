from sqlalchemy import select
from app.models import Link
from datetime import datetime, timezone

def test_link_with_cookie(client, db_session):
    account = {
        "email" : "test_user@gmail.com",
        "username" : "test_user",
        "password" : "test_user"
    }
    # Send the request 
    register = client.post(
        "/auth/register",
        json = account
    )

    assert register.status_code == 201, register.text 
    assert register.json()["Message"] == "test_user Created Successfully."

    # Login 
    login = client.post(
        "/auth/login",
        json = {
            "email":account["email"],
            "password":account["password"]
        }
    )

    assert login.status_code == 200, login.text

    token = client.cookies.get("session_token")

    # Create A link
    create_link = client.post(
        "/api/links",
        json = {
            "given_url" : "https://www.instagram.com"
        }
    )

    body = create_link.json()

    assert create_link.status_code == 201, create_link.text 

    # It created a link need to check expiry is None
    # things there ?? Short_code 

    link = db_session.execute(
        select(Link)
        .where(Link.short_code == body["short_code"], Link.expires_at.is_(None))
    ).scalar_one_or_none()

    assert link

def test_with_no_cookie(client, db_session):
    now = datetime.now(timezone.utc)

    response = client.post(
        "/api/links", 
        json = {
            "given_url" : "https://www.instagram.com"
        }
        )

    assert response.status_code ==201, response.text

    body = response.json()

    link = db_session.execute(
        select(Link)
        .where(Link.short_code == body["short_code"])
    ).scalar_one_or_none()

    # Check there is a link with that short_code
    assert link
    assert link.destination_url == "https://www.instagram.com/"

    assert link.expires_at is not None

    
    