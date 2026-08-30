"""
POST /events — log a user interaction event.

Called by the frontend immediately after each interaction:
  view, skip, like, tap (dwell_time_ms is a field on any event type,
  not a separate event type).

The event is persisted to PostgreSQL and the user's feed cache is invalidated
so their next feed request picks up the new signal.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.event import EventCreate, EventResponse
from app.services.event_service import log_event

router = APIRouter()


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log an interaction event",
    description=(
        "Records a single user interaction (view, skip, like, tap). "
        "After logging, the user's cached feed is invalidated so the next "
        "GET /feed call reflects the new signal."
    ),
)
async def create_event(
    payload: EventCreate,
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    return await log_event(db=db, payload=payload)