import backend.models  # noqa: F401
"""
Database configuration and session management.

This module creates the SQLAlchemy engine, session factory,
and database initialization functionality.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.core.config import settings
from backend.database.base import Base


# ------------------------------------------------------------
# Database Engine
# ------------------------------------------------------------

connect_args = {}

if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}


engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)


# ------------------------------------------------------------
# Session Factory
# ------------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ------------------------------------------------------------
# Database Session Dependency
# ------------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session for application operations.

    The session is automatically closed after the operation
    completes.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ------------------------------------------------------------
# Database Initialization
# ------------------------------------------------------------

def init_db() -> None:
    """
    Create all registered database tables.

    Tables are created only when they do not already exist.
    """

    Base.metadata.create_all(bind=engine)