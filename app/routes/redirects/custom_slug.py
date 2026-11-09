from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.link_redirect import get_redirect_url

router = APIRouter()


@router.get("/{username}/{custom_slug}", status_code=status.HTTP_302_FOUND)
def redirect_premium_links(
    username: str,
    custom_slug: str,
    db: Session = Depends(get_db),
):
    url = get_redirect_url(
        db,
        username=username,
        custom_slug=custom_slug,
    )
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)