from datetime import datetime, timezone, timedelta

from app.database.database import get_db
from app.services.url_services import generate_short_code
from app.schemas.url_schema import LinkResponse, LinkCreate
from app.models.link import Link
from app.models.user import User

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import text

router = APIRouter()

@router.post("/api/links", response_model = LinkResponse, status_code = status.HTTP_201_CREATED)
def shorten_url(data: LinkCreate, db : Session = Depends(get_db)):
    # Short code is created
    code = generate_short_code()
    now = datetime.now(timezone.utc)

    link = Link(
        destination_url = str(data.given_url),
        short_code = code,
        owner_id=None, 
        custom_slug=None,
        created_at=now,
        expires_at=now + timedelta(days=30)
    )

    db.add(link)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise

    return {
        "given_url" : str(data.given_url),
        "short_url" : f"http://127.0.0.1:8000/{code}",
        "short_code": code
    }


@router.get("/{short_code}", status_code = status.HTTP_302_FOUND)
def redirect(short_code : str, db:Session = Depends(get_db)):
    # Temporary checking 
    print("Received Code: ", short_code)

    # Checking for shortcode in DB
    res = db.execute(text("SELECT destination_url, expires_at from links where short_code = :code"), {"code" : short_code}).fetchone()
    print(res)
    # If returned Nothing 
    if not res:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Not Found"
        )

    # Unpack them if we got result 
    link, expiry = res
    now = datetime.now(timezone.utc)

    if expiry is not None and now > expiry:
        raise HTTPException(
            status_code = status.HTTP_410_GONE,
            detail = 'Link Expired'
        )

    # Everything is good so send the redirect response
    return RedirectResponse(
        url=link,
        status_code=status.HTTP_302_FOUND
    )