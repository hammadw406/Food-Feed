"""
Pydantic schemas for the /feed endpoint.
FeedItem is the unit the frontend consumes -- one card in the scroll feed.
Feed shows dishes, not restaurant cards (see feed_service.py docstring).
Tapping a dish opens that restaurant's full menu via a separate endpoint.
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from pydantic import BaseModel, Field


class FeedRequest(BaseModel):
    """Query params for GET /feed -- validated separately via Query() in the router."""
    user_id: Optional[uuid.UUID] = None
    limit: int = Field(default=20, ge=1, le=50)
    offset: int = Field(default=0, ge=0)


class FeedItem(BaseModel):
    """A single dish card shown to the user in the feed."""
    candidate_id: str
    restaurant_id: int
    restaurant_name: str
    display_name: str
    category: Optional[str] = None
    area: Optional[str] = None
    price: Optional[float] = None
    rating: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None

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