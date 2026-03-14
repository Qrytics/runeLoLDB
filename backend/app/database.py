"""Database connection and session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:@localhost:5432/runeloldb",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def get_db():
    """Dependency: yield a DB session and close it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
