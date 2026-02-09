"""Token storage using OS keychain via Python keyring.

Stores OAuth credentials securely in:
- macOS: Keychain
- Windows: Credential Manager
- Linux: Secret Service (requires libsecret)
"""

from __future__ import annotations

import json
from typing import Any

import keyring

SERVICE_NAME = "linkedin-mcp"
ACCOUNT_NAME = "oauth-credentials"


def store_credentials(credentials: dict[str, Any]) -> None:
    """Store OAuth credentials in OS keychain."""
    keyring.set_password(SERVICE_NAME, ACCOUNT_NAME, json.dumps(credentials))


def get_credentials() -> dict[str, Any] | None:
    """Retrieve OAuth credentials from OS keychain."""
    try:
        data = keyring.get_password(SERVICE_NAME, ACCOUNT_NAME)
        return json.loads(data) if data else None
    except Exception:
        return None


def delete_credentials() -> bool:
    """Delete OAuth credentials from OS keychain."""
    try:
        keyring.delete_password(SERVICE_NAME, ACCOUNT_NAME)
        return True
    except Exception:
        return False


def has_credentials() -> bool:
    """Check if credentials exist in keychain."""
    return get_credentials() is not None
