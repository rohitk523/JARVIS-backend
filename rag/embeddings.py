"""Embedding wrapper — stub for Gemini Embedding API.

Phase 0: returns zero vectors.  Will be replaced with real embeddings
once the Gemini embedding endpoint is integrated.
"""

from __future__ import annotations

import logging
from typing import Sequence

logger = logging.getLogger("jarvis.rag.embeddings")

_EMBEDDING_DIM = 768  # Gemini text-embedding-004 dimension


async def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    """Return embedding vectors for each text.

    Phase 0 stub: returns zero-vectors of the expected dimensionality.
    """
    logger.info("embed_texts called with %d text(s) — returning zero vectors (stub)", len(texts))
    return [[0.0] * _EMBEDDING_DIM for _ in texts]


async def embed_query(query: str) -> list[float]:
    """Return an embedding vector for a single search query."""
    results = await embed_texts([query])
    return results[0]
