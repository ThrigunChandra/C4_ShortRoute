from app.models import User, Link
from app.database.database import get_db
from app.dependencies.auth import get_user

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/api/links", status_code = status.HTTP_200_OK)
def get_all_links(db:Session = Depends(get_db), user: User | None = Depends(get_user)):
    # What will user return ?? 
    # User row ?? 
    # Need user_id to get links associated with that user 
    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Please log in"
        )
    
    links = db.execute(
        select(Link)
        .where(Link.owner_id == user.id)
        .order_by(Link.created_at.desc())
    ).scalars().all()

    return [
        {
            "id" : link.id,
            "destination_url" : link.destination_url,
            "short_code" : link.short_code,
            "created_at" : link.created_at,
            "click_count" : link.click_count
        }
        for link in links
    ]