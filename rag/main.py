"""RAG service — FastAPI application (port 8003).

Phase 0: stub implementation.  Returns placeholder responses while the
embedding pipeline and vector search are built out.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from rag.db import ensure_schema
from rag.ingest import ingest_document
from rag.search import search_documents

app = FastAPI(
    title="JARVIS RAG Service",
    version="0.1.0",
)


@app.on_event("startup")
async def startup() -> None:
    ensure_schema()


# ── Schemas ───────────────────────────────────────────────────────────────────


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class QueryResponse(BaseModel):
    message: str
    results: list[dict[str, Any]]


class IngestRequest(BaseModel):
    document_id: str
    content: str
    metadata: dict[str, Any] = {}


class IngestResponse(BaseModel):
    message: str
    chunks: int


# ── Endpoints ─────────────────────────────────────────────────────────────────


@app.post("/rag/query", response_model=QueryResponse)
async def query(body: QueryRequest) -> QueryResponse:
    """Search indexed documents for passages matching the query."""
    results = search_documents(body.query, top_k=body.top_k)
    message = (
        f"Found {len(results)} result(s)."
        if results
        else "No documents indexed yet."
    )
    return QueryResponse(message=message, results=results)


@app.post("/rag/ingest", response_model=IngestResponse)
async def ingest(body: IngestRequest) -> IngestResponse:
    """Ingest a document: chunk, embed, and store."""
    chunk_count = ingest_document(
        document_id=body.document_id,
        content=body.content,
        metadata=body.metadata,
    )
    return IngestResponse(
        message=f"Ingested {chunk_count} chunk(s) for document {body.document_id}.",
        chunks=chunk_count,
    )


@app.get("/rag/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "rag"}
