# Model imports
from app.models.link import Link

# Service Import
from app.database.database import get_db
from app.services.url_services import generate_short_code

# Pydantic Validation
from app.schemas.url_schema import LinkCreate

from fastapi import APIRouter, Depends
from datetime import timezone, datetime, timedelta

from sqlalchemy.orm import IntegrityError
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/api/links", status_code = 201)
def shorten_url(data: LinkCreate, db : Session = Depends(get_db)):

    for _ in range(5):
        code = generate_short_code()
        link = Link(
            owner_id = None,
            destination_url = str(data.given_url),
            short_code = code,
            custom_slug = None,
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        )
        db.add(link)
        try: 
            db.commit()
        except IntegrityError as exc:
            db.rollback()

            
            

    return {
        "given_url" : str(data.given_url),
        "short_link" : f"http://127.0.0.1:8000/{code}"
    }
    