import httpx
import pytest
from unittest.mock import Mock

from tools.godot_docs import (
    GodotDocsClient,
    GodotDocsError,
)


def test_get_page_converts_http_error_to_godot_docs_error():
    client = GodotDocsClient()

    request = httpx.Request(
        "GET",
        "https://docs.godotengine.org/fake",
    )

    response = httpx.Response(
        status_code=404,
        request=request,
    )

    client.client.get = Mock(
        return_value=response
    )

    with pytest.raises(GodotDocsError):
        client.get_page("fake")


def test_get_page_converts_network_error_to_godot_docs_error():
    client = GodotDocsClient()

    request = httpx.Request(
        "GET",
        "https://docs.godotengine.org/fake",
    )

    client.client.get = Mock(
        side_effect=httpx.ConnectError(
            "Connection failed",
            request=request,
        )
    )

    with pytest.raises(GodotDocsError):
        client.get_page("fake")


def test_get_page_text_raises_when_content_missing():
    client = GodotDocsClient()

    client.get_page = Mock(
        return_value="""
        <html>
            <body>
                <div>No Godot documentation here.</div>
            </body>
        </html>
        """
    )

    with pytest.raises(GodotDocsError):
        client.get_page_text("fake")