from __future__ import annotations

from dataclasses import dataclass, field

import httpx


@dataclass
class SearchResult:
    url: str
    title: str
    snippet: str
    engine: str | None = None
    score: float | None = None
    published_date: str | None = None


@dataclass
class SearchResponse:
    query: str
    results: list[SearchResult] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    answers: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


class BaseSearchClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self._client.aclose()

    async def is_healthy(self) -> str:
        try:
            r = await self._client.get(f"{self.base_url}/")
            return "ok" if r.status_code < 500 else "degraded"
        except Exception:
            return "down"

    async def search(self, query: str, **kwargs) -> SearchResponse:
        raise NotImplementedError
