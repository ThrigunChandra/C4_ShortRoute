from datetime import timezone, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.responses import RedirectResponse

from app.database.database import get_db

router = APIRouter()

@router.get("/{short_code}", status_code = status.HTTP_302_FOUND)
def redirect(short_code : str, db:Session = Depends(get_db)):
    # Temporary checking 


    # Checking for shortcode in DB
    res = db.execute(text("SELECT destination_url, expires_at, owner_id from links where short_code = :code"), {"code" : short_code}).fetchone()

    # If returned Nothing 
    if not res:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Not Found"
        )

    # Unpack them if we got result 
    link, expiry, owner_id = res
    now = datetime.now(timezone.utc)

    if expiry is not None and now > expiry:
        raise HTTPException(
            status_code = status.HTTP_410_GONE,
            detail = 'Link Expired'
        )

    if owner_id:
        try:
            db.execute(
                text("""
                    UPDATE links 
                    SET click_count = click_count + 1 
                    WHERE short_code = :code
                """),
                {"code" : short_code}
                )
            db.commit()
        except SQLAlchemyError:
            db.rollback
            raise

    # Everything is good so send the redirect response
    return RedirectResponse(
        url=link,
        status_code=status.HTTP_302_FOUND
    )