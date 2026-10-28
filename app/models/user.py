from sqlalchemy import (BigInteger, Text, String, Column, Identity, text, DateTime)
from sqlalchemy.sql import func


from app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(
        BigInteger, 
        Identity(always=True),
        primary_key=True
    )
    email = Column(
        Text, 
        unique=True,
        nullable=False
    )
    username = Column(
        String(20),
        unique=True,
        nullable=False,
    )

    password_hash = Column(
        Text, 
        nullable=False
    )

    membership_tier = Column(
        Text, 
        nullable=False,
        server_default=text("'free'")
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )