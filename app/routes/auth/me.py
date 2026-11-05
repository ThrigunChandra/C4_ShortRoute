from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select 
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models import LoginSession, User
from app.services.all_services import hash_token

router = APIRouter()

@router.get("/auth/me")
def get_me(request: Request, db: Session = Depends(get_db)):
    cookie = request.cookies.get("session_token")

    if not cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in"
        )

    query = select(LoginSession).where(
        LoginSession.token_hash == hash_token(cookie),
        LoginSession.revoked_at.is_(None),
        LoginSession.expires_at > datetime.now(timezone.utc)
    )

    login_session = db.scalar(query)

    if login_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    user = db.get(User, login_session.user_id)

    return {
        "id":user.id,
        "username": user.username,
        "email":user.email,
        "membership_tier": user.membership_tier
    }