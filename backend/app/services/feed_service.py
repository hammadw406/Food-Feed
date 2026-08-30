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

from pathlib import Path

import lightgbm as lgb
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.restaurant import Item
from app.schemas.feed import FeedItem, FeedResponse
from app.services.cache_service import cache_get, cache_set

_CACHE_NS = "feed"
PER_RESTAURANT_CAP = 2

_RANKING_MODEL_PATH = Path(__file__).resolve().parents[3] / "ml" / "models" / "ranking_model.txt"
_ranking_model: Optional[lgb.Booster] = None


def _get_ranking_model() -> lgb.Booster:
    """Load the LightGBM ranking model once and cache it in memory."""
    global _ranking_model
    if _ranking_model is None:
        _ranking_model = lgb.Booster(model_file=str(_RANKING_MODEL_PATH))
    return _ranking_model


def _vector_literal(vector) -> str:
    """
    Format a preference vector as a pgvector literal string, e.g. "[0.1,0.2,...]",
    for use with CAST(:pref AS vector). Works whether preference_vector comes
    back from asyncpg as a python list/ndarray or already as a string.
    """
    if isinstance(vector, str):
        return vector
    return "[" + ",".join(str(float(v)) for v in vector) + "]"


_CANDIDATE_QUERY = text("""
    SELECT
        i.candidate_id,
        i.display_name,
        i.category,
        i.price,
        i.rating,
        i.restaurant_id,
        i.restaurant_name,
        i.area,
        i.cluster_id,
        r.review_count,
        i.embedding <=> CAST(:pref AS vector) AS distance
    FROM items i
    JOIN restaurants r ON r.restaurant_id = i.restaurant_id
    WHERE i.embedding IS NOT NULL
    ORDER BY distance
    LIMIT 50
""")


async def _personalized_candidates(
    db: AsyncSession,
    preference_vector,
    limit: int,
    offset: int,
) -> List[FeedItem]:
    """
    pgvector ANN candidate generation (top 50 nearest to the user's
    preference vector) + LightGBM reranking. Feature order/names are
    read directly from ml/models/ranking_model.txt's feature_names line:
    pref_similarity, rating, price, cluster_id, review_count.
    """
    rows = (
        await db.execute(_CANDIDATE_QUERY, {"pref": _vector_literal(preference_vector)})
    ).all()
    if not rows:
        return []

    model = _get_ranking_model()

    features = []
    for row in rows:
        (
            candidate_id, display_name, category, price, rating,
            restaurant_id, restaurant_name, area, cluster_id,
            review_count, distance,
        ) = row
        pref_similarity = 1.0 - float(distance) if distance is not None else 0.0
        features.append([
            pref_similarity,
            float(rating) if rating is not None else 0.0,
            float(price) if price is not None else 0.0,
            float(cluster_id) if cluster_id is not None else -1.0,
            float(review_count) if review_count is not None else 0.0,
        ])

    scores = model.predict(features)

    scored_rows = list(zip(rows, scores))
    scored_rows.sort(key=lambda pair: pair[1], reverse=True)

    restaurant_counts: dict[int, int] = {}
    picked: List[tuple] = []
    for row, score in scored_rows:
        restaurant_id = row[5]
        if restaurant_counts.get(restaurant_id, 0) >= PER_RESTAURANT_CAP:
            continue
        picked.append((row, score))
        restaurant_counts[restaurant_id] = restaurant_counts.get(restaurant_id, 0) + 1

    page = picked[offset: offset + limit]

    return [
        FeedItem(
            candidate_id=row[0],
            display_name=row[1],
            category=row[2],
            price=float(row[3]) if row[3] is not None else None,
            rating=float(row[4]) if row[4] is not None else None,
            restaurant_id=row[5],
            restaurant_name=row[6],
            area=row[7],
            score=float(score),
        )
        for row, score in page
    ]


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

    feed_items: List[FeedItem]
    if not is_cold_start:
        feed_items = await _personalized_candidates(
            db, preference_vector, limit=limit, offset=offset
        )
        if not feed_items:
            is_cold_start = True

    if is_cold_start:
        items = await _cluster_diverse_sample(db, limit=limit, offset=offset)
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
                score=None,
            )
            for i in items
        ]

    count_stmt = select(func.count()).select_from(Item)
    total: int = (await db.execute(count_stmt)).scalar_one()

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