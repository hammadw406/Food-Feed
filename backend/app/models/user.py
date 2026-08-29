"""
User ORM model.

The `embedding` column is the real-time preference vector for the user —
it starts as NULL (cold-start) and is updated by Person 3's real-time
embedding update logic each time an interaction event arrives.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Uuid
from pgvector.sqlalchemy import Vector

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Email synced from auth provider (Supabase / Clerk).
    # Optional — anonymous users are allowed in the MVP.
    email = Column(String(255), nullable=True, unique=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Real-time user preference embedding (384 dims, same space as item embeddings).
    # Updated as a weighted moving average after each positive interaction.
    # NULL = cold-start state → feed falls back to diverse / popular sampling.
    embedding = Column(Vector(384), nullable=True)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
