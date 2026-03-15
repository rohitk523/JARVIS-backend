"""Retrieve and refresh integration tokens for MCP server authentication."""

from __future__ import annotations

import logging
from typing import Any

from shared.supabase_client import get_supabase_client

logger = logging.getLogger("jarvis.mcp_gateway.auth")


async def get_integration_token(
    user_id: str,
    provider: str,
) -> str | None:
    """Fetch the stored access token for a user + provider pair.

    Returns ``None`` when no integration is found.
    """
    sb = get_supabase_client()
    result = (
        sb.table("integrations")
        .select("access_token, refresh_token, expires_at")
        .eq("user_id", user_id)
        .eq("provider", provider)
        .single()
        .execute()
    )
    if not result.data:
        return None

    token: str = result.data["access_token"]
    # TODO: check expires_at and refresh if needed
    return token


async def refresh_integration_token(
    user_id: str,
    provider: str,
) -> str | None:
    """Attempt to refresh an expired token.

    This is a placeholder — the actual refresh flow depends on each
    provider's OAuth implementation.
    """
    logger.warning(
        "Token refresh not yet implemented for provider=%s user=%s",
        provider,
        user_id,
    )
    return None
