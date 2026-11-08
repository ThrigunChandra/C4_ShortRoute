from app.database.database import get_db
from app.dependencies.auth import get_user
from app.models import User, Link

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()

@router.get("/api/links/{link_id}", status_code = status.HTTP_200_OK)
def get_specific_link(link_id : int, db : Session= Depends(get_db), user : User | None  = Depends(get_user)):
    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Please Login"
        )

    link = db.execute(
        select(Link)
        .where(Link.id == link_id, Link.owner_id == user.id)
    ).scalar_one_or_none()

    if link is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Link Not Found"
        )

    return {
        "Link" : link.destination_url,
        "Click Count": link.click_count
    }

