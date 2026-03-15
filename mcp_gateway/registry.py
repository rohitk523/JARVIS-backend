"""Static registry of known MCP servers.

Each entry maps a short name to connection details.  Tokens are injected
at runtime via environment variables or the auth_manager module.
"""

from __future__ import annotations

from typing import Any

MCP_SERVERS: dict[str, dict[str, Any]] = {
    "linear": {
        "url": "https://mcp.linear.app/sse",
        "auth_type": "bearer",
        "token": "",  # populated at runtime from integrations table
        "description": "Linear project management — issues, projects, teams",
    },
}
