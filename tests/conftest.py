"""Shared pytest fixtures for JARVIS backend tests."""

from __future__ import annotations

from typing import Any, AsyncIterator
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from shared.config import Settings


def _mock_settings() -> Settings:
    """Return a Settings instance with dummy values for testing."""
    return Settings(
        supabase_url="https://test.supabase.co",
        supabase_anon_key="test-anon-key",
        supabase_service_key="test-service-key",
        supabase_jwt_secret="test-jwt-secret-that-is-long-enough-for-hs256",
        livekit_url="wss://test.livekit.cloud",
        livekit_api_key="test-lk-key",
        livekit_api_secret="test-lk-secret",
        anthropic_api_key="sk-ant-test",
        google_api_key="AIza-test",
        deepgram_api_key="test-deepgram",
        cartesia_api_key="test-cartesia",
        redis_url="redis://localhost:6379",
    )


@pytest.fixture()
def mock_settings() -> Settings:
    """Provide mock settings to tests."""
    return _mock_settings()


@pytest.fixture()
async def api_client() -> AsyncIterator[AsyncClient]:
    """Provide an async test client for the API service.

    Patches ``get_settings`` so the app boots without real env vars.
    """
    with patch("shared.config.get_settings", return_value=_mock_settings()):
        from api.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
