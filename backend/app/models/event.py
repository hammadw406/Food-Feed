"""
Event ORM model — every user interaction logged here.

Schema shared with Person 3 (ML).
DO NOT change column names or enum values without aligning with Person 3 first.
"""

import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    JSON,
    Uuid,
)

from app.database import Base


class EventType(str, enum.Enum):
    """
    Interaction event types captured by the frontend (Person 1).

    view     — item entered the viewport
    dwell    — user paused on item for >N seconds (dwell_time is populated)
    skip     — user scrolled past quickly
    like     — explicit like / save
    tap      — user tapped through to the restaurant detail screen
    """
    view = "view"
    dwell = "dwell"
    skip = "skip"
    like = "like"
    tap = "tap"


class Event(Base):
    __tablename__ = "events"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys — not enforced as DB-level constraints to allow events
    # to arrive before the referenced rows are fully committed (edge case).
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    item_id = Column(Uuid(as_uuid=True), nullable=False, index=True)  # restaurant or menu item

    event_type = Column(Enum(EventType), nullable=False)

    # Only populated for "dwell" events; NULL for all others.
    dwell_time = Column(Float, nullable=True)

    # UTC timestamp of when the event occurred (client-side time preferred).
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Flexible context payload — time of day, session_id, feed position, etc.
    # Example: {"session_id": "abc", "time_of_day": "lunch", "feed_position": 3}
    context = Column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<Event id={self.id} user={self.user_id} type={self.event_type}>"
