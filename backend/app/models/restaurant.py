"""
Restaurant and Item ORM models.

Column types verified directly against the live Supabase table via
information_schema.columns on 2026-08-30:

restaurants:
    restaurant_id   integer (PK, not uuid)
    name            text
    area            text
    cuisine         text        (not "cuisine_type")
    price_band      text        (not "price_range"; sparse -- empty for
                                  the original 126 restaurants)
    rating          numeric
    review_count    integer
    source          text
    embedding       vector(384) ("USER-DEFINED" = pgvector type)
    created_at      timestamp with time zone

items:
    candidate_id    text (PK, not uuid)     -- this is the menu-item-level
                                                table; there is no separate
                                                "menu_items" table in the
                                                live DB, despite what the
                                                original migration assumed
    restaurant_id   integer, FK -> restaurants.restaurant_id
    restaurant_name text
    candidate_type  text
    display_name    text        (not "name")
    category        text
    price           numeric
    rating          numeric
    area            text
    embed_text      text
    embedding       vector(384)
    created_at      timestamp with time zone
    cluster_id      integer     (from ml/precompute_clusters.py, Phase 3
                                  cold-start sampling)

This replaces the earlier Restaurant/MenuItem models, which were built
against the original scaffold spec (uuid PKs, cuisine_type, price_range,
lat/lng, dine_in/delivery, a separate menu_items table) rather than the
schema actually loaded into Supabase. Do not reintroduce that version,
and do not run the 001_initial_schema.py Alembic migration against the
live database -- it CREATEs these tables from scratch with the wrong
shape and will either fail (tables already exist) or, in a fresh DB,
produce a schema the ML pipeline can't read.

DO NOT change column names without aligning with Person 3 (ML) first --
the entire ml/ pipeline (embeddings, cold-start clustering, ranking model
training) depends on these exact field names.

Known gaps not modeled here, worth raising with the team:
    - lat/lng, dine_in, delivery, image_url, description do not exist on
      the live restaurants table. If the frontend needs any of these for
      the feed UI, they need to be added via a real migration against the
      live table, not assumed to already exist.
    - price_band is empty for 126 of 164 restaurants (per the ML handoff)
      -- don't rely on it being populated everywhere.
"""
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    restaurant_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    area = Column(Text, nullable=True)
    cuisine = Column(Text, nullable=True)
    # Sparse -- only partially filled for the 38 restaurants added via
    # menu scraping, empty for the original 126. Don't assume non-null.
    price_band = Column(Text, nullable=True)
    rating = Column(Numeric, nullable=True)
    review_count = Column(Integer, nullable=True)
    source = Column(Text, nullable=True)
    embedding = Column(Vector(384), nullable=True)

    items = relationship("Item", back_populates="restaurant", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Restaurant id={self.restaurant_id} name={self.name!r}>"


class Item(Base):
    """
    Menu-item-level candidate. Matches the live `items` table used
    throughout ml/build_candidates.py, ml/load_items_to_pgvector.py,
    ml/precompute_clusters.py, and ml/build_training_features.py.
    """
    __tablename__ = "items"

    candidate_id = Column(String, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id", ondelete="CASCADE"), nullable=False, index=True)
    restaurant_name = Column(Text, nullable=True)
    candidate_type = Column(Text, nullable=True)
    display_name = Column(Text, nullable=False)
    category = Column(Text, nullable=True)
    price = Column(Numeric, nullable=True)
    rating = Column(Numeric, nullable=True)
    area = Column(Text, nullable=True)
    embed_text = Column(Text, nullable=True)
    embedding = Column(Vector(384), nullable=True)
    # Populated by ml/precompute_clusters.py -- used for cold-start diverse
    # sampling (ml/coldstart.py). NULL until that script has been run.
    cluster_id = Column(Integer, nullable=True)

    restaurant = relationship("Restaurant", back_populates="items")

    def __repr__(self) -> str:
        return f"<Item id={self.candidate_id} name={self.display_name!r}>"
