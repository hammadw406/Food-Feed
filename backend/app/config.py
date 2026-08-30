"""
App configuration — reads from .env via pydantic-settings.
"""

from __future__ import annotations

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Database -----------------------------------------------------------
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/food_discovery"

    # ---- Redis --------------------------------------------------------------
    redis_url: str = "redis://localhost:6379"

    # ---- Auth ---------------------------------------------------------------
    auth_provider: str = "supabase"          # "supabase" or "clerk"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    clerk_secret_key: str = ""

    # Set to "true" in dev to skip JWT verification entirely
    skip_auth: bool = False

    # ---- CORS ---------------------------------------------------------------
    cors_origins: List[str] = [
        "http://localhost:3000",             # Next.js dev server
        "https://food-feed.vercel.app",      # Production frontend
    ]

    # ---- Cache --------------------------------------------------------------
    feed_cache_ttl_seconds: int = 60         # How long to cache a user's feed

    # ---- Monitoring ---------------------------------------------------------
    sentry_dsn: str = ""


settings = Settings()
