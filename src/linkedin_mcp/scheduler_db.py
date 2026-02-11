"""SQLite-based storage for scheduled LinkedIn posts."""

from __future__ import annotations

import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

DB_DIR = os.path.join(os.path.expanduser("~"), ".linkedin-mcp")
DB_PATH = os.path.join(DB_DIR, "scheduled.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS scheduled_posts (
    id TEXT PRIMARY KEY,
    commentary TEXT NOT NULL,
    url TEXT,
    visibility TEXT NOT NULL DEFAULT 'PUBLIC',
    scheduled_time TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    published_at TEXT,
    post_urn TEXT,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0
);
"""


class ScheduledPostsDB:
    """SQLite-backed scheduled posts storage."""

    def __init__(self, db_path: str = DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def add(
        self,
        commentary: str,
        scheduled_time: str,
        url: str | None = None,
        visibility: str = "PUBLIC",
    ) -> dict[str, Any]:
        post_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """INSERT INTO scheduled_posts
               (id, commentary, url, visibility, scheduled_time, status, created_at, retry_count)
               VALUES (?, ?, ?, ?, ?, 'pending', ?, 0)""",
            (post_id, commentary, url, visibility, scheduled_time, created_at),
        )
        self._conn.commit()
        return self.get(post_id)  # type: ignore

    def get(self, post_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT * FROM scheduled_posts WHERE id = ?", (post_id,)
        ).fetchone()
        return dict(row) if row else None

    def list(
        self, status: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        if status:
            rows = self._conn.execute(
                "SELECT * FROM scheduled_posts WHERE status = ? ORDER BY scheduled_time ASC LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM scheduled_posts ORDER BY scheduled_time ASC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_due(self) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        rows = self._conn.execute(
            "SELECT * FROM scheduled_posts WHERE status = 'pending' AND scheduled_time <= ? ORDER BY scheduled_time ASC",
            (now,),
        ).fetchall()
        return [dict(r) for r in rows]

    def mark_published(self, post_id: str, post_urn: str) -> dict[str, Any] | None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "UPDATE scheduled_posts SET status = 'published', published_at = ?, post_urn = ? WHERE id = ?",
            (now, post_urn, post_id),
        )
        self._conn.commit()
        return self.get(post_id)

    def mark_failed(self, post_id: str, error_message: str) -> dict[str, Any] | None:
        self._conn.execute(
            "UPDATE scheduled_posts SET status = 'failed', error_message = ?, retry_count = retry_count + 1 WHERE id = ?",
            (error_message, post_id),
        )
        self._conn.commit()
        return self.get(post_id)

    def cancel(self, post_id: str) -> dict[str, Any] | None:
        row = self.get(post_id)
        if not row or row["status"] != "pending":
            return None
        self._conn.execute(
            "UPDATE scheduled_posts SET status = 'cancelled' WHERE id = ?",
            (post_id,),
        )
        self._conn.commit()
        return self.get(post_id)

    def close(self) -> None:
        self._conn.close()


# Singleton
_db: ScheduledPostsDB | None = None


def get_db(db_path: str = DB_PATH) -> ScheduledPostsDB:
    global _db
    if _db is None:
        _db = ScheduledPostsDB(db_path)
    return _db


def run_scheduler() -> None:
    """Entry point for the linkedin-mcp-scheduler console script.

    Checks for due posts and publishes them.
    """
    from linkedin_sdk import LinkedInClient

    from .token_storage import get_credentials

    db = get_db()
    due = db.get_due()

    if not due:
        print("No posts due for publishing.")
        return

    creds = get_credentials()
    if creds:
        client = LinkedInClient(
            access_token=creds.get("accessToken"),
            person_id=creds.get("personId"),
        )
    else:
        client = LinkedInClient()
    for post in due:
        try:
            result = client.create_post(
                commentary=post["commentary"],
                visibility=post["visibility"],
            )
            db.mark_published(post["id"], result["postUrn"])
            print(f"Published: {post['id']} -> {result['postUrn']}")
        except Exception as e:
            db.mark_failed(post["id"], str(e))
            print(f"Failed: {post['id']} -> {e}")
