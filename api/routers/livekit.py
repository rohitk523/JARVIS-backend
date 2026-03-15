"""LiveKit token generation endpoint."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from livekit.api import AccessToken, VideoGrants
from pydantic import BaseModel

from api.deps import get_current_user, get_settings
from shared.config import Settings

router = APIRouter()


class TokenRequest(BaseModel):
    """Client sends a room name (optional — auto-generated if omitted)."""

    room_name: str = "jarvis-room"


class TokenResponse(BaseModel):
    token: str
    room_name: str


@router.post("/token", response_model=TokenResponse)
async def create_livekit_token(
    body: TokenRequest,
    user: dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    """Generate a LiveKit access token for the authenticated user."""
    user_id: str = user.get("sub", "")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing 'sub' claim",
        )

    token = (
        AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
        .with_identity(user_id)
        .with_name(user.get("email", user_id))
        .with_grants(
            VideoGrants(
                room_join=True,
                room=body.room_name,
            )
        )
    )

    return TokenResponse(
        token=token.to_jwt(),
        room_name=body.room_name,
    )
