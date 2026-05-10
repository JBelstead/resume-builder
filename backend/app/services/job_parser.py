"""Fetches a job posting URL and extracts visible text.

Only the user-supplied URL is contacted — no additional external hosts (FR-009).
"""

import httpx
from bs4 import BeautifulSoup


class JobURLError(Exception):
    pass


class JobParser:
    _TIMEOUT = 15.0
    _REMOVE_TAGS = {"script", "style", "nav", "header", "footer", "aside"}

    async def fetch(self, url: str) -> str:
        """Fetch URL and return extracted plain text."""
        try:
            async with httpx.AsyncClient(
                timeout=self._TIMEOUT,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (resume-builder job parser)"},
            ) as client:
                response = await client.get(url)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise JobURLError(f"Timed out fetching URL: {url}") from exc
        except (httpx.ConnectError, httpx.HTTPStatusError) as exc:
            raise JobURLError(f"Failed to fetch URL: {exc}") from exc

        return self._extract_text(response.text)

    def _extract_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(list(self._REMOVE_TAGS)):
            tag.decompose()
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
