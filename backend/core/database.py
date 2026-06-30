"""Async SQLAlchemy engine and session factory.

Provides the database engine, session factory, and the ``get_db`` FastAPI
dependency. No models or migrations are defined here.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import settings

# PostgresDsn uses the "postgresql" scheme; asyncpg requires "postgresql+asyncpg".
_db_url = str(settings.DATABASE_URL)
if _db_url.startswith("postgresql://"):
    _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    _db_url,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=5,
    pool_pre_ping=True, # Discard stale connections before use
    echo=False,
    future=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency that yields a transactional AsyncSession."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
