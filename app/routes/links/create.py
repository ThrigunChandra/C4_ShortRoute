from datetime import datetime, timezone, timedelta

from app.dependencies.auth import get_user
from app.database.database import get_db
from app.schemas.all_schemas import LinkCreate, LinkResponse
from app.services.all_services import generate_short_code
from app.models import Link, User

from fastapi import status, Depends, APIRouter, HTTPException

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = APIRouter()

# Creation of Links is from here 
@router.post("/api/links", response_model = LinkResponse, status_code = status.HTTP_201_CREATED)
def shorten_url(data: LinkCreate, db : Session = Depends(get_db), user : User = Depends(get_user)):
    # Short code is created
    code = generate_short_code()
    now = datetime.now(timezone.utc)

    link = Link(
        destination_url = str(data.given_url),
        short_code = code,
        owner_id=user.id if user else None, 
        custom_slug=None,
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
        "short_url" : f"http://127.0.0.1:8000/{code}",
        "short_code": code
    }