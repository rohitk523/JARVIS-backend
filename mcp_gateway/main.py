"""MCP Gateway — FastAPI service (port 8001).

Provides a unified HTTP interface to invoke tools on remote MCP servers.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import APIRouter, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

from mcp_gateway.gateway import MCPGateway

# ── Lifespan ──────────────────────────────────────────────────────────────────

_gateway = MCPGateway()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield
    await _gateway.close()


app = FastAPI(
    title="JARVIS MCP Gateway",
    version="0.1.0",
    lifespan=lifespan,
)

router = APIRouter(prefix="/mcp", tags=["mcp"])


# ── Schemas ───────────────────────────────────────────────────────────────────


class InvokeRequest(BaseModel):
    server_name: str
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class InvokeResponse(BaseModel):
    content: str
    is_error: bool = False


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/invoke", response_model=InvokeResponse)
async def invoke_tool(body: InvokeRequest) -> InvokeResponse:
    """Invoke a tool on a named MCP server."""
    try:
        result = await _gateway.invoke_tool(
            server_name=body.server_name,
            tool_name=body.tool_name,
            arguments=body.arguments,
        )
        return InvokeResponse(content=result.content, is_error=result.is_error)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        return InvokeResponse(content=str(exc), is_error=True)


@router.get("/tools")
async def list_tools(
    server_name: str = Query(..., description="Name of the MCP server"),
) -> list[dict[str, Any]]:
    """List tools available on a given MCP server."""
    try:
        return await _gateway.list_tools(server_name)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "mcp-gateway"}


app.include_router(router)
