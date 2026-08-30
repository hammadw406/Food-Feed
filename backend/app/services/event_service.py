"""
Event service -- persists an interaction event and triggers downstream hooks.

After persisting, this service:
  1. Invalidates the user's feed cache (so the next GET /feed reflects the new signal).
  2. Calls a hook for Person 3's real-time embedding update logic (placeholder today;
     the batch version already exists in ml/compute_preferences.py).
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interaction import Interaction
from app.schemas.event import EventCreate, EventResponse
from app.services.cache_service import cache_delete


async def log_event(db: AsyncSession, payload: EventCreate) -> EventResponse:
    """
    Persist an interaction event and trigger downstream updates.
    """
    created_at = payload.created_at or datetime.now(timezone.utc)

    interaction = Interaction(
        user_id=payload.user_id,
        candidate_id=payload.candidate_id,
        event_type=payload.event_type,
        dwell_time_ms=payload.dwell_time_ms,
        session_id=payload.session_id,
        created_at=created_at,
    )
    db.add(interaction)
    await db.flush()  # get interaction_id without committing yet

    # ---------------------------------------------------------------- hooks
    if payload.user_id:
        await _invalidate_user_feed_cache(payload.user_id)

    # TODO(ml -- Person 3): call real-time embedding update here once a
    # real-time version exists. Today, ml/compute_preferences.py recomputes
    # preference vectors in batch across all users, not per-event.
    # Example: await update_user_embedding(db, payload.user_id, payload.candidate_id, payload.event_type)

    return EventResponse(
        interaction_id=interaction.interaction_id,
        user_id=interaction.user_id,
        candidate_id=interaction.candidate_id,
        event_type=interaction.event_type,
        created_at=interaction.created_at,
    )


async def _invalidate_user_feed_cache(user_id: str) -> None:
    """
    Invalidate the default feed cache entry (limit=20, offset=0) for this user.
    """
    cache_key = f"{user_id}:20:0"
    await cache_delete("feed", cache_key)
