"""Async Redis client and FastAPI dependency.

A single shared client backed by redis-py's built-in connection pool.
Business logic (caching, sessions, rate limiting) belongs in dedicated modules.
"""

from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from core.config import settings

redis_client: Redis = Redis.from_url(
    str(settings.REDIS_URL),
    decode_responses=True,
    health_check_interval=30,
    auto_close_connection_pool=False,
)


async def get_redis() -> AsyncGenerator[Redis]:
    """FastAPI dependency that yields the shared Redis client."""
    yield redis_client
