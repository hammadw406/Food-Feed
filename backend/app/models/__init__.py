# models package — import all models so Alembic autogenerate can detect them
from app.models.restaurant import Restaurant, MenuItem  # noqa: F401
from app.models.user import User                        # noqa: F401
from app.models.event import Event, EventType           # noqa: F401
