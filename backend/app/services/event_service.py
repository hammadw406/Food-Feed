"""
Event service — persists an interaction event and triggers downstream hooks.

After persisting, this service:
  1. Invalidates the user's feed cache (so the next GET /feed reflects the new signal).
  2. Calls a hook for Person 3's real-time embedding update logic (placeholder today).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.schemas.event import EventCreate, EventResponse
from app.services.cache_service import cache_delete


async def log_event(db: AsyncSession, payload: EventCreate) -> EventResponse:
    """
    Persist an interaction event and trigger downstream updates.
    """
    # Use client-supplied timestamp if provided, else server time (UTC).
    timestamp = payload.timestamp or datetime.now(timezone.utc)

    event = Event(
        id=uuid.uuid4(),
        user_id=payload.user_id,
        item_id=payload.item_id,
        event_type=payload.event_type,
        dwell_time=payload.dwell_time,
        timestamp=timestamp,
        context=payload.context,
    )
    db.add(event)
    await db.flush()  # get the ID without committing yet

    # ---------------------------------------------------------------- hooks
    # Invalidate feed cache so next request rebuilds the feed.
    if payload.user_id:
        # Invalidate all cached pages for this user (wildcard by prefix not
        # supported in simple Redis; we invalidate the first page as a heuristic).
        await _invalidate_user_feed_cache(payload.user_id)

    # TODO(ml — Person 3): call real-time embedding update here.
    # Example: await update_user_embedding(db, payload.user_id, payload.item_id, payload.event_type)

    return EventResponse(
        id=event.id,
        user_id=event.user_id,
        item_id=event.item_id,
        event_type=event.event_type,
        timestamp=event.timestamp,
    )


async def _invalidate_user_feed_cache(user_id: uuid.UUID) -> None:
    """
    Invalidate the default feed cache entry (limit=20, offset=0) for this user.
    """
    cache_key = f"{user_id}:20:0"
    await cache_delete("feed", cache_key)
