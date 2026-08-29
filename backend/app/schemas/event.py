"""
Pydantic schemas for the /events endpoint.

Shared contract with Person 3 (ML) — do not change field names without coordinating.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.models.event import EventType


class EventCreate(BaseModel):
    """
    POST /events request body.
    The frontend sends this immediately after each user interaction.
    """
    user_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Null for anonymous / pre-auth sessions.",
    )
    item_id: uuid.UUID = Field(description="Restaurant or menu item UUID.")
    event_type: EventType
    dwell_time: Optional[float] = Field(
        default=None,
        description="Seconds the user spent on this item. Only set for 'dwell' events.",
    )
    # Client-side timestamp — more accurate than server receipt time.
    timestamp: Optional[datetime] = Field(
        default=None,
        description="UTC ISO-8601. Defaults to server time if not provided.",
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Flexible JSON payload. "
            "Recommended keys: session_id (str), time_of_day (str), feed_position (int)."
        ),
        examples=[{"session_id": "abc123", "time_of_day": "lunch", "feed_position": 3}],
    )


class EventResponse(BaseModel):
    """Response body after a successful event log."""
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    item_id: uuid.UUID
    event_type: EventType
    timestamp: datetime

    model_config = {"from_attributes": True}
