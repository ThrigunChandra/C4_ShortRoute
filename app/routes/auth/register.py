from datetime import datetime, timezone

from app.database.database import get_db
from app.models.user import User
from app.schemas.all_schemas import UserCreate
from app.services.all_services import hash_password

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status 

router = APIRouter()

@router.post("/api/register", status_code = status.HTTP_201_CREATED)
def user_register(data:UserCreate, db:Session = Depends(get_db)):
    user = User(
        email = str(data.email), 
        username = data.username,
        password_hash = hash_password(data.password)
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        messages = {
            "users_email_key": "Email is already registered",
            "users_username_key": "Username is already taken",
        }

        constraint = exc.orig.diag.constraint_name 

        if constraint in messages :
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = messages[constraint]
            ) from exc
        else:
            raise

    return {
        "Message" : f"User: {data.username} \nCreated Successfully"
    }

    