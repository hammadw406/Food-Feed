# models package — import all models so Alembic autogenerate can detect them
from app.models.restaurant import Restaurant, Item  # noqa: F401
from app.models.user import User                        # noqa: F401
from app.models.interaction import Interaction, EventType  # noqa: F401