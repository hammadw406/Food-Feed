"""
Cache service — thin async wrapper over Redis get/set/delete.
All keys are namespaced under "ff:" (food-feed) to avoid collisions.
"""

from __future__ import annotations

import json
from typing import Any, Optional

from app.redis_client import get_redis_client


_NS = "ff"  # namespace prefix


def _key(*parts: str) -> str:
    return f"{_NS}:{':'.join(parts)}"


async def cache_get(namespace: str, identifier: str) -> Optional[Any]:
    """
    Retrieve a JSON-serialised value from Redis.
    Returns None on cache miss.
    """
    redis = await get_redis_client()
    raw = await redis.get(_key(namespace, identifier))
    if raw is None:
        return None
    return json.loads(raw)


async def cache_set(namespace: str, identifier: str, value: Any, ttl: int = 60) -> None:
    """
    Store a JSON-serialisable value in Redis with a TTL (seconds).
    """
    redis = await get_redis_client()
    await redis.set(_key(namespace, identifier), json.dumps(value), ex=ttl)


async def cache_delete(namespace: str, identifier: str) -> None:
    """
    Invalidate a single cache entry (e.g. after an event updates the user's feed).
    """
    redis = await get_redis_client()
    await redis.delete(_key(namespace, identifier))
