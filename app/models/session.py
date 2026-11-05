from sqlalchemy import (BigInteger, Text, DateTime, Column, Identity, CheckConstraint, ForeignKey)
from sqlalchemy import func

from datetime import timedelta

from app.database.database import Base

class LoginSession(Base):
    __tablename__ = "sessions"

    id = Column(
        BigInteger, 
        Identity(always=True),
        primary_key=True
    )
    user_id = Column(
        BigInteger, 
        ForeignKey("users.id"),
        nullable=False
    )
    token_hash = Column(
        Text,
        nullable=False,
        unique=True
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False
    )
    revoked_at = Column(
        DateTime(timezone=True),
        nullable=True
    )