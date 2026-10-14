"""
database.py
-----------
Configures the SQLite database engine and session maker using SQLAlchemy.
Provides a database session dependency for FastAPI routes.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Default SQLite database file in the project root directory
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./students.db")

# SQLite requires check_same_thread=False when used across multiple FastAPI threads
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# SessionLocal is the factory for creating individual database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our SQLAlchemy ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session per request
    and ensures it is properly closed when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
