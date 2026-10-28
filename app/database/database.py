from ..config import DATABASE_URL 

from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, DeclarativeBase

class Base(DeclarativeBase):
    pass

engine = create_engine(
    DATABASE_URL
)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    with SessionLocal() as db:
        yield db