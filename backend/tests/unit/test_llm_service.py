"""Unit tests for LLMService."""

import json
import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.llm import LLMService, LLMTimeoutError, LLMUnavailableError


@pytest.fixture
def llm():
    with patch("app.services.llm.settings") as mock_settings:
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_settings.ollama_model = "llama3.3"
        return LLMService()


def test_rejects_non_localhost_url():
    with patch("app.services.llm.settings") as mock_settings:
        mock_settings.ollama_base_url = "http://external.host:11434"
        mock_settings.ollama_model = "llama3.3"
        with pytest.raises(ValueError, match="localhost"):
            LLMService()


def test_accepts_ollama_service_url():
    with patch("app.services.llm.settings") as mock_settings:
        mock_settings.ollama_base_url = "http://ollama:11434"
        mock_settings.ollama_model = "llama3.3"
        service = LLMService()
        assert service._base_url == "http://ollama:11434"


@pytest.mark.asyncio
async def test_generate_returns_content(llm: LLMService):
    mock_response_data = {"message": {"content": json.dumps({"summary": "test"})}}
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = mock_response_data

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        result = await llm.generate("sys", "user")

    assert "summary" in result
    # Confirm outbound call targeted localhost
    call_args = mock_client.post.call_args
    assert "localhost:11434" in call_args[0][0]


@pytest.mark.asyncio
async def test_generate_raises_timeout(llm: LLMService):
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        mock_client_cls.return_value = mock_client

        with pytest.raises(LLMTimeoutError):
            await llm.generate("sys", "user")


@pytest.mark.asyncio
async def test_generate_raises_unavailable_on_connect_error(llm: LLMService):
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("refused"))
        mock_client_cls.return_value = mock_client

        with pytest.raises(LLMUnavailableError):
            await llm.generate("sys", "user")
