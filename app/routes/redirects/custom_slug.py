from datetime import datetime, timezone

from app.database.database import get_db
from app.models import Link, User

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


router = APIRouter()

@router.get("/{username}/{custom_slug}")
def redirect_premium_links(username: str, custom_slug: str, db : Session = Depends(get_db)):
    owner_id = db.execute(
        text("""
            SELECT id 
            FROM users 
            WHERE username = :x
        """), {"x": username}
    ).scalar_one_or_none()
    if not owner_id:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Link Not found."
        )
    res = db.execute(
        text("""
            SELECT id, destination_url
            FROM links 
            WHERE 
                owner_id = :x AND 
                custom_slug = :s
                
                """), 
            {
                "x" : owner_id, 
                "s" : custom_slug
                }
                ).one_or_none()

    if res is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Link Not found"
        )

    link_id, url = res

    # Link Not Found
    if not url:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Link Not found."
        )

    # Updating the count of Link
    if link_id:
        try:
            db.execute(
                text("""
                    UPDATE links
                    SET click_count = click_count + 1
                    WHERE id = :id
            """),
            {
                "id":link_id
            }
            )
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise

    return RedirectResponse(
            url=url,
            status_code=status.HTTP_302_FOUND
        )