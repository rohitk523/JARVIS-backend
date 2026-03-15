"""Shared Pydantic models used across all JARVIS backend services."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Users ─────────────────────────────────────────────────────────────────────


class UserProfile(BaseModel):
    """Public-facing user profile."""

    id: str
    email: str
    full_name: str = ""
    avatar_url: str = ""
    created_at: datetime


# ── Integrations ──────────────────────────────────────────────────────────────


class Integration(BaseModel):
    """Third-party integration record (e.g. Linear, GitHub)."""

    id: str
    user_id: str
    provider: str
    access_token: str
    refresh_token: str | None = None
    expires_at: datetime | None = None
    created_at: datetime


# ── Conversations ─────────────────────────────────────────────────────────────


class Conversation(BaseModel):
    """A conversation (session) between a user and JARVIS."""

    id: str
    user_id: str
    title: str = "New Conversation"
    created_at: datetime


class ConversationMessage(BaseModel):
    """A single message within a conversation."""

    id: str
    conversation_id: str
    role: str  # "user" | "assistant" | "system" | "tool"
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    created_at: datetime


# ── Documents / RAG ──────────────────────────────────────────────────────────


class Document(BaseModel):
    """Metadata for a user-uploaded document stored in Supabase Storage."""

    id: str
    user_id: str
    filename: str
    storage_path: str
    content_type: str = "application/octet-stream"
    size_bytes: int = 0
    chunk_count: int = 0
    created_at: datetime


# ── CLI Bridge ────────────────────────────────────────────────────────────────


class CLIJob(BaseModel):
    """Record of a CLI command execution."""

    id: str
    user_id: str
    tool_name: str
    command: str
    status: str = "pending"  # pending | running | completed | failed
    output: str = ""
    created_at: datetime


# ── MCP ───────────────────────────────────────────────────────────────────────


class MCPToolCall(BaseModel):
    """Request payload when invoking an MCP tool."""

    server_name: str
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class MCPToolResult(BaseModel):
    """Result returned after invoking an MCP tool."""

    content: str
    is_error: bool = False
