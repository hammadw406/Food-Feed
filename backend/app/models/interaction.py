"""
Interaction ORM model — every user interaction logged here.

Schema matches the live `interactions` table already in use by the ML
pipeline (see ml/simulate_interactions.py, ml/compute_preferences.py,
ml/build_training_features.py). This replaces the earlier `events` model,
which was built against the original project scaffold spec rather than
the schema actually loaded into Supabase -- do not reintroduce that
version.

DO NOT change column names or enum values without aligning with Person 3
(ML) first -- build_training_features.py and train_ranking_model.py both
depend on these exact field names.

Column types verified directly against the live Supabase table via
information_schema.columns on 2026-08-30:
    interaction_id  integer
    user_id         text
    candidate_id    text
    event_type      text
    dwell_time_ms   integer
    session_id      text
    created_at      timestamp with time zone
"""
import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Integer,
    String,
)
from app.database import Base


class EventType(str, enum.Enum):
    """
    Interaction event types.

    Note: there is no separate "dwell" event type. Dwell time is a field
    (dwell_time_ms) present on any event, not its own event -- this
    differs from the original scaffold spec, which treated dwell as a
    distinct event type.

    view — item entered the viewport
    skip — user scrolled past
    like — explicit like / save
    tap  — user tapped through to the restaurant/item detail screen
    """
    view = "view"
    skip = "skip"
    like = "like"
    tap = "tap"


class Interaction(Base):
    __tablename__ = "interactions"

    # Postgres-side auto-increment integer, not a uuid -- do not set a
    # client-side default here; let the DB assign it (e.g. via SERIAL /
    # IDENTITY, matching however the live table was originally created).
    interaction_id = Column(Integer, primary_key=True, autoincrement=True)

    # Matches ml pipeline's user_id / candidate_id format (e.g. "sim_user_004").
    user_id = Column(String, nullable=True, index=True)
    candidate_id = Column(String, nullable=False, index=True)

    event_type = Column(Enum(EventType), nullable=False)

    # Milliseconds, not seconds -- matches ml/simulate_interactions.py and
    # the live table. Populated across all event types, not just one.
    dwell_time_ms = Column(Integer, nullable=True)

    # First-class column, not buried in a JSON context blob -- required by
    # build_training_features.py and train_ranking_model.py, which both
    # group training rows by session_id for LightGBM's LambdaRank objective.
    session_id = Column(String, nullable=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<Interaction id={self.interaction_id} user={self.user_id} type={self.event_type}>"
