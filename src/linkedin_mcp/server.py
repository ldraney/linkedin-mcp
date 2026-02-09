"""MCP server entry point — FastMCP app and LinkedInClient lifecycle."""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from linkedin_sdk import LinkedInClient

from .token_storage import get_credentials

mcp = FastMCP("linkedin")

# ---------------------------------------------------------------------------
# Shared client instance
# ---------------------------------------------------------------------------

_client: LinkedInClient | None = None


def get_client() -> LinkedInClient:
    """Return the shared LinkedInClient, creating it on first call.

    Reads credentials from OS keychain first, falls back to env vars.
    """
    global _client
    if _client is None:
        creds = get_credentials()
        if creds:
            _client = LinkedInClient(
                access_token=creds.get("accessToken"),
                person_id=creds.get("personId"),
            )
        else:
            _client = LinkedInClient()
    return _client


def reset_client() -> None:
    """Reset the shared client (used after credential changes)."""
    global _client
    if _client is not None:
        _client.close()
    _client = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_json(value: str | dict | list | None, name: str) -> Any:
    """Parse a JSON string into a Python object, or pass through if already parsed."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON for parameter '{name}': {exc}") from exc


def _error_response(exc: Exception) -> str:
    """Format an exception into a user-friendly error string."""
    if isinstance(exc, httpx.HTTPStatusError):
        try:
            body = exc.response.json()
        except Exception:
            body = exc.response.text
        return json.dumps(
            {
                "error": True,
                "status_code": exc.response.status_code,
                "message": str(exc),
                "details": body,
            },
            indent=2,
        )
    return json.dumps({"error": True, "message": str(exc)}, indent=2)


# ---------------------------------------------------------------------------
# Register tool modules — each module calls @mcp.tool() at import time
# ---------------------------------------------------------------------------

from .tools import register_all_tools  # noqa: E402

register_all_tools()


def main() -> None:
    """Entry point for the console script."""
    mcp.run()
