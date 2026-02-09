# Development Guide

## Project Structure

```
src/linkedin_mcp/
  server.py            # FastMCP server entry point (main())
  token_storage.py     # keyring-based credential storage
  scheduler_db.py      # SQLite storage for scheduled posts
  tools/
    auth.py            # get_auth_url, exchange_code, save_credentials, refresh_token
    posts.py           # create_post, get_my_posts, delete_post, update_post
    media.py           # create_post_with_link/image/doc/video/poll/multi_images
    engagement.py      # add_comment, add_reaction
    users.py           # get_user_info
    scheduler.py       # schedule_post, list_scheduled, cancel_scheduled, get_scheduled
manifest.json          # .mcpb desktop extension
```

## Setup

```bash
# Install dependencies
uv sync

# Run the server locally
export LINKEDIN_ACCESS_TOKEN="..."
export LINKEDIN_PERSON_ID="..."
uv run python -m linkedin_mcp

# Run tests
uv run pytest
```

## Adding/Modifying Tools

Each tool module in `src/linkedin_mcp/tools/` maps to SDK methods. When adding a tool:

1. Use `@mcp.tool()` decorator
2. Parameters must use `Annotated[type, Field(description=...)]` — FastMCP only puts descriptions in JSON schema from this pattern
3. Accept `str | dict` / `str | list` for structured params — use `_parse_json()` helper
4. Register the tool module in `tools/__init__.py`

## Releasing

CI auto-publishes on push to `main` when the version is bumped.

1. Bump version in **both** `pyproject.toml` and `manifest.json` (CI fails if they differ)
2. Push to `main`
3. CI: publish to PyPI (OIDC) -> build `.mcpb` -> create GitHub Release

Download link (always latest): `https://github.com/ldraney/linkedin-mcp/releases/latest/download/ldraney-linkedin-mcp.mcpb`
