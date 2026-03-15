"""Third-party integration management endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.deps import get_current_user
from shared.supabase_client import get_supabase_client

router = APIRouter()

_TABLE = "integrations"


class IntegrationCreate(BaseModel):
    provider: str
    access_token: str
    refresh_token: str | None = None
    expires_at: str | None = None  # ISO-8601


@router.get("")
async def list_integrations(
    user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """List all integrations for the authenticated user."""
    user_id: str = user["sub"]
    sb = get_supabase_client()
    result = (
        sb.table(_TABLE)
        .select("id, provider, created_at, expires_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_integration(
    body: IntegrationCreate,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Store a new integration (tokens are stored encrypted at-rest by Supabase)."""
    user_id: str = user["sub"]
    sb = get_supabase_client()
    payload: dict[str, Any] = {
        "user_id": user_id,
        "provider": body.provider,
        "access_token": body.access_token,
        "refresh_token": body.refresh_token,
        "expires_at": body.expires_at,
    }
    result = sb.table(_TABLE).insert(payload).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create integration",
        )
    return result.data[0]


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: str,
    user: dict[str, Any] = Depends(get_current_user),
) -> None:
    """Remove an integration (only if it belongs to the authenticated user)."""
    user_id: str = user["sub"]
    sb = get_supabase_client()
    result = (
        sb.table(_TABLE)
        .delete()
        .eq("id", integration_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )
