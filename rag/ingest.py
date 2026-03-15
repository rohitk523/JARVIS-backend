"""Document ingestion — Phase 0 stub.

Logs the receipt of a document but does not perform chunking or
embedding.  Will be fully implemented when the embedding pipeline
is ready.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("jarvis.rag.ingest")


def ingest_document(
    document_id: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> int:
    """Ingest a document: chunk, embed, and store in the vector DB.

    Phase 0: logs receipt and returns 0 chunks processed.

    Returns
    -------
    int
        Number of chunks created (0 in stub).
    """
    logger.info(
        "ingest_document stub called — document_id=%s content_length=%d metadata=%s",
        document_id,
        len(content),
        metadata,
    )
    return 0
