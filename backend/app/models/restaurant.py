"""
Restaurant and MenuItem ORM models.

Both tables include a `embedding` column (vector(384)) so Person 3 can store
sentence-transformer embeddings without a schema migration.
"""

import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Numeric,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    cuisine_type = Column(String(100), nullable=True)
    area = Column(String(100), nullable=True)          # e.g. "DHA Phase 5"
    price_range = Column(String(10), nullable=True)    # "$" | "$$" | "$$$"
    rating = Column(Float, nullable=True)
    lat = Column(Numeric(9, 6), nullable=True)
    lng = Column(Numeric(9, 6), nullable=True)
    dine_in = Column(Boolean, default=False)
    delivery = Column(Boolean, default=False)
    image_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    # Embedding produced by sentence-transformers (all-MiniLM-L6-v2 → 384 dims).
    # NULL until Person 3 runs the embedding computation pass.
    embedding = Column(Vector(384), nullable=True)

    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Restaurant id={self.id} name={self.name!r}>"


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(Uuid(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    category = Column(String(100), nullable=True)      # e.g. "Burger", "Drink"
    image_url = Column(Text, nullable=True)

    # Per-item embedding — allows nearest-neighbor on menu items too
    embedding = Column(Vector(384), nullable=True)

    restaurant = relationship("Restaurant", back_populates="menu_items")

    def __repr__(self) -> str:
        return f"<MenuItem id={self.id} name={self.name!r}>"
