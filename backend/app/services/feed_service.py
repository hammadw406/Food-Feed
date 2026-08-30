"""
Feed service -- builds the list of dishes (items) returned by GET /feed.

Feed shows dishes, not restaurant cards. Tapping a dish opens that
restaurant's full menu (see GET /restaurants/{restaurant_id}/menu in
routers/restaurants.py).

Current strategy:
  1. Check Redis cache for this user's feed.
  2. On miss:
     a. If the user has a preference_vector in user_preferences (Person 3's
        batch scoring has run for them) -> placeholder for pgvector nearest-
        neighbor query, ordered/reranked by the LightGBM model
        (ml/train_ranking_model.py). NOT YET WIRED -- see TODO(ml) below.
     b. Cold-start (no preference vector yet) -> diverse sample across
        item clusters (mirrors the logic in ml/coldstart.py: round-robin
        across cluster_id, rating-weighted within each cluster, capped
        per restaurant so one place doesn't dominate the first feed).
  3. Cache the result for FEED_CACHE_TTL seconds.
  4. Invalidate cache key whenever a new event is logged for this user
     (see services/event_service.py).

NOTE: user_preferences is a separate table from users -- it's populated
by ml/compute_preferences.py, keyed by the same user_id string stored on
interactions, not a foreign key to users.id. A real per-user lookup here
needs to join on that string, not assume a uuid relationship.
"""
from __future__ import annotations

import random
from typing import List, Optional

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.restaurant import Item
from app.schemas.feed import FeedItem, FeedResponse
from app.services.cache_service import cache_get, cache_set

_CACHE_NS = "feed"
PER_RESTAURANT_CAP = 2


async def build_feed(
    db: AsyncSession,
    user_id: Optional[str],
    limit: int = 20,
    offset: int = 0,
) -> FeedResponse:
    """
    Build and return a personalised feed of dishes for `user_id`.
    Falls back to cluster-diverse sampling when the user has no
    preference vector yet.
    """
    cache_key = f"{user_id}:{limit}:{offset}"

    # ------------------------------------------------------------------ cache
    cached = await cache_get(_CACHE_NS, cache_key)
    if cached:
        return FeedResponse(**cached)

    # -------------------------------------------------- check preference vector
    is_cold_start = True
    preference_vector = None
    if user_id:
        pref_row = (
            await db.execute(
                text("SELECT preference_vector FROM user_preferences WHERE user_id = :uid"),
                {"uid": str(user_id)},
            )
        ).first()
        if pref_row is not None:
            preference_vector = pref_row[0]
            is_cold_start = False

    if not is_cold_start:
        # TODO(ml -- Person 3): replace with a real pgvector ANN query + the
        # trained LightGBM model, e.g.:
        #   1. SELECT candidate_id, embedding <=> :preference_vector AS distance
        #      FROM items ORDER BY distance LIMIT 50  -- candidate generation
        #   2. score candidates with ml/models/ranking_model.txt (feature set:
        #      pref_similarity, rating, price, cluster_id, review_count)
        #   3. return the top `limit` after offset, sorted by predicted score
        # Falling back to cold-start sampling until this is wired in.
        is_cold_start = True

    items: List[Item] = await _cluster_diverse_sample(db, limit=limit, offset=offset)

    count_stmt = select(func.count()).select_from(Item)
    total: int = (await db.execute(count_stmt)).scalar_one()

    feed_items = [
        FeedItem(
            candidate_id=i.candidate_id,
            display_name=i.display_name,
            category=i.category,
            price=float(i.price) if i.price is not None else None,
            rating=float(i.rating) if i.rating is not None else None,
            restaurant_id=i.restaurant_id,
            restaurant_name=i.restaurant_name,
            area=i.area,
            score=None,  # populated once the ranking model is wired in
        )
        for i in items
    ]

    response = FeedResponse(
        user_id=user_id,
        items=feed_items,
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


async def _cluster_diverse_sample(db: AsyncSession, limit: int, offset: int) -> List[Item]:
    """
    Cluster-based diverse sampling, mirroring ml/coldstart.py: round-robin
    across cluster_id, rating-weighted within each cluster, capped at
    PER_RESTAURANT_CAP items per restaurant.

    Offset is applied by re-seeding rather than a true DB offset -- since
    this sampling is randomized, "page 2" is a fresh diverse sample rather
    than a stable continuation. Acceptable for the cold-start MVP; revisit
    if the frontend needs stable pagination.
    """
    stmt = select(Item).where(Item.cluster_id.isnot(None))
    result = await db.execute(stmt)
    all_items = list(result.scalars().all())

    if not all_items:
        return []

    clusters: dict[int, List[Item]] = {}
    for item in all_items:
        clusters.setdefault(item.cluster_id, []).append(item)

    cluster_ids = list(clusters.keys())
    random.shuffle(cluster_ids)

    restaurant_counts: dict[int, int] = {}
    chosen: List[Item] = []
    exhausted = set()
    pointer = 0

    while len(chosen) < limit + offset and len(exhausted) < len(cluster_ids):
        cid = cluster_ids[pointer % len(cluster_ids)]
        pointer += 1
        if cid in exhausted:
            continue

        candidates = [
            i for i in clusters[cid]
            if restaurant_counts.get(i.restaurant_id, 0) < PER_RESTAURANT_CAP
            and i not in chosen
        ]
        if not candidates:
            exhausted.add(cid)
            continue

        weights = [float(i.rating) if i.rating else 3.5 for i in candidates]
        picked = random.choices(candidates, weights=weights, k=1)[0]

        chosen.append(picked)
        restaurant_counts[picked.restaurant_id] = restaurant_counts.get(picked.restaurant_id, 0) + 1

    return chosen[offset: offset + limit]