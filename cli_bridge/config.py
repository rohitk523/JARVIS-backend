"""CLI tool registry — defines which tools are available and their constraints."""

from __future__ import annotations

from typing import Any

CLI_TOOLS: dict[str, dict[str, Any]] = {
    "gemini": {
        "binary": "gemini",
        "description": "Google Gemini CLI",
        "allowed_flags": ["--model", "--prompt"],
    },
}
