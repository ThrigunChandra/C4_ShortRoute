from app.database.database import get_db
from app.schemas.all_schemas import LoginCred
from app.services.all_services import verify_password, generate_token, hash_token
from app.models import User, LoginSession

from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, status, Depends, HTTPException, Request, Response
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/auth/login", status_code = status.HTTP_200_OK)
def login(data : LoginCred, request:Request, response: Response, db: Session = Depends(get_db)):
    query = select(User).where(str(data.email) == User.email)
    user = db.scalar(query)

    # Invalid Pass or email
    if user is None or not verify_password(user.password_hash, data.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password"
        )

    now = datetime.now(timezone.utc)
    token = generate_token()

    # Checking for any old sessions
    old_token = request.cookies.get("session_token")

    # If exists then update revoked_at attribs
    # Made a mistake here rectified it 
    if old_token:
        db.execute(
            update(LoginSession)
            .where(
                LoginSession.token_hash == hash_token(old_token), 
                LoginSession.revoked_at.is_(None)
            )
                .values(revoked_at=now)
            )

    # 
    db.add(LoginSession(
        user_id=user.id,
        token_hash=hash_token(token),
        created_at=now,
        expires_at=now+timedelta(days=7)
        ))

    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Well this never happens."
        )

    response.set_cookie( 
        key="session_token", 
        value=token, 
        httponly=True, 
        samesite="lax",
        secure=False,
        max_age=7 * 24 * 60 * 60,
        path="/",
    )

    return {
        "message" : "Login Successful"
        }