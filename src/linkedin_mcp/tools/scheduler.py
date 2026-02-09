"""Scheduler tools — schedule, list, cancel, and get scheduled posts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Annotated

from pydantic import Field

from ..server import mcp, _error_response
from ..scheduler_db import get_db


@mcp.tool()
def schedule_post(
    commentary: Annotated[str, Field(description="Post text content (max 3000 characters).")],
    scheduled_time: Annotated[str, Field(description="ISO 8601 datetime for when to publish, e.g. 2026-02-10T14:00:00Z. Must be in the future.")],
    url: Annotated[str | None, Field(description="Optional article URL to attach.")] = None,
    visibility: Annotated[str, Field(description="Post visibility: PUBLIC, CONNECTIONS, LOGGED_IN, or CONTAINER.")] = "PUBLIC",
) -> str:
    """Schedule a LinkedIn post for future publication.

    IMPORTANT: Run `linkedin-mcp-scheduler` periodically (e.g. via cron) to publish due posts.

    Args:
        commentary: Post text content (max 3000 characters).
        scheduled_time: ISO 8601 datetime for when to publish. Must be in the future.
        url: Optional article URL to attach.
        visibility: Post visibility.
    """
    try:
        # Validate future time
        scheduled_dt = datetime.fromisoformat(scheduled_time.replace("Z", "+00:00"))
        if scheduled_dt <= datetime.now(timezone.utc):
            return json.dumps({"error": True, "message": "scheduled_time must be in the future"})

        db = get_db()
        post = db.add(
            commentary=commentary,
            scheduled_time=scheduled_time,
            url=url,
            visibility=visibility,
        )
        return json.dumps({
            "postId": post["id"],
            "scheduledTime": post["scheduled_time"],
            "status": post["status"],
            "message": f"Post scheduled for {scheduled_time}",
        }, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def list_scheduled_posts(
    status: Annotated[str | None, Field(description="Filter by status: pending, published, failed, or cancelled.")] = None,
    limit: Annotated[int, Field(description="Maximum number of posts to return.")] = 50,
) -> str:
    """List scheduled posts, optionally filtered by status.

    Args:
        status: Filter by status: pending, published, failed, or cancelled.
        limit: Maximum number of posts to return.
    """
    try:
        db = get_db()
        posts = db.list(status=status, limit=limit)
        return json.dumps({
            "posts": posts,
            "count": len(posts),
            "message": f"Found {len(posts)} {status or 'all'} scheduled posts",
        }, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def cancel_scheduled_post(
    post_id: Annotated[str, Field(description="The UUID of the scheduled post to cancel.")],
) -> str:
    """Cancel a scheduled post (must be in pending status).

    Args:
        post_id: The UUID of the scheduled post to cancel.
    """
    try:
        db = get_db()
        result = db.cancel(post_id)
        if not result:
            return json.dumps({"error": True, "message": f"Post not found or not in pending status: {post_id}"})
        return json.dumps({
            "postId": result["id"],
            "status": "cancelled",
            "message": "Scheduled post cancelled successfully",
            "success": True,
        }, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def get_scheduled_post(
    post_id: Annotated[str, Field(description="The UUID of the scheduled post to retrieve.")],
) -> str:
    """Get details of a scheduled post.

    Args:
        post_id: The UUID of the scheduled post to retrieve.
    """
    try:
        db = get_db()
        post = db.get(post_id)
        if not post:
            return json.dumps({"error": True, "message": f"Scheduled post not found: {post_id}"})
        return json.dumps({
            "post": post,
            "message": f"Status: {post['status']}",
        }, indent=2)
    except Exception as exc:
        return _error_response(exc)
