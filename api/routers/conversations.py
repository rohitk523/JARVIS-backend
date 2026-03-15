"""Conversation history endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.deps import get_current_user
from shared.supabase_client import get_supabase_client

router = APIRouter()

_CONVERSATIONS = "conversations"
_MESSAGES = "conversation_messages"


class ConversationCreate(BaseModel):
    title: str = "New Conversation"


@router.get("")
async def list_conversations(
    user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Return all conversations for the current user, newest first."""
    user_id: str = user["sub"]
    sb = get_supabase_client()
    result = (
        sb.table(_CONVERSATIONS)
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Return a conversation together with its messages."""
    user_id: str = user["sub"]
    sb = get_supabase_client()

    conv_result = (
        sb.table(_CONVERSATIONS)
        .select("*")
        .eq("id", conversation_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not conv_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages_result = (
        sb.table(_MESSAGES)
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .execute()
    )

    return {
        **conv_result.data,
        "messages": messages_result.data,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    body: ConversationCreate,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Create a new conversation for the authenticated user."""
    user_id: str = user["sub"]
    sb = get_supabase_client()
    result = (
        sb.table(_CONVERSATIONS)
        .insert({"user_id": user_id, "title": body.title})
        .execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation",
        )
    return result.data[0]
