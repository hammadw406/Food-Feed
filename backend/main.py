"""
Food Feed — FastAPI application entry point.
Person 2: Backend / API
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.redis_client import get_redis_client
from app.routers import feed, events, restaurants

# ---------------------------------------------------------------------------
# Lifespan: startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — create all tables if they don't exist yet (dev convenience).
    # In production, Alembic migrations handle schema changes.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Redis temporarily disabled for local testing — no Redis instance available yet.
    # TODO: restore before merging / before production use.
    # redis = await get_redis_client()
    # await redis.ping()
    # print("Redis connected")

    yield  # App is running

    # Shutdown — dispose DB connections
    await engine.dispose()
    # await redis.aclose()
    print("Connections closed")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Food Feed API",
    description=(
        "Personalized food discovery feed for DHA, Lahore. "
        "Learns from user interactions (dwell, skip, like, tap) to reshape the feed in real time."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow the Next.js frontend (and local dev) to call the API
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(feed.router, prefix="/feed", tags=["Feed"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    """Simple liveness probe for Railway/Render health checks."""
    return {"status": "ok", "service": "food-feed-backend"}