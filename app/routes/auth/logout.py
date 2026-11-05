from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import update
from sqlalchemy.orm import Session 

from app.database.database import get_db
from app.models import LoginSession
from app.services.all_services import hash_token 

router = APIRouter()

@router.post("/auth/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("session_token")

    if token:
        query = (
            update(LoginSession)
            .where(
                LoginSession.token_hash == hash_token(token),
                LoginSession.revoked_at.is_(None)
            )
        ).values(revoked_at=datetime.now(timezone.utc))

        db.execute(query)
        db.commit()

    response.delete_cookie(key="session_token", path="/")

    return {"message":"Logged out"}