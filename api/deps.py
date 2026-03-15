"""Re-usable FastAPI dependencies for the API service."""

from __future__ import annotations

from shared.auth import get_current_user
from shared.config import Settings, get_settings

__all__ = ["get_current_user", "get_settings", "Settings"]
