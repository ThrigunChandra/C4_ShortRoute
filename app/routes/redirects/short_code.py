from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.link_redirect import get_redirect_url

router = APIRouter()


@router.get("/{short_code}", status_code=status.HTTP_302_FOUND)
def redirect(short_code: str, db: Session = Depends(get_db)):
    url = get_redirect_url(db, short_code=short_code)
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)