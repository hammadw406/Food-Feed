"""
Cache service — thin async wrapper over Redis get/set/delete.
All keys are namespaced under "ff:" (food-feed) to avoid collisions.

Degrades gracefully if Redis is unreachable (e.g. local dev without Redis
running) — logs a warning and treats it as a cache miss / no-op rather
than crashing the request. Caching is a performance optimization here,
not a correctness requirement.
"""
from __future__ import annotations

import logging
from typing import Any, Optional
import json

from redis.exceptions import RedisError

from app.redis_client import get_redis_client

logger = logging.getLogger(__name__)

_NS = "ff"  # namespace prefix


def _key(*parts: str) -> str:
    return f"{_NS}:{':'.join(parts)}"


async def cache_get(namespace: str, identifier: str) -> Optional[Any]:
    """
    Retrieve a JSON-serialised value from Redis.
    Returns None on cache miss OR if Redis is unreachable.
    """
    try:
        redis = await get_redis_client()
        raw = await redis.get(_key(namespace, identifier))
    except RedisError as e:
        logger.warning("Redis unavailable, skipping cache_get: %s", e)
        return None
    if raw is None:
        return None
    return json.loads(raw)


async def cache_set(namespace: str, identifier: str, value: Any, ttl: int = 60) -> None:
    """
    Store a JSON-serialisable value in Redis with a TTL (seconds).
    No-ops if Redis is unreachable.
    """
    try:
        redis = await get_redis_client()
        await redis.set(_key(namespace, identifier), json.dumps(value), ex=ttl)
    except RedisError as e:
        logger.warning("Redis unavailable, skipping cache_set: %s", e)


async def cache_delete(namespace: str, identifier: str) -> None:
    """
    Invalidate a single cache entry (e.g. after an event updates the user's feed).
    No-ops if Redis is unreachable.
    """
    try:
        redis = await get_redis_client()
        await redis.delete(_key(namespace, identifier))
    except RedisError as e:
        logger.warning("Redis unavailable, skipping cache_delete: %s", e)