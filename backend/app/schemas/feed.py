"""
Pydantic schemas for the /feed endpoint.

FeedItem is the unit the frontend consumes — one card in the scroll feed.
It is intentionally flat (no nested menu items) to keep the feed response small.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from pydantic import BaseModel, Field


class FeedRequest(BaseModel):
    """Query params for GET /feed — validated separately via Query() in the router."""
    user_id: Optional[uuid.UUID] = None
    limit: int = Field(default=20, ge=1, le=50)
    offset: int = Field(default=0, ge=0)


class FeedItem(BaseModel):
    """A single feed card shown to the user."""
    id: uuid.UUID                       # restaurant ID
    name: str
    cuisine_type: Optional[str] = None
    area: Optional[str] = None
    price_range: Optional[str] = None
    rating: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    dine_in: bool = False
    delivery: bool = False

    # Score assigned by the ranking layer.
    # 0.0–1.0 for ML-ranked items; None for cold-start random items.
    score: Optional[float] = None

    model_config = {"from_attributes": True}


class FeedResponse(BaseModel):
    """Top-level response for GET /feed."""
    user_id: Optional[uuid.UUID] = None
    items: List[FeedItem]
    total: int
    is_cold_start: bool = Field(
        default=False,
        description="True when the feed was built without a user embedding (new user).",
    )
