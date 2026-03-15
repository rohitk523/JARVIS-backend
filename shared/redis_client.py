"""Async Redis client factory."""

from __future__ import annotations

import redis.asyncio as aioredis

from shared.config import get_settings

_client: aioredis.Redis | None = None


async def get_redis_client() -> aioredis.Redis:
    """Return a lazily-initialised async Redis connection.

    The connection is pooled internally by *redis-py* and safe to reuse
    across concurrent requests.
    """
    global _client
    if _client is None:
        settings = get_settings()
        _client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
    return _client


async def close_redis_client() -> None:
    """Gracefully close the Redis connection (call on app shutdown)."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
