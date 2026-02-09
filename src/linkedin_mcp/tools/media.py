"""Media tools — create posts with images, documents, videos, links, polls."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _parse_json, _error_response


@mcp.tool()
def create_post_with_link(
    commentary: Annotated[str, Field(description="Post text content.")],
    url: Annotated[str, Field(description="Article URL to attach.")],
    title: Annotated[str | None, Field(description="Article title (defaults to URL).")] = None,
    description: Annotated[str | None, Field(description="Article description.")] = None,
    visibility: Annotated[str, Field(description="Post visibility: PUBLIC, CONNECTIONS, LOGGED_IN, or CONTAINER.")] = "PUBLIC",
) -> str:
    """Create a post with an article link preview.

    Args:
        commentary: Post text content.
        url: Article URL to attach.
        title: Article title (defaults to URL).
        description: Article description.
        visibility: Post visibility.
    """
    try:
        result = get_client().create_post_with_link(
            commentary=commentary,
            url=url,
            title=title,
            description=description,
            visibility=visibility,
        )
        result["message"] = "Post with link created successfully"
        result["url"] = f"https://www.linkedin.com/feed/update/{result['postUrn']}"
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def create_post_with_image(
    commentary: Annotated[str, Field(description="Post text content.")],
    image_path: Annotated[str, Field(description="Absolute path to the image file (PNG, JPG, JPEG, GIF).")],
    alt_text: Annotated[str | None, Field(description="Alt text for the image.")] = None,
    visibility: Annotated[str, Field(description="Post visibility: PUBLIC, CONNECTIONS, LOGGED_IN, or CONTAINER.")] = "PUBLIC",
) -> str:
    """Create a post with an uploaded image.

    Args:
        commentary: Post text content.
        image_path: Absolute path to the image file (PNG, JPG, JPEG, GIF).
        alt_text: Alt text for the image.
        visibility: Post visibility.
    """
    try:
        result = get_client().create_post_with_image(
            commentary=commentary,
            image_path=image_path,
            alt_text=alt_text,
            visibility=visibility,
        )
        result["message"] = "Post with image created successfully"
        result["url"] = f"https://www.linkedin.com/feed/update/{result['postUrn']}"
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def create_post_with_document(
    commentary: Annotated[str, Field(description="Post text content.")],
    document_path: Annotated[str, Field(description="Absolute path to the document file (PDF, DOC, DOCX, PPT, PPTX).")],
    title: Annotated[str | None, Field(description="Document title (defaults to filename).")] = None,
    visibility: Annotated[str, Field(description="Post visibility: PUBLIC, CONNECTIONS, LOGGED_IN, or CONTAINER.")] = "PUBLIC",
) -> str:
    """Create a post with an uploaded document.

    Args:
        commentary: Post text content.
        document_path: Absolute path to the document file (PDF, DOC, DOCX, PPT, PPTX).
        title: Document title (defaults to filename).
        visibility: Post visibility.
    """
    try:
        result = get_client().create_post_with_document(
            commentary=commentary,
            document_path=document_path,
            title=title,
            visibility=visibility,
        )
        result["message"] = "Post with document created successfully"
        result["url"] = f"https://www.linkedin.com/feed/update/{result['postUrn']}"
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def create_post_with_video(
    commentary: Annotated[str, Field(description="Post text content.")],
    video_path: Annotated[str, Field(description="Absolute path to the video file (MP4, MOV, AVI, WMV, WebM, MKV).")],
    title: Annotated[str | None, Field(description="Video title (defaults to filename).")] = None,
    visibility: Annotated[str, Field(description="Post visibility: PUBLIC, CONNECTIONS, LOGGED_IN, or CONTAINER.")] = "PUBLIC",
) -> str:
    """Create a post with an uploaded video.

    Args:
        commentary: Post text content.
        video_path: Absolute path to the video file (MP4, MOV, AVI, WMV, WebM, MKV).
        title: Video title (defaults to filename).
        visibility: Post visibility.
    """
    try:
        result = get_client().create_post_with_video(
            commentary=commentary,
            video_path=video_path,
            title=title,
            visibility=visibility,
        )
        result["message"] = "Post with video created successfully"
        result["url"] = f"https://www.linkedin.com/feed/update/{result['postUrn']}"
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def create_poll(
    question: Annotated[str, Field(description="Poll question text.")],
    options: Annotated[str | list, Field(description="JSON array of 2-4 option strings, e.g. [\"Yes\", \"No\", \"Maybe\"].")],
    commentary: Annotated[str, Field(description="Optional post text to accompany the poll.")] = "",
    duration: Annotated[str, Field(description="Poll duration: ONE_DAY, THREE_DAYS, SEVEN_DAYS, or FOURTEEN_DAYS.")] = "THREE_DAYS",
    visibility: Annotated[str, Field(description="Post visibility: PUBLIC, CONNECTIONS, LOGGED_IN, or CONTAINER.")] = "PUBLIC",
) -> str:
    """Create a LinkedIn poll post.

    Args:
        question: Poll question text.
        options: JSON array of 2-4 option strings, e.g. ["Yes", "No", "Maybe"].
        commentary: Optional post text to accompany the poll.
        duration: Poll duration: ONE_DAY, THREE_DAYS, SEVEN_DAYS, or FOURTEEN_DAYS.
        visibility: Post visibility.
    """
    try:
        parsed_options = _parse_json(options, "options")
        if not isinstance(parsed_options, list):
            return json.dumps({"error": True, "message": "options must be a JSON array of strings"})

        result = get_client().create_poll(
            question=question,
            options=parsed_options,
            commentary=commentary,
            duration=duration,
            visibility=visibility,
        )
        result["message"] = "Poll created successfully"
        result["url"] = f"https://www.linkedin.com/feed/update/{result['postUrn']}"
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def create_post_with_multi_images(
    commentary: Annotated[str, Field(description="Post text content.")],
    image_paths: Annotated[str | list, Field(description="JSON array of absolute paths to image files (2-20 images).")],
    alt_texts: Annotated[str | list | None, Field(description="JSON array of alt texts, matched by index to image_paths.")] = None,
    visibility: Annotated[str, Field(description="Post visibility: PUBLIC, CONNECTIONS, LOGGED_IN, or CONTAINER.")] = "PUBLIC",
) -> str:
    """Create a post with multiple images (2-20).

    Args:
        commentary: Post text content.
        image_paths: JSON array of absolute paths to image files (2-20 images).
        alt_texts: JSON array of alt texts, matched by index to image_paths.
        visibility: Post visibility.
    """
    try:
        parsed_paths = _parse_json(image_paths, "image_paths")
        parsed_alts = _parse_json(alt_texts, "alt_texts")

        result = get_client().create_post_with_multi_images(
            commentary=commentary,
            image_paths=parsed_paths,
            alt_texts=parsed_alts,
            visibility=visibility,
        )
        result["message"] = f"Post with {len(parsed_paths)} images created successfully"
        result["url"] = f"https://www.linkedin.com/feed/update/{result['postUrn']}"
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)
