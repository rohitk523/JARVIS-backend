"""User settings endpoints (backed by Supabase)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.deps import get_current_user
from shared.supabase_client import get_supabase_client

router = APIRouter()

_TABLE = "user_settings"


class UserSettings(BaseModel):
    """Freeform user settings payload."""

    voice: str = "alloy"
    language: str = "en"
    theme: str = "system"
    notifications_enabled: bool = True


@router.get("")
async def get_settings(
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Fetch user settings. Returns defaults when no row exists."""
    user_id: str = user["sub"]
    sb = get_supabase_client()
    result = sb.table(_TABLE).select("*").eq("user_id", user_id).execute()
    if result.data:
        return result.data[0]
    # Return defaults when no settings row exists yet
    return UserSettings().model_dump()


@router.put("")
async def update_settings(
    body: UserSettings,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Upsert user settings."""
    user_id: str = user["sub"]
    sb = get_supabase_client()
    payload = {"user_id": user_id, **body.model_dump()}
    result = (
        sb.table(_TABLE)
        .upsert(payload, on_conflict="user_id")
        .execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save settings",
        )
    return result.data[0]
