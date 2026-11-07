from datetime import timezone, datetime

from fastapi import Request, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LoginSession, User
from app.database.database import get_db 
from app.services.all_services import hash_token

def get_user(request:Request, db:Session = Depends(get_db)):
    # Getting time now to check expired or not 
    now = datetime.now(timezone.utc)

    # Get the token to check exist's or not 
    token = request.cookies.get("session_token")
    # If not exists return None
    if not token:
        return None

    # query to find the session where revoked is None and expiry > now 
    query = db.execute(
        select(LoginSession)
        .where(
            LoginSession.token_hash == hash_token(token), 
            LoginSession.revoked_at.is_(None), 
            LoginSession.expires_at > now
            )
    ).scalar_one_or_none()

    if not query:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Session expired."
        )

    user = db.get(User, query.user_id)

    if user is None:
        raise HTTPException(
            status_code = 401, 
            detail = 'Invalid Session'
        )

    return user