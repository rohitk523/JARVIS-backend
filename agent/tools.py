"""Function tools exposed to the LLM via livekit-agents function calling."""

from __future__ import annotations

import logging
from typing import Annotated

from livekit.agents import llm

from agent.clients.cli_client import run_remote_cli_task
from agent.clients.mcp_client import invoke_mcp_tool
from agent.clients.rag_client import search_rag

logger = logging.getLogger("jarvis.tools")


def register_tools(fnc_ctx: llm.FunctionContext) -> None:
    """Register all JARVIS tools onto the given FunctionContext."""

    @fnc_ctx.ai_callable(
        description=(
            "Search the user's uploaded documents for information relevant to "
            "the given query.  Returns the most relevant passages."
        ),
    )
    async def search_documents(
        query: Annotated[str, llm.TypeInfo(description="Natural-language search query")],
    ) -> str:
        logger.info("search_documents called — query=%s", query)
        result = await search_rag(query)
        return result

    @fnc_ctx.ai_callable(
        description=(
            "Invoke a tool on a remote MCP server (e.g. Linear, GitHub). "
            "Specify the server name, tool name, and a JSON-encoded arguments string."
        ),
    )
    async def use_mcp_tool(
        server_name: Annotated[str, llm.TypeInfo(description="MCP server name, e.g. 'linear'")],
        tool_name: Annotated[str, llm.TypeInfo(description="Tool name on the MCP server")],
        arguments: Annotated[str, llm.TypeInfo(description="JSON-encoded arguments for the tool")],
    ) -> str:
        logger.info(
            "use_mcp_tool called — server=%s tool=%s",
            server_name,
            tool_name,
        )
        result = await invoke_mcp_tool(server_name, tool_name, arguments)
        return result

    @fnc_ctx.ai_callable(
        description=(
            "Run an approved CLI command (e.g. Gemini CLI). "
            "Returns the command output."
        ),
    )
    async def run_cli_task(
        tool_name: Annotated[str, llm.TypeInfo(description="CLI tool name, e.g. 'gemini'")],
        command: Annotated[str, llm.TypeInfo(description="The full command string to execute")],
    ) -> str:
        logger.info("run_cli_task called — tool=%s command=%s", tool_name, command)
        result = await run_remote_cli_task(tool_name, command)
        return result
