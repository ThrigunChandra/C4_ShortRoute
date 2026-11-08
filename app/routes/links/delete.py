from app.database.database import get_db
from app.dependencies.auth import get_user
from app.models import Link, User

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.services.link_cache import delete_cached_links

router = APIRouter()

@router.delete("/api/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link_by_id(link_id: int, db : Session = Depends(get_db), user : User | None = Depends(get_user)):
    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Please Login"
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
    keys = [f"redirect:code:{link.short_code}"]

    if link.custom_slug is not None:
        keys.append(f"redirect:slug:{user.username}:{link.custom_slug}")

    db.delete(link)
    db.commit()

    delete_cached_links(*keys)

    return Response(status_code = status.HTTP_204_NO_CONTENT)