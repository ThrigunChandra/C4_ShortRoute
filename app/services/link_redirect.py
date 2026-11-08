from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Link, User
from app.services.link_cache import (
    get_cached_link,
    cache_link,
    delete_cached_links,
)


def get_redirect_url(
    db: Session,
    short_code: str | None = None,
    username: str | None = None,
    custom_slug: str | None = None,
) -> str:
    if short_code is not None:
        key = f"redirect:code:{short_code}"
    else:
        key = f"redirect:slug:{username}:{custom_slug}"

    # First check Redis
    data = get_cached_link(key)
    cache_miss = data is None

    if cache_miss:
        # Not cached, get it from PostgreSQL
        if short_code is not None:
            query = select(Link).where(Link.short_code == short_code)
        else:
            query = (
                select(Link)
                .join(User, Link.owner_id == User.id)
                .where(
                    User.username == username,
                    Link.custom_slug == custom_slug,
                )
            )

        link = db.execute(query).scalar_one_or_none()

        if link is None:
            raise HTTPException(status_code=404, detail="Not Found")

        data = {
            "id": link.id,
            "destination_url": link.destination_url,
            "owner_id": link.owner_id,
            "expires_at": (
                link.expires_at.isoformat()
                if link.expires_at is not None
                else None
            ),
        }

    # Visitor links can expire, even when found in Redis
    ttl = 300

    if data["expires_at"] is not None:
        expiry = datetime.fromisoformat(data["expires_at"])
        remaining = (expiry - datetime.now(timezone.utc)).total_seconds()

        if remaining <= 0:
            delete_cached_links(key)
            raise HTTPException(status_code=410, detail="Link Expired")

        ttl = min(ttl, int(remaining))

    # Save valid links on a cache miss
    if cache_miss and ttl > 0:
        cache_link(key, data, ttl=ttl)

    # Count owned links on BOTH cache hits and misses
    if data["owner_id"] is not None:
        try:
            updated_id = db.execute(
                update(Link)
                .where(Link.id == data["id"])
                .values(click_count=Link.click_count + 1)
                .returning(Link.id)
            ).scalar_one_or_none()

            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise

        # The link might have been deleted while still cached
        if updated_id is None:
            delete_cached_links(key)
            raise HTTPException(status_code=404, detail="Not Found")

    return data["destination_url"]