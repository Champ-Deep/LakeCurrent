from __future__ import annotations

from app.clients.base import BaseSearchClient, SearchResponse
from app.parsing.lakeglimpse_parser import parse


class LakeGlimpseClient(BaseSearchClient):
    async def search(self, query: str, **kwargs) -> SearchResponse:
        params = {"q": query}
        response = await self._client.get(f"{self.base_url}/search", params=params)
        response.raise_for_status()
        return parse(response.text, query=query)
