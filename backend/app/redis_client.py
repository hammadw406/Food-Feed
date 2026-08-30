"""
Async Redis client — single shared connection pool for the whole app.
"""

from __future__ import annotations

import redis.asyncio as aioredis
from app.config import settings

_redis_client: aioredis.Redis | None = None


async def get_redis_client() -> aioredis.Redis:
    """
    Returns the shared Redis client, creating it if it doesn't exist yet.
    Called once at startup (lifespan) and also available as a FastAPI dependency.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client
