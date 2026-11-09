from datetime import datetime, timezone, timedelta

from app.dependencies.auth import get_user
from app.database.database import get_db
from app.schemas.all_schemas import LinkCreate, LinkResponse
from app.services.all_services import generate_short_code
from app.models import Link, User
from app.dependencies.rate_limit import limit_link_creation

from fastapi import status, Depends, APIRouter, HTTPException

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = APIRouter()

# Creation of Links is from here 
@router.post(
        "/api/links", 
        response_model = LinkResponse, 
        status_code = status.HTTP_201_CREATED,
        dependencies = [Depends(limit_link_creation)]
        )
def shorten_url(data: LinkCreate, db : Session = Depends(get_db), user : User | None = Depends(get_user)):
    # Short code is created
    code = generate_short_code()
    now = datetime.now(timezone.utc)

    if data.custom_slug and user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Please login through a Premium Account"
        )
    if data.custom_slug and user.membership_tier != 'premium':
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Please update to premium to unlock this feature"
        )

    if data.custom_slug:
        existing_link = db.execute(
            select(Link)
            .where(Link.custom_slug == data.custom_slug, Link.owner_id == user.id)
        ).scalar_one_or_none()
        if existing_link:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = "You already have this code."
            )

    link = Link(
        destination_url = str(data.given_url),
        short_code = code,
        owner_id=user.id if user else None, 
        custom_slug=data.custom_slug,
        created_at=now,
        expires_at=None if user else (now + timedelta(days=30))
    )
    

    db.add(link)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        print(exc)
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = 'Failed to create code. Please try again.'
        )

    return {
        "given_url" : str(data.given_url),
        "short_code": code,
        "short_url" : (
            f"http://127.0.0.1:8000/{user.username}/{data.custom_slug}" if data.custom_slug else f"http://127.0.0.1:8000/{code}"
        )
    }