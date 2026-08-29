"""
Pydantic schemas for the /restaurants endpoint.

RestaurantDetail is the full card shown on the restaurant detail screen,
including all menu items.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class MenuItemSchema(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}


class RestaurantDetail(BaseModel):
    """Full restaurant detail — used on the detail screen, not the feed card."""
    id: uuid.UUID
    name: str
    cuisine_type: Optional[str] = None
    area: Optional[str] = None
    price_range: Optional[str] = None
    rating: Optional[float] = None
    lat: Optional[Decimal] = None
    lng: Optional[Decimal] = None
    dine_in: bool = False
    delivery: bool = False
    image_url: Optional[str] = None
    description: Optional[str] = None
    menu_items: List[MenuItemSchema] = []

    model_config = {"from_attributes": True}


class RestaurantListItem(BaseModel):
    """Minimal restaurant info for list views."""
    id: uuid.UUID
    name: str
    cuisine_type: Optional[str] = None
    area: Optional[str] = None
    rating: Optional[float] = None
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}
