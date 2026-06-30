import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from core.config import settings

# ---------------------------------------------------------------------------
# Alembic config object — provides access to alembic.ini values.
# ---------------------------------------------------------------------------
config = context.config

# Wire up Python logging from alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Override the URL from alembic.ini with the value from application settings.
# asyncpg requires the "postgresql+asyncpg" scheme.
# ---------------------------------------------------------------------------
_db_url = str(settings.DATABASE_URL)
if _db_url.startswith("postgresql://"):
    _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

config.set_main_option("sqlalchemy.url", _db_url)

# ---------------------------------------------------------------------------
# Target metadata for autogenerate.
# Import and set Base.metadata here once models exist, e.g.:
#   from app.models import Base
#   target_metadata = Base.metadata
# ---------------------------------------------------------------------------
target_metadata = None


# ---------------------------------------------------------------------------
# Offline mode — emits SQL to stdout without a live DB connection.
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Generate SQL scripts without connecting to the database."""
    context.configure(
        url=_db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online mode — runs migrations against a live async connection.
# ---------------------------------------------------------------------------
def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations using an async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
