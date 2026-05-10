"""Ollama HTTP client — all calls target localhost:11434 only."""

import json

import httpx

from app.config import settings


class LLMUnavailableError(Exception):
    pass


class LLMTimeoutError(Exception):
    pass


class LLMService:
    _TIMEOUT = 60.0

    def __init__(self) -> None:
        # Enforce localhost-only target (FR-009)
        base = settings.ollama_base_url
        if not (base.startswith("http://localhost") or base.startswith("http://ollama")):
            raise ValueError("OLLAMA_BASE_URL must point to localhost or the ollama service")
        self._base_url = base
        self._model = settings.ollama_model

    async def generate(self, system_prompt: str, user_message: str) -> str:
        url = f"{self._base_url}/api/chat"
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
        }
        try:
            async with httpx.AsyncClient(timeout=self._TIMEOUT) as client:
                response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return str(data["message"]["content"])
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError("LLM request timed out after 60 seconds") from exc
        except (httpx.ConnectError, httpx.HTTPStatusError) as exc:
            raise LLMUnavailableError(f"LLM service unreachable: {exc}") from exc
