"""Redis pub/sub streaming for CLI output."""

from __future__ import annotations

import logging

from shared.redis_client import get_redis_client

logger = logging.getLogger("jarvis.cli_bridge.streaming")

_CHANNEL_PREFIX = "cli_output:"


async def publish_output_chunk(job_id: str, chunk: str) -> None:
    """Publish an output chunk to the Redis channel for this job."""
    redis = await get_redis_client()
    channel = f"{_CHANNEL_PREFIX}{job_id}"
    await redis.publish(channel, chunk)


async def subscribe_output(job_id: str):
    """Yield output chunks for a job as they arrive via Redis pub/sub.

    This is an async generator suitable for use with SSE or WebSocket
    endpoints.

    Usage::

        async for chunk in subscribe_output(job_id):
            print(chunk)
    """
    redis = await get_redis_client()
    channel = f"{_CHANNEL_PREFIX}{job_id}"
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield message["data"]
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
