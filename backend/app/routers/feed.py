"""
GET /feed — returns a personalised feed of restaurants for the requesting user.

Query params:
  user_id (UUID, optional) — omit for anonymous users
  limit   (int, 1-50, default 20)
  offset  (int, default 0)

Auth: optional — pass a Bearer token for personalised results; omit for anonymous.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.feed import FeedResponse
from app.services.feed_service import build_feed

router = APIRouter()


@router.get(
    "",
    response_model=FeedResponse,
    summary="Get personalised feed",
    description=(
        "Returns a ranked list of restaurants tailored to the user's interaction history. "
        "Falls back to diverse popular sampling for new users (cold-start). "
        "Results are cached in Redis for 60 seconds per user."
    ),
)
async def get_feed(
    user_id: Optional[uuid.UUID] = Query(
        default=None,
        description="The user's UUID. Omit for anonymous sessions.",
    ),
    limit: int = Query(default=20, ge=1, le=50, description="Number of feed items to return."),
    offset: int = Query(default=0, ge=0, description="Pagination offset."),
    db: AsyncSession = Depends(get_db),
) -> FeedResponse:
    return await build_feed(db=db, user_id=user_id, limit=limit, offset=offset)
