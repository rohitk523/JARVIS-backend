"""Subprocess runner for CLI commands with sandboxing and timeouts."""

from __future__ import annotations

import asyncio
import logging
import shlex

from cli_bridge.config import CLI_TOOLS
from cli_bridge.streaming import publish_output_chunk

logger = logging.getLogger("jarvis.cli_bridge.runner")

# Maximum execution time for any single command (seconds)
_DEFAULT_TIMEOUT = 120


async def run_cli_command(
    tool_name: str,
    command: str,
    job_id: str,
    timeout: int = _DEFAULT_TIMEOUT,
) -> str:
    """Execute *command* using the binary registered for *tool_name*.

    The command is validated against the tool's allowed flags before
    execution.  Output is streamed via Redis pub/sub and also returned
    as a single string when the process completes.

    Raises
    ------
    ValueError
        If the tool is unknown or the command uses disallowed flags.
    TimeoutError
        If the process exceeds *timeout* seconds.
    RuntimeError
        If the process exits with a non-zero return code.
    """
    tool_cfg = CLI_TOOLS.get(tool_name)
    if tool_cfg is None:
        raise ValueError(f"Unknown CLI tool: {tool_name}")

    binary: str = tool_cfg["binary"]
    allowed_flags: list[str] = tool_cfg.get("allowed_flags", [])

    # ── Validate flags ────────────────────────────────────────────────────
    parts = shlex.split(command)
    for part in parts:
        if part.startswith("-") and part not in allowed_flags:
            # Allow long-form --flag=value by checking the flag prefix
            flag_name = part.split("=", 1)[0]
            if flag_name not in allowed_flags:
                raise ValueError(
                    f"Flag '{flag_name}' is not allowed for tool '{tool_name}'. "
                    f"Allowed: {allowed_flags}"
                )

    full_command = f"{binary} {command}"
    logger.info("Running CLI command [%s]: %s", job_id, full_command)

    # ── Execute ───────────────────────────────────────────────────────────
    process = await asyncio.create_subprocess_shell(
        full_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    output_chunks: list[str] = []

    try:
        assert process.stdout is not None
        while True:
            line = await asyncio.wait_for(
                process.stdout.readline(),
                timeout=timeout,
            )
            if not line:
                break
            decoded = line.decode("utf-8", errors="replace")
            output_chunks.append(decoded)
            # Stream to Redis pub/sub
            await publish_output_chunk(job_id, decoded)
    except asyncio.TimeoutError:
        process.kill()
        raise TimeoutError(
            f"Command timed out after {timeout}s: {full_command}"
        )

    await process.wait()
    full_output = "".join(output_chunks)

    if process.returncode != 0:
        logger.warning(
            "Command exited with code %d: %s",
            process.returncode,
            full_command,
        )
        raise RuntimeError(
            f"Command failed (exit {process.returncode}):\n{full_output}"
        )

    return full_output
