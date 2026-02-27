"""
Database configuration and session management for Nyaya Mitra.

This module sets up SQLAlchemy with PostgreSQL connection, provides
the Base model class with common fields, and implements database
session management with context managers.

Requirements: 9.3 (Data encryption at rest), 9.5 (Account deletion)
"""

from contextlib import contextmanager
from datetime import datetime
from typing import Generator
from uuid import uuid4

from sqlalchemy import Column, DateTime, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    database_url: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env file


# Load settings
settings = Settings()

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Maximum overflow connections
    echo=False,  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create declarative base
Base = declarative_base()


class BaseModel(Base):
    """
    Base model class with common fields for all database models.
    
    Provides:
    - id: UUID primary key
    - created_at: Timestamp of record creation
    - updated_at: Timestamp of last update
    
    All models should inherit from this class to ensure consistent
    field naming and behavior across the application.
    """
    
    __abstract__ = True
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
        index=True
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Provides automatic session management with proper cleanup:
    - Creates a new session
    - Yields the session for use
    - Commits on success
    - Rolls back on error
    - Always closes the session
    
    Usage:
        with get_db() as db:
            user = db.query(User).first()
            # ... perform database operations
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI endpoints.
    
    Provides a database session that is automatically cleaned up
    after the request completes. Use with FastAPI's Depends().
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db_session)):
            return db.query(User).all()
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This function should be called on application startup to ensure
    all database tables exist. It's idempotent - safe to call multiple times.
    
    Note: In production, use Alembic migrations instead of this function.
    """
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all database tables.
    
    WARNING: This will delete all data! Only use in development/testing.
    """
    Base.metadata.drop_all(bind=engine)
