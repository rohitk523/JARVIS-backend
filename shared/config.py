"""Centralised configuration loaded from environment variables / .env file."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All environment variables consumed by JARVIS backend services."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Supabase ──────────────────────────────────────────────────────────
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    supabase_jwt_secret: str = ""

    # ── LiveKit ───────────────────────────────────────────────────────────
    livekit_url: str
    livekit_api_key: str
    livekit_api_secret: str

    # ── LLM / AI ──────────────────────────────────────────────────────────
    anthropic_api_key: str
    google_api_key: str = ""
    deepgram_api_key: str = ""
    cartesia_api_key: str = ""

    # ── Redis ─────────────────────────────────────────────────────────────
    redis_url: str = "redis://redis:6379"

    # ── Internal service URLs (defaults for Docker Compose networking) ───
    mcp_gateway_url: str = "http://mcp-gateway:8001"
    cli_bridge_url: str = "http://cli-bridge:8002"
    rag_service_url: str = "http://rag:8003"


@lru_cache
def get_settings() -> Settings:
    """Return a cached *Settings* singleton."""
    return Settings()  # type: ignore[call-arg]
