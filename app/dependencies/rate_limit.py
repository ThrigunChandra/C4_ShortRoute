from fastapi import Depends, HTTPException, Request
from redis.exceptions import RedisError

from app.dependencies.auth import get_user
from app.models import User
from app.services.rate_limiter import check_rate_limit


def limit_link_creation(
    request: Request,
    user: User | None = Depends(get_user),
):
    # Example limits for a 60-second window
    if user is None:
        ip = request.client.host if request.client else "unknown"
        identity = f"ip:{ip}"
        limit = 5
    else:
        identity = f"user:{user.id}"
        limit = 30 if user.membership_tier == "premium" else 10

    key = f"rate_limit:create_link:{identity}"

    try:
        limited, retry_after = check_rate_limit(
            key=key,
            limit=limit,
            window=60,
        )
    except RedisError as exc:
        raise HTTPException(
            status_code=503,
            detail="Rate limiter unavailable. Please try again.",
        ) from exc

    if limited:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )