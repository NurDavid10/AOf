"""
Database connection and session management.

This module sets up the SQLAlchemy engine, session factory, and provides
utilities for database connections using context managers.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from app.config import get_settings

# Get settings
settings = get_settings()

# Construct database URL
DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False           # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.

    Yields:
        Session: SQLAlchemy database session

    Note:
        This generator ensures the session is closed after use,
        even if an exception occurs.

    Example:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions outside of FastAPI routes.

    Yields:
        Session: SQLAlchemy database session

    Example:
        with get_db_context() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.

    This function creates all tables defined in the ORM models.
    It should be called when setting up the database for the first time.

    Note:
        Make sure all models are imported before calling this function
        so that they are registered with Base.metadata
    """
    from app.models import user, course, task, payment, queue, expense, maintenance_task
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all database tables.

    Warning:
        This will delete all data in the database!
        Use with caution, typically only in development/testing.
    """
    Base.metadata.drop_all(bind=engine)
