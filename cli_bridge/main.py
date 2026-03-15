"""CLI Bridge — FastAPI service (port 8002).

Executes approved CLI commands in sandboxed subprocesses and streams
output via Redis pub/sub.
"""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import APIRouter, FastAPI, HTTPException, status
from pydantic import BaseModel

from cli_bridge.config import CLI_TOOLS
from cli_bridge.runner import run_cli_command
from shared.redis_client import close_redis_client, get_redis_client

# ── In-memory job store (backed up to Redis) ─────────────────────────────────

_jobs: dict[str, dict[str, Any]] = {}


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield
    await close_redis_client()


app = FastAPI(
    title="JARVIS CLI Bridge",
    version="0.1.0",
    lifespan=lifespan,
)

router = APIRouter(prefix="/cli", tags=["cli"])


# ── Schemas ───────────────────────────────────────────────────────────────────


class RunRequest(BaseModel):
    tool_name: str
    command: str


class RunResponse(BaseModel):
    job_id: str
    status: str
    output: str


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/run", response_model=RunResponse)
async def run_command(body: RunRequest) -> RunResponse:
    """Execute a CLI command and return the result."""
    if body.tool_name not in CLI_TOOLS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown CLI tool: {body.tool_name}. "
            f"Available: {list(CLI_TOOLS.keys())}",
        )

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "id": job_id,
        "tool_name": body.tool_name,
        "command": body.command,
        "status": "running",
        "output": "",
    }

    try:
        output = await run_cli_command(
            tool_name=body.tool_name,
            command=body.command,
            job_id=job_id,
        )
        _jobs[job_id]["status"] = "completed"
        _jobs[job_id]["output"] = output
    except Exception as exc:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["output"] = str(exc)

    # Persist to Redis for cross-service access
    redis = await get_redis_client()
    await redis.hset(f"cli_job:{job_id}", mapping=_jobs[job_id])
    await redis.expire(f"cli_job:{job_id}", 3600)

    return RunResponse(
        job_id=job_id,
        status=_jobs[job_id]["status"],
        output=_jobs[job_id]["output"],
    )


@router.get("/jobs/{job_id}")
async def get_job(job_id: str) -> dict[str, Any]:
    """Retrieve the status and output of a CLI job."""
    # Try in-memory first
    if job_id in _jobs:
        return _jobs[job_id]

    # Fall back to Redis
    redis = await get_redis_client()
    data = await redis.hgetall(f"cli_job:{job_id}")
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )
    return data


@router.get("/jobs")
async def list_jobs() -> list[dict[str, Any]]:
    """List all in-memory jobs (recent only)."""
    return list(_jobs.values())


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "cli-bridge"}


app.include_router(router)
