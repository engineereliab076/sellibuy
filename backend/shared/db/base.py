"""Shared SQLAlchemy declarative base.

All ORM models across every domain inherit from ``Base``.
Alembic reads ``Base.metadata`` to detect schema changes.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
