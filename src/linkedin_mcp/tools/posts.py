"""Post tools — create, read, update, delete posts."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _error_response


@mcp.tool()
def create_post(
    commentary: Annotated[str, Field(description="Post text content (max 3000 characters).")],
    visibility: Annotated[str, Field(description="Post visibility: PUBLIC, CONNECTIONS, LOGGED_IN, or CONTAINER.")] = "PUBLIC",
) -> str:
    """Create a simple text post on LinkedIn.

    Args:
        commentary: Post text content (max 3000 characters).
        visibility: Post visibility: PUBLIC, CONNECTIONS, LOGGED_IN, or CONTAINER.
    """
    try:
        result = get_client().create_post(
            commentary=commentary,
            visibility=visibility,
        )
        result["message"] = "Post created successfully"
        result["url"] = f"https://www.linkedin.com/feed/update/{result['postUrn']}"
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def get_my_posts(
    limit: Annotated[int, Field(description="Number of posts to return (max 100).")] = 10,
    offset: Annotated[int, Field(description="Pagination offset.")] = 0,
) -> str:
    """Get the authenticated user's recent posts.

    Args:
        limit: Number of posts to return (max 100).
        offset: Pagination offset.
    """
    try:
        result = get_client().get_my_posts(limit=limit, offset=offset)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def delete_post(
    post_urn: Annotated[str, Field(description="The URN of the post to delete, e.g. urn:li:share:7...")],
) -> str:
    """Delete a LinkedIn post.

    Args:
        post_urn: The URN of the post to delete, e.g. urn:li:share:7...
    """
    try:
        get_client().delete_post(post_urn)
        return json.dumps({
            "postUrn": post_urn,
            "message": "Post deleted successfully",
            "success": True,
        }, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def update_post(
    post_urn: Annotated[str, Field(description="The URN of the post to update.")],
    commentary: Annotated[str | None, Field(description="New post text.")] = None,
    content_call_to_action_label: Annotated[str | None, Field(description="New call-to-action label.")] = None,
    content_landing_page: Annotated[str | None, Field(description="New landing page URL.")] = None,
) -> str:
    """Update an existing LinkedIn post.

    Args:
        post_urn: The URN of the post to update.
        commentary: New post text.
        content_call_to_action_label: New call-to-action label.
        content_landing_page: New landing page URL.
    """
    try:
        get_client().update_post(
            post_urn=post_urn,
            commentary=commentary,
            content_call_to_action_label=content_call_to_action_label,
            content_landing_page=content_landing_page,
        )
        return json.dumps({
            "postUrn": post_urn,
            "message": "Post updated successfully",
            "success": True,
        }, indent=2)
    except Exception as exc:
        return _error_response(exc)
