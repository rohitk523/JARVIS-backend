"""Core MCP Gateway — manages connections to MCP servers and tool invocation."""

from __future__ import annotations

import logging
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from mcp_gateway.registry import MCP_SERVERS
from shared.models import MCPToolResult

logger = logging.getLogger("jarvis.mcp_gateway")


class MCPGateway:
    """Manages MCP server connections and proxies tool calls."""

    def __init__(self) -> None:
        self._sessions: dict[str, ClientSession] = {}
        self._context_managers: list[Any] = []

    async def _get_session(self, server_name: str) -> ClientSession:
        """Return a cached session for *server_name*, creating one if needed."""
        if server_name in self._sessions:
            return self._sessions[server_name]

        server_cfg = MCP_SERVERS.get(server_name)
        if server_cfg is None:
            raise ValueError(f"Unknown MCP server: {server_name}")

        url = server_cfg["url"]
        headers: dict[str, str] = {}
        if server_cfg.get("auth_type") == "bearer" and server_cfg.get("token"):
            headers["Authorization"] = f"Bearer {server_cfg['token']}"

        # Connect via Streamable HTTP transport
        cm = streamablehttp_client(url=url, headers=headers)
        read_stream, write_stream, _ = await cm.__aenter__()
        self._context_managers.append(cm)

        session = ClientSession(read_stream, write_stream)
        await session.__aenter__()
        self._context_managers.append(session)

        await session.initialize()
        self._sessions[server_name] = session
        logger.info("Connected to MCP server '%s' at %s", server_name, url)
        return session

    async def invoke_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> MCPToolResult:
        """Invoke a tool on the named MCP server."""
        session = await self._get_session(server_name)
        result = await session.call_tool(tool_name, arguments)

        # Flatten text content blocks into a single string
        content_parts: list[str] = []
        for block in result.content:
            if hasattr(block, "text"):
                content_parts.append(block.text)
            else:
                content_parts.append(str(block))

        return MCPToolResult(
            content="\n".join(content_parts),
            is_error=result.isError if hasattr(result, "isError") else False,
        )

    async def list_tools(self, server_name: str) -> list[dict[str, Any]]:
        """List tools available on the named MCP server."""
        session = await self._get_session(server_name)
        result = await session.list_tools()
        return [
            {
                "name": tool.name,
                "description": getattr(tool, "description", ""),
                "input_schema": getattr(tool, "inputSchema", {}),
            }
            for tool in result.tools
        ]

    async def close(self) -> None:
        """Close all active sessions and transports."""
        for cm in reversed(self._context_managers):
            try:
                await cm.__aexit__(None, None, None)
            except Exception:
                logger.exception("Error closing MCP context manager")
        self._context_managers.clear()
        self._sessions.clear()
