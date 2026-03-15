"""Async HTTP client for the CLI Bridge service."""

from __future__ import annotations

import httpx

from shared.config import get_settings

_TIMEOUT = httpx.Timeout(120.0, connect=5.0)


async def run_remote_cli_task(tool_name: str, command: str) -> str:
    """Submit a CLI task to the CLI Bridge and return the output.

    The CLI Bridge executes the command in a sandboxed subprocess and
    returns the captured stdout/stderr.
    """
    settings = get_settings()
    url = f"{settings.cli_bridge_url}/cli/run"
    payload = {"tool_name": tool_name, "command": command}

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(url, json=payload)

    if resp.status_code != 200:
        return f"CLI Bridge error ({resp.status_code}): {resp.text}"

    data = resp.json()
    return data.get("output", "")


async def get_cli_job(job_id: str) -> dict:
    """Retrieve the status and output of a CLI job by ID."""
    settings = get_settings()
    url = f"{settings.cli_bridge_url}/cli/jobs/{job_id}"

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(url)

    if resp.status_code != 200:
        return {"status": "error", "output": resp.text}
    return resp.json()
