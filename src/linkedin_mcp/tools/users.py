"""User tools — get profile information."""

from __future__ import annotations

import json
from typing import Annotated

from ..server import mcp, get_client, _error_response


@mcp.tool()
def get_user_info() -> str:
    """Get the authenticated user's profile information."""
    try:
        info = get_client().get_user_info()
        return json.dumps({
            "personUrn": f"urn:li:person:{info.get('sub', '')}",
            "name": info.get("name", ""),
            "email": info.get("email", ""),
            "pictureUrl": info.get("picture", ""),
        }, indent=2)
    except Exception as exc:
        return _error_response(exc)
