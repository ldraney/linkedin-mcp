"""Auth tools — OAuth flow and credential management."""

from __future__ import annotations

import json
import os
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, reset_client, _error_response
from ..token_storage import store_credentials, delete_credentials
from linkedin_sdk import LinkedInClient


def _mask_token(token: str) -> str:
    """Mask a token for safe display."""
    if not token or len(token) < 12:
        return "****"
    return f"{token[:4]}...{token[-4:]}"


@mcp.tool()
def get_auth_url(
    client_id: Annotated[str | None, Field(description="LinkedIn app client ID. Falls back to LINKEDIN_CLIENT_ID env var.")] = None,
    redirect_uri: Annotated[str | None, Field(description="OAuth redirect URI. Falls back to LINKEDIN_REDIRECT_URI env var.")] = None,
    scopes: Annotated[list[str] | None, Field(description="OAuth scopes. Defaults to openid, profile, email, w_member_social.")] = None,
) -> str:
    """Get LinkedIn OAuth authorization URL.

    Args:
        client_id: LinkedIn app client ID. Falls back to LINKEDIN_CLIENT_ID env var.
        redirect_uri: OAuth redirect URI. Falls back to LINKEDIN_REDIRECT_URI env var.
        scopes: OAuth scopes. Defaults to openid, profile, email, w_member_social.
    """
    try:
        cid = client_id or os.environ.get("LINKEDIN_CLIENT_ID")
        ruri = redirect_uri or os.environ.get("LINKEDIN_REDIRECT_URI")
        if not cid:
            return json.dumps({"error": True, "message": "client_id or LINKEDIN_CLIENT_ID env var required"})
        if not ruri:
            return json.dumps({"error": True, "message": "redirect_uri or LINKEDIN_REDIRECT_URI env var required"})

        url = LinkedInClient.get_auth_url(
            client_id=cid,
            redirect_uri=ruri,
            scopes=scopes,
        )
        return json.dumps({
            "authUrl": url,
            "instructions": (
                "1. Visit the URL above to authenticate with LinkedIn\n"
                "2. After approval, copy the authorization code from the callback URL\n"
                "3. Use exchange_code to get an access token\n"
                "4. Use save_credentials to store the token in your OS keychain"
            ),
        }, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def exchange_code(
    authorization_code: Annotated[str, Field(description="The authorization code from the OAuth callback URL.")],
    client_id: Annotated[str | None, Field(description="LinkedIn app client ID. Falls back to LINKEDIN_CLIENT_ID env var.")] = None,
    client_secret: Annotated[str | None, Field(description="LinkedIn app client secret. Falls back to LINKEDIN_CLIENT_SECRET env var.")] = None,
    redirect_uri: Annotated[str | None, Field(description="OAuth redirect URI. Falls back to LINKEDIN_REDIRECT_URI env var.")] = None,
) -> str:
    """Exchange OAuth authorization code for access token.

    Args:
        authorization_code: The authorization code from the OAuth callback URL.
        client_id: LinkedIn app client ID. Falls back to LINKEDIN_CLIENT_ID env var.
        client_secret: LinkedIn app client secret. Falls back to LINKEDIN_CLIENT_SECRET env var.
        redirect_uri: OAuth redirect URI. Falls back to LINKEDIN_REDIRECT_URI env var.
    """
    try:
        cid = client_id or os.environ.get("LINKEDIN_CLIENT_ID", "")
        csecret = client_secret or os.environ.get("LINKEDIN_CLIENT_SECRET", "")
        ruri = redirect_uri or os.environ.get("LINKEDIN_REDIRECT_URI", "")

        token_response = LinkedInClient.exchange_code(
            code=authorization_code,
            client_id=cid,
            client_secret=csecret,
            redirect_uri=ruri,
        )

        # Get person ID from userinfo
        temp_client = LinkedInClient(access_token=token_response["access_token"], person_id="temp")
        user_info = temp_client.get_user_info()
        temp_client.close()

        return json.dumps({
            "accessToken": _mask_token(token_response["access_token"]),
            "expiresIn": token_response.get("expires_in"),
            "personId": user_info["sub"],
            "message": (
                f"Token obtained! Use save_credentials to store it securely.\n"
                f"Person ID: {user_info['sub']}"
            ),
        }, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def save_credentials(
    access_token: Annotated[str, Field(description="LinkedIn OAuth access token.")],
    person_id: Annotated[str, Field(description="LinkedIn person ID (the 'sub' field from userinfo).")],
    refresh_token: Annotated[str | None, Field(description="Optional refresh token.")] = None,
) -> str:
    """Save LinkedIn credentials to OS keychain.

    Stores securely in macOS Keychain, Windows Credential Manager, or Linux Secret Service.

    Args:
        access_token: LinkedIn OAuth access token.
        person_id: LinkedIn person ID (the 'sub' field from userinfo).
        refresh_token: Optional refresh token.
    """
    try:
        credentials = {
            "accessToken": access_token,
            "personId": person_id,
            "refreshToken": refresh_token,
        }
        store_credentials(credentials)

        # Reset client so next call picks up new credentials
        reset_client()

        return json.dumps({
            "success": True,
            "accessToken": _mask_token(access_token),
            "personId": person_id,
            "message": "Credentials stored securely in your OS keychain. LinkedIn tools should work now!",
        }, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def refresh_token(
    refresh_token_value: Annotated[str, Field(description="The refresh token to use.")],
    client_id: Annotated[str | None, Field(description="LinkedIn app client ID. Falls back to LINKEDIN_CLIENT_ID env var.")] = None,
    client_secret: Annotated[str | None, Field(description="LinkedIn app client secret. Falls back to LINKEDIN_CLIENT_SECRET env var.")] = None,
) -> str:
    """Refresh an expired LinkedIn access token.

    Args:
        refresh_token_value: The refresh token to use.
        client_id: LinkedIn app client ID. Falls back to LINKEDIN_CLIENT_ID env var.
        client_secret: LinkedIn app client secret. Falls back to LINKEDIN_CLIENT_SECRET env var.
    """
    try:
        cid = client_id or os.environ.get("LINKEDIN_CLIENT_ID", "")
        csecret = client_secret or os.environ.get("LINKEDIN_CLIENT_SECRET", "")

        result = LinkedInClient.refresh_token(
            refresh_token=refresh_token_value,
            client_id=cid,
            client_secret=csecret,
        )

        return json.dumps({
            "accessToken": _mask_token(result["access_token"]),
            "expiresIn": result.get("expires_in"),
            "message": f"Token refreshed! Expires in {result.get('expires_in', 0) // 86400} days.",
        }, indent=2)
    except Exception as exc:
        return _error_response(exc)
