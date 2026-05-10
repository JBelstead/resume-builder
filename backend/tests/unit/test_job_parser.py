"""Unit tests for JobParser."""

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.job_parser import JobParser, JobURLError


@pytest.fixture
def parser():
    return JobParser()


@pytest.mark.asyncio
async def test_fetch_extracts_text(parser: JobParser):
    html = "<html><body><h1>Engineer</h1><p>Build things.</p><script>alert('x')</script></body></html>"
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.text = html

    with patch("httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client

        result = await parser.fetch("https://example.com/jobs/1")

    assert "Engineer" in result
    assert "Build things" in result
    assert "alert" not in result


@pytest.mark.asyncio
async def test_fetch_only_contacts_supplied_url(parser: JobParser):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.text = "<html><body>Job</body></html>"

    with patch("httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client

        await parser.fetch("https://example.com/job/42")

        assert mock_client.get.call_count == 1
        called_url = mock_client.get.call_args[0][0]
        assert called_url == "https://example.com/job/42"


@pytest.mark.asyncio
async def test_fetch_raises_on_timeout(parser: JobParser):
    with patch("httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        mock_cls.return_value = mock_client

        with pytest.raises(JobURLError, match="Timed out"):
            await parser.fetch("https://example.com/job/1")


@pytest.mark.asyncio
async def test_fetch_raises_on_connect_error(parser: JobParser):
    with patch("httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
        mock_cls.return_value = mock_client

        with pytest.raises(JobURLError, match="Failed"):
            await parser.fetch("https://example.com/job/1")


def test_extract_text_strips_noise(parser: JobParser):
    html = """
    <html><body>
    <nav>Skip nav</nav>
    <header>Skip header</header>
    <main><h1>Title</h1><p>Content here</p></main>
    <footer>Skip footer</footer>
    <script>skip script</script>
    <style>skip style</style>
    </body></html>
    """
    text = parser._extract_text(html)
    assert "Title" in text
    assert "Content here" in text
    assert "Skip nav" not in text
    assert "skip script" not in text
