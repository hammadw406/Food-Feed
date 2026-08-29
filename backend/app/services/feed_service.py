"""
Feed service — builds the list of restaurants returned by GET /feed.

Current strategy (pre-ML):
  1. Check Redis cache for this user's feed.
  2. On miss:
     a. If the user has an embedding (Person 3 has set it) → placeholder for
        vector nearest-neighbor query (returns popular fallback for now).
     b. Cold-start (no embedding) → diverse sample: sort by rating DESC,
        with a small random shuffle to surface variety.
  3. Cache the result for FEED_CACHE_TTL seconds.
  4. Invalidate cache key whenever a new event is logged for this user.

NOTE: Steps 2a's real vector search will be wired in by Person 3.
The hook is clearly marked with # TODO(ml).
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.restaurant import Restaurant
from app.schemas.feed import FeedItem, FeedResponse
from app.services.cache_service import cache_get, cache_set

_CACHE_NS = "feed"


async def build_feed(
    db: AsyncSession,
    user_id: Optional[uuid.UUID],
    limit: int = 20,
    offset: int = 0,
) -> FeedResponse:
    """
    Build and return a personalised feed for `user_id`.

    Falls back to popular/diverse sampling when the user has no embedding.
    """
    cache_key = f"{user_id}:{limit}:{offset}"

    # ------------------------------------------------------------------ cache
    cached = await cache_get(_CACHE_NS, cache_key)
    if cached:
        return FeedResponse(**cached)

    # -------------------------------------------------------- check embedding
    is_cold_start = True
    # TODO(ml — Person 3): Replace this block with a pgvector ANN query.
    # When User.embedding is not NULL, query:
    #   SELECT * FROM restaurants
    #   ORDER BY embedding <=> :user_embedding
    #   LIMIT :limit OFFSET :offset
    # and set is_cold_start = False.

    # -------------------------------------------------- cold-start / popular
    stmt = (
        select(Restaurant)
        .where(Restaurant.embedding.is_(None) | Restaurant.embedding.isnot(None))  # all rows
        .order_by(Restaurant.rating.desc().nulls_last(), func.random())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    restaurants: List[Restaurant] = list(result.scalars().all())

    # Count total for pagination
    count_stmt = select(func.count()).select_from(Restaurant)
    total: int = (await db.execute(count_stmt)).scalar_one()

    items = [
        FeedItem(
            id=r.id,
            name=r.name,
            cuisine_type=r.cuisine_type,
            area=r.area,
            price_range=r.price_range,
            rating=r.rating,
            image_url=r.image_url,
            description=r.description,
            dine_in=r.dine_in or False,
            delivery=r.delivery or False,
            score=None,  # populated by ML ranking — not available yet
        )
        for r in restaurants
    ]

    response = FeedResponse(
        user_id=user_id,
        items=items,
        total=total,
        is_cold_start=is_cold_start,
    )

    # ----------------------------------------------------------------- cache
    await cache_set(
        _CACHE_NS,
        cache_key,
        response.model_dump(mode="json"),
        ttl=settings.feed_cache_ttl_seconds,
    )

    return response
