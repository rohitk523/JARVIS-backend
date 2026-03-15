"""Document upload and management endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from api.deps import get_current_user
from shared.supabase_client import get_supabase_client

router = APIRouter()

_TABLE = "documents"
_BUCKET = "documents"


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Upload a document to Supabase Storage and record metadata."""
    user_id: str = user["sub"]
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    sb = get_supabase_client()
    content = await file.read()
    storage_path = f"{user_id}/{file.filename}"

    # Upload file to Supabase Storage
    sb.storage.from_(_BUCKET).upload(
        path=storage_path,
        file=content,
        file_options={"content-type": file.content_type or "application/octet-stream"},
    )

    # Record metadata in the documents table
    metadata = {
        "user_id": user_id,
        "filename": file.filename,
        "storage_path": storage_path,
        "content_type": file.content_type or "application/octet-stream",
        "size_bytes": len(content),
        "chunk_count": 0,
    }
    result = sb.table(_TABLE).insert(metadata).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record document metadata",
        )
    return result.data[0]


@router.get("")
async def list_documents(
    user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """List all documents uploaded by the current user."""
    user_id: str = user["sub"]
    sb = get_supabase_client()
    result = (
        sb.table(_TABLE)
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    user: dict[str, Any] = Depends(get_current_user),
) -> None:
    """Delete a document from storage and remove its metadata row."""
    user_id: str = user["sub"]
    sb = get_supabase_client()

    # Fetch the document first to get the storage path
    result = (
        sb.table(_TABLE)
        .select("storage_path")
        .eq("id", document_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    storage_path: str = result.data["storage_path"]

    # Remove from storage
    sb.storage.from_(_BUCKET).remove([storage_path])

    # Remove metadata row
    sb.table(_TABLE).delete().eq("id", document_id).eq("user_id", user_id).execute()
