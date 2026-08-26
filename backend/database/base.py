"""
SQLAlchemy declarative base for the application.

All ORM models inherit from Base so SQLAlchemy can discover
and manage their database table definitions.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    """

    pass