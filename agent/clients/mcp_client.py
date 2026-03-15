"""Async HTTP client for the MCP Gateway service."""

from __future__ import annotations

import json

import httpx

from shared.config import get_settings

_TIMEOUT = httpx.Timeout(30.0, connect=5.0)


async def invoke_mcp_tool(
    server_name: str,
    tool_name: str,
    arguments_json: str,
) -> str:
    """Call POST /mcp/invoke on the MCP Gateway and return the result text."""
    settings = get_settings()
    url = f"{settings.mcp_gateway_url}/mcp/invoke"

    try:
        arguments = json.loads(arguments_json) if arguments_json else {}
    except json.JSONDecodeError:
        return f"Error: invalid JSON arguments — {arguments_json}"

    payload = {
        "server_name": server_name,
        "tool_name": tool_name,
        "arguments": arguments,
    }

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(url, json=payload)

    if resp.status_code != 200:
        return f"MCP Gateway error ({resp.status_code}): {resp.text}"

    data = resp.json()
    if data.get("is_error"):
        return f"Tool error: {data.get('content', 'unknown error')}"
    return data.get("content", "")


async def list_mcp_tools(server_name: str) -> list[dict]:
    """Fetch the list of available tools from an MCP server."""
    settings = get_settings()
    url = f"{settings.mcp_gateway_url}/mcp/tools"
    params = {"server_name": server_name}

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(url, params=params)

    if resp.status_code != 200:
        return []
    return resp.json()
