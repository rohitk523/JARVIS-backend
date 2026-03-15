"""Document search — Phase 0 stub.

Returns an empty result set for all queries.  Will be replaced with
vector similarity search once embeddings and sqlite-vec are wired up.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("jarvis.rag.search")


def search_documents(
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Search indexed documents for relevant passages.

    Phase 0: always returns an empty list.
    """
    logger.info("search_documents stub called — query=%s top_k=%d", query, top_k)
    return []
