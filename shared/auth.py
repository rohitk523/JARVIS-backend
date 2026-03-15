"""JWT verification and FastAPI authentication dependency."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from shared.config import Settings, get_settings

_bearer_scheme = HTTPBearer()


async def verify_jwt(
    token: str,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Decode and verify a Supabase-issued JWT.

    Returns the full JWT payload on success.  Raises *HTTPException 401*
    on any verification failure.
    """
    if settings is None:
        settings = get_settings()

    if not settings.supabase_jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_JWT_SECRET is not configured",
        )

    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return payload


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """FastAPI dependency — extract and verify the Bearer token.

    Returns the decoded JWT payload (contains ``sub``, ``email``, etc.).
    """
    return await verify_jwt(credentials.credentials, settings)
