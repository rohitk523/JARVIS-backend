"""SQLite + sqlite-vec schema management for the RAG service."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger("jarvis.rag.db")

DB_PATH = Path("data/rag.db")


def _get_connection() -> sqlite3.Connection:
    """Return a connection to the local SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema() -> None:
    """Create tables if they do not exist.

    NOTE: The ``embeddings`` table uses a BLOB column for the vector.
    Once sqlite-vec is available it will be swapped for a virtual table
    with ``vec0`` module.
    """
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id          TEXT PRIMARY KEY,
            filename    TEXT NOT NULL,
            content     TEXT NOT NULL DEFAULT '',
            metadata    TEXT NOT NULL DEFAULT '{}',
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS chunks (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id     TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index     INTEGER NOT NULL,
            text            TEXT NOT NULL,
            embedding       BLOB,
            created_at      TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id);
        """
    )

    conn.commit()
    conn.close()
    logger.info("RAG schema ensured at %s", DB_PATH)
