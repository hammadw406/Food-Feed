"""Initial schema — restaurants, menu_items, users, events.

Revision: 001
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # ---------------------------------------------------------------- users
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=True, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("embedding", Vector(384), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # ---------------------------------------------------------- restaurants
    op.create_table(
        "restaurants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("cuisine_type", sa.String(100), nullable=True),
        sa.Column("area", sa.String(100), nullable=True),
        sa.Column("price_range", sa.String(10), nullable=True),
        sa.Column("rating", sa.Float, nullable=True),
        sa.Column("lat", sa.Numeric(9, 6), nullable=True),
        sa.Column("lng", sa.Numeric(9, 6), nullable=True),
        sa.Column("dine_in", sa.Boolean, default=False),
        sa.Column("delivery", sa.Boolean, default=False),
        sa.Column("image_url", sa.Text, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("embedding", Vector(384), nullable=True),
    )
    op.create_index("ix_restaurants_name", "restaurants", ["name"])

    # ---------------------------------------------------------- menu_items
    op.create_table(
        "menu_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "restaurant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("restaurants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("image_url", sa.Text, nullable=True),
        sa.Column("embedding", Vector(384), nullable=True),
    )
    op.create_index("ix_menu_items_restaurant_id", "menu_items", ["restaurant_id"])

    # ------------------------------------------------------------- events
    op.create_table(
        "events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("item_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum("view", "dwell", "skip", "like", "tap", name="eventtype"),
            nullable=False,
        ),
        sa.Column("dwell_time", sa.Float, nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("context", JSONB, nullable=True),
    )
    op.create_index("ix_events_user_id", "events", ["user_id"])
    op.create_index("ix_events_item_id", "events", ["item_id"])
    op.create_index("ix_events_timestamp", "events", ["timestamp"])

    # pgvector HNSW index on restaurants.embedding for fast ANN search
    op.execute(
        "CREATE INDEX ix_restaurants_embedding_hnsw "
        "ON restaurants USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64);"
    )


def downgrade() -> None:
    op.drop_table("events")
    op.drop_table("menu_items")
    op.drop_table("restaurants")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS eventtype;")
    op.execute("DROP EXTENSION IF EXISTS vector;")
