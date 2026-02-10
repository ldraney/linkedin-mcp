# linkedin-mcp

MCP server for the LinkedIn API v202510 — create posts, upload media, manage engagement, and schedule content.

## Why this server?

There are several LinkedIn MCP servers on GitHub (10+ at time of writing). Most fall into two camps: **scraper-based** servers that use browser automation / scraping (e.g. [adhikasp/mcp-linkedin](https://github.com/adhikasp/mcp-linkedin), [stickerdaniel/linkedin-mcp-server](https://github.com/stickerdaniel/linkedin-mcp-server), [alinaqi/mcp-linkedin-server](https://github.com/alinaqi/mcp-linkedin-server)), and **official-API** servers that only expose a handful of tools (e.g. [fredericbarthelet/linkedin-mcp-server](https://github.com/fredericbarthelet/linkedin-mcp-server) with 2 tools). This project takes a different approach: it uses the official LinkedIn API exclusively, covers a broad set of content-management and scheduling endpoints, and stores credentials securely.

- **Full OAuth 2.0 flow with OS keychain storage** — tokens are stored in macOS Keychain, Windows Credential Manager, or Linux Secret Service via [keyring](https://pypi.org/project/keyring/). No plaintext tokens in config files.
- **21 tools across 6 categories** — posts, 6 media types (link, image, multi-image, document, video, poll), engagement (comments + reactions), scheduling, user info, and auth. Most competing servers cover only a subset of these.
- **Pinned to LinkedIn API v202510** — LinkedIn's v202601 release moved `get_my_posts`, `add_comment`, and `add_reaction` to partner-only access. This server pins to v202510 where those endpoints still work with standard OAuth tokens.
- **Built-in post scheduler** — SQLite-backed queue for scheduling future posts, with tools to list, inspect, and cancel scheduled items.
- **One-click `.mcpb` install** — ships a pre-built Claude Desktop extension so non-technical users can install without touching a terminal.

## Installation

### Claude Desktop (one-click)

Download the `.mcpb` extension from the [latest release](https://github.com/ldraney/linkedin-mcp/releases/latest/download/ldraney-linkedin-mcp.mcpb) and double-click to install.

### Manual

```bash
uvx ldraney-linkedin-mcp
```

Or add to your Claude Code config:

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "uvx",
      "args": ["ldraney-linkedin-mcp"],
      "env": {
        "LINKEDIN_ACCESS_TOKEN": "your_token",
        "LINKEDIN_PERSON_ID": "your_person_id"
      }
    }
  }
}
```

## Authentication

The server supports multiple authentication methods:

1. **Environment variables**: Set `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_PERSON_ID`
2. **OS Keychain**: Use the `save_credentials` tool to store credentials securely
3. **OAuth flow**: Use `get_auth_url` to start the OAuth flow

## Tools (21)

### Auth (4)
- `get_auth_url` — Get LinkedIn OAuth authorization URL
- `exchange_code` — Exchange OAuth code for access token
- `save_credentials` — Save credentials to OS keychain
- `refresh_token` — Refresh an expired token

### Posts (4)
- `create_post` — Create a text post
- `get_my_posts` — List your recent posts
- `delete_post` — Delete a post
- `update_post` — Update a post

### Media (6)
- `create_post_with_link` — Post with article preview
- `create_post_with_image` — Post with image
- `create_post_with_document` — Post with PDF/DOC/PPT
- `create_post_with_video` — Post with video
- `create_poll` — Create a poll
- `create_post_with_multi_images` — Post with multiple images

### Engagement (2)
- `add_comment` — Comment on a post
- `add_reaction` — React to a post

### Users (1)
- `get_user_info` — Get your profile info

### Scheduler (4)
- `schedule_post` — Schedule a future post
- `list_scheduled_posts` — List scheduled posts
- `cancel_scheduled_post` — Cancel a scheduled post
- `get_scheduled_post` — Get scheduled post details

## License

MIT
