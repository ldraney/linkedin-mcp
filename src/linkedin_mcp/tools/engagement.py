"""Engagement tools — comments and reactions."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _error_response


@mcp.tool()
def add_comment(
    post_urn: Annotated[str, Field(description="The URN of the post to comment on.")],
    text: Annotated[str, Field(description="Comment text (max 1250 characters).")],
) -> str:
    """Add a comment to a LinkedIn post.

    Args:
        post_urn: The URN of the post to comment on.
        text: Comment text (max 1250 characters).
    """
    try:
        result = get_client().add_comment(post_urn=post_urn, text=text)
        result["postUrn"] = post_urn
        result["message"] = "Comment added successfully"
        result["success"] = True
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def add_reaction(
    post_urn: Annotated[str, Field(description="The URN of the post to react to.")],
    reaction_type: Annotated[str, Field(description="Reaction type: LIKE, PRAISE, EMPATHY, INTEREST, APPRECIATION, or ENTERTAINMENT.")],
) -> str:
    """Add a reaction to a LinkedIn post.

    Args:
        post_urn: The URN of the post to react to.
        reaction_type: Reaction type: LIKE, PRAISE, EMPATHY, INTEREST, APPRECIATION, or ENTERTAINMENT.
    """
    try:
        get_client().add_reaction(post_urn=post_urn, reaction_type=reaction_type)
        return json.dumps({
            "postUrn": post_urn,
            "reactionType": reaction_type,
            "message": f"Reaction {reaction_type} added successfully",
            "success": True,
        }, indent=2)
    except Exception as exc:
        return _error_response(exc)
