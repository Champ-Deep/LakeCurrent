from __future__ import annotations

from app.clients.base import BaseSearchClient, SearchResponse
from app.parsing.lakefilter_parser import parse


class LakeFilterClient(BaseSearchClient):
    async def search(self, query: str, **kwargs) -> SearchResponse:
        params = {"q": query, "format": "json"}
        for key in ("categories", "language", "pageno", "time_range", "safesearch"):
            if key in kwargs and kwargs[key] is not None:
                params[key] = kwargs[key]

        response = await self._client.get(f"{self.base_url}/search", params=params)
        response.raise_for_status()
        return parse(response.json())
