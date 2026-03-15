"""JARVIS API — main FastAPI application (port 8000)."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import (
    auth,
    conversations,
    documents,
    health,
    integrations,
    livekit,
    settings,
)
from shared.redis_client import close_redis_client


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown lifecycle hook."""
    yield
    await close_redis_client()


app = FastAPI(
    title="JARVIS API",
    version="0.1.0",
    description="Voice-first AI agent — REST API gateway",
    lifespan=lifespan,
)

# ── CORS (permissive for development) ────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(livekit.router, prefix="/livekit", tags=["livekit"])
app.include_router(settings.router, prefix="/settings", tags=["settings"])
app.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
