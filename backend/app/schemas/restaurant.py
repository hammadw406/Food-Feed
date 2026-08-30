"""
Pydantic schemas for the /restaurants endpoint.

RestaurantDetail is the full card shown when a user taps a dish in the
feed -- it opens that restaurant's page with its full menu of items.
Matches the live restaurants/items tables (see app/models/restaurant.py).
"""
from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class MenuItemSchema(BaseModel):
    candidate_id: str
    display_name: str
    category: Optional[str] = None
    price: Optional[Decimal] = None
    rating: Optional[Decimal] = None

    model_config = {"from_attributes": True}


class RestaurantDetail(BaseModel):
    """Full restaurant detail -- shown when a feed dish is tapped, includes the full menu."""
    restaurant_id: int
    name: str
    area: Optional[str] = None
    cuisine: Optional[str] = None
    price_band: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    items: List[MenuItemSchema] = []

    model_config = {"from_attributes": True}


class RestaurantListItem(BaseModel):
    """Minimal restaurant info for list views."""
    restaurant_id: int
    name: str
    area: Optional[str] = None
    cuisine: Optional[str] = None
    rating: Optional[float] = None

    model_config = {"from_attributes": True}
