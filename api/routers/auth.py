"""Authentication endpoints — proxy to Supabase Auth."""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.deps import get_current_user, get_settings
from shared.config import Settings

router = APIRouter()


# ── Request / Response schemas ───────────────────────────────────────────────


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Helpers ──────────────────────────────────────────────────────────────────


def _auth_headers(settings: Settings) -> dict[str, str]:
    return {
        "apikey": settings.supabase_anon_key,
        "Content-Type": "application/json",
    }


# ── Routes ───────────────────────────────────────────────────────────────────


@router.post("/login")
async def login(
    body: LoginRequest,
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Sign in with email + password via Supabase GoTrue."""
    url = f"{settings.supabase_url}/auth/v1/token?grant_type=password"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            headers=_auth_headers(settings),
            json={"email": body.email, "password": body.password},
        )
    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=resp.json().get("error_description", "Authentication failed"),
        )
    return resp.json()


@router.post("/refresh")
async def refresh_token(
    body: RefreshRequest,
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Refresh an access token via Supabase GoTrue."""
    url = f"{settings.supabase_url}/auth/v1/token?grant_type=refresh_token"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            headers=_auth_headers(settings),
            json={"refresh_token": body.refresh_token},
        )
    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=resp.json().get("error_description", "Token refresh failed"),
        )
    return resp.json()


@router.get("/me")
async def me(
    user: dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Return the current user's profile from Supabase."""
    user_id: str = user["sub"]
    url = f"{settings.supabase_url}/auth/v1/admin/users/{user_id}"
    headers = {
        "apikey": settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch user profile from Supabase",
        )
    data = resp.json()
    return {
        "id": data.get("id"),
        "email": data.get("email"),
        "full_name": data.get("user_metadata", {}).get("full_name", ""),
        "avatar_url": data.get("user_metadata", {}).get("avatar_url", ""),
        "created_at": data.get("created_at"),
    }
