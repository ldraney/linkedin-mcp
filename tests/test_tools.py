"""Mock-based tests for LinkedIn MCP tools."""

from __future__ import annotations

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_client():
    """Provide a mocked LinkedInClient for all tests.

    We patch get_client at every location it's imported into.
    """
    mock = MagicMock()
    mock.person_urn = "urn:li:person:test123"
    mock.person_id = "test123"
    mock.access_token = "test_token"

    # Patch in every module that imports get_client from server
    with (
        patch("linkedin_mcp.server.get_client", return_value=mock),
        patch("linkedin_mcp.tools.posts.get_client", return_value=mock),
        patch("linkedin_mcp.tools.media.get_client", return_value=mock),
        patch("linkedin_mcp.tools.engagement.get_client", return_value=mock),
        patch("linkedin_mcp.tools.users.get_client", return_value=mock),
    ):
        yield mock


def test_create_post(mock_client):
    from linkedin_mcp.tools.posts import create_post

    mock_client.create_post.return_value = {
        "postUrn": "urn:li:share:123",
        "statusCode": 201,
    }

    result = json.loads(create_post("Hello LinkedIn!"))
    assert result["postUrn"] == "urn:li:share:123"
    assert result["message"] == "Post created successfully"
    assert "url" in result
    mock_client.create_post.assert_called_once_with(
        commentary="Hello LinkedIn!",
        visibility="PUBLIC",
    )


def test_get_my_posts(mock_client):
    from linkedin_mcp.tools.posts import get_my_posts

    mock_client.get_my_posts.return_value = {
        "elements": [{"id": "urn:li:share:1"}],
        "paging": {"count": 1, "start": 0},
    }

    result = json.loads(get_my_posts(limit=5, offset=0))
    assert len(result["elements"]) == 1
    mock_client.get_my_posts.assert_called_once_with(limit=5, offset=0)


def test_delete_post(mock_client):
    from linkedin_mcp.tools.posts import delete_post

    mock_client.delete_post.return_value = 204

    result = json.loads(delete_post("urn:li:share:123"))
    assert result["success"] is True
    assert result["message"] == "Post deleted successfully"


def test_update_post(mock_client):
    from linkedin_mcp.tools.posts import update_post

    mock_client.update_post.return_value = 200

    result = json.loads(update_post("urn:li:share:123", commentary="Updated text"))
    assert result["success"] is True


def test_create_post_with_link(mock_client):
    from linkedin_mcp.tools.media import create_post_with_link

    mock_client.create_post_with_link.return_value = {
        "postUrn": "urn:li:share:456",
        "statusCode": 201,
    }

    result = json.loads(
        create_post_with_link("Check this out", "https://example.com", title="Example")
    )
    assert result["postUrn"] == "urn:li:share:456"


def test_add_comment(mock_client):
    from linkedin_mcp.tools.engagement import add_comment

    mock_client.add_comment.return_value = {
        "commentUrn": "urn:li:comment:789",
        "statusCode": 201,
    }

    result = json.loads(add_comment("urn:li:share:123", "Great post!"))
    assert result["commentUrn"] == "urn:li:comment:789"
    assert result["success"] is True


def test_add_reaction(mock_client):
    from linkedin_mcp.tools.engagement import add_reaction

    mock_client.add_reaction.return_value = 200

    result = json.loads(add_reaction("urn:li:share:123", "LIKE"))
    assert result["success"] is True
    assert result["reactionType"] == "LIKE"


def test_get_user_info(mock_client):
    from linkedin_mcp.tools.users import get_user_info

    mock_client.get_user_info.return_value = {
        "sub": "test123",
        "name": "Test User",
        "email": "test@example.com",
        "picture": "https://example.com/photo.jpg",
    }

    result = json.loads(get_user_info())
    assert result["personUrn"] == "urn:li:person:test123"
    assert result["name"] == "Test User"


def test_get_auth_url():
    from linkedin_mcp.tools.auth import get_auth_url

    with patch.dict(os.environ, {
        "LINKEDIN_CLIENT_ID": "test_client_id",
        "LINKEDIN_REDIRECT_URI": "http://localhost:8080/callback",
    }):
        result = json.loads(get_auth_url())
        assert "authUrl" in result
        assert "linkedin.com" in result["authUrl"]
        assert "test_client_id" in result["authUrl"]


def test_error_handling(mock_client):
    from linkedin_mcp.tools.posts import create_post

    mock_client.create_post.side_effect = ValueError("Something went wrong")

    result = json.loads(create_post("test"))
    assert result["error"] is True
    assert "Something went wrong" in result["message"]


def test_scheduler_db():
    """Test scheduler DB operations with a temp database."""
    from linkedin_mcp.scheduler_db import ScheduledPostsDB

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        db = ScheduledPostsDB(db_path)

        # Add a post
        post = db.add(
            commentary="Test scheduled post",
            scheduled_time="2099-12-31T23:59:59Z",
            visibility="PUBLIC",
        )
        assert post["commentary"] == "Test scheduled post"
        assert post["status"] == "pending"

        # Get it back
        fetched = db.get(post["id"])
        assert fetched is not None
        assert fetched["id"] == post["id"]

        # List posts
        posts = db.list()
        assert len(posts) == 1

        # Cancel
        cancelled = db.cancel(post["id"])
        assert cancelled["status"] == "cancelled"

        # Can't cancel again
        assert db.cancel(post["id"]) is None

        db.close()
    finally:
        os.unlink(db_path)


def test_create_poll(mock_client):
    from linkedin_mcp.tools.media import create_poll

    mock_client.create_poll.return_value = {
        "postUrn": "urn:li:share:poll123",
        "statusCode": 201,
    }

    result = json.loads(create_poll("Best language?", '["Python", "Rust", "Go"]'))
    assert result["postUrn"] == "urn:li:share:poll123"
