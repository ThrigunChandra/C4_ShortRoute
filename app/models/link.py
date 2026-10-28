from sqlalchemy import (
    BigInteger, Column, String, DateTime, Boolean,
    ForeignKey, Identity, Text, text
    )
from sqlalchemy.sql import func 

from app.database.database import Base

class Link(Base):
    __tablename__ = "links"

    id = Column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )

    owner_id = Column(BigInteger, ForeignKey("users.id"))

    destination_url = Column(Text, nullable = False)
    short_code = Column(Text, nullable = False, unique=True)
    custom_slug = Column(String(20))

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    expires_at = Column(
        DateTime(timezone=True)
    )

    is_active = Column(
        Boolean,
        nullable=False,
        server_default=text("true")
    )
    click_count = Column(
        BigInteger, 
        nullable=False,
        server_default=text("0")
    )