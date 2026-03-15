"""Async HTTP client for the RAG service."""

from __future__ import annotations

import httpx

from shared.config import get_settings

_TIMEOUT = httpx.Timeout(30.0, connect=5.0)


async def search_rag(query: str) -> str:
    """Send a query to the RAG service and return matching passages."""
    settings = get_settings()
    url = f"{settings.rag_service_url}/rag/query"
    payload = {"query": query}

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(url, json=payload)

    if resp.status_code != 200:
        return f"RAG service error ({resp.status_code}): {resp.text}"

    data = resp.json()
    results = data.get("results", [])
    if not results:
        return data.get("message", "No documents found matching your query.")

    # Format results into a readable string for the LLM
    parts: list[str] = []
    for i, result in enumerate(results, 1):
        source = result.get("source", "unknown")
        text = result.get("text", "")
        parts.append(f"[{i}] (source: {source})\n{text}")
    return "\n\n".join(parts)
