# linkedin-mcp

MCP server for the LinkedIn API v202510 — create posts, upload media, manage engagement, and schedule content.

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
