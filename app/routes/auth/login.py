from app.database.database import get_db
from app.schemas.all_schemas import LoginCred
from app.services.all_services import verify_password
from app.models.user import User

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/auth/login")
def login(data : LoginCred, db: Session =Depends(get_db)):
    query = select(User).where(str(data.email) == User.email)
    user = db.scalar(query)

    if user is None or not verify_password(user.password_hash, data.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password"
        )
    return {"message":"Login Successful"}