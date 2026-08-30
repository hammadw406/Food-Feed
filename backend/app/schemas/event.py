"""
Pydantic schemas for the /events endpoint (logs to the `interactions` table).

Shared contract with Person 3 (ML) -- matches the schema already live in
Supabase and used throughout the ml/ pipeline. Do not change field names
without coordinating; build_training_features.py and train_ranking_model.py
depend on these exact names.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.interaction import EventType


class EventCreate(BaseModel):
    """
    POST /events request body.
    The frontend sends this immediately after each user interaction.
    """
    user_id: Optional[str] = Field(
        default=None,
        description="Null for anonymous / pre-auth sessions.",
    )
    candidate_id: str = Field(description="ID of the item shown (matches items.candidate_id).")
    event_type: EventType
    dwell_time_ms: Optional[int] = Field(
        default=None,
        description="Milliseconds the user spent on this item.",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Groups events into a single scroll session. Used by the ranking model's training pipeline.",
    )
    # Client-side timestamp -- more accurate than server receipt time.
    created_at: Optional[datetime] = Field(
        default=None,
        description="UTC ISO-8601. Defaults to server time if not provided.",
    )


class EventResponse(BaseModel):
    """Response body after a successful event log."""
    interaction_id: int
    user_id: Optional[str]
    candidate_id: str
    event_type: EventType
    created_at: datetime

    model_config = {"from_attributes": True}
