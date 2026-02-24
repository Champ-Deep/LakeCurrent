from __future__ import annotations

from app.clients.base import SearchResponse, SearchResult


def _safe_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse(data: dict) -> SearchResponse:
    """Parse a LakeFilter JSON response into a SearchResponse."""
    results: list[SearchResult] = []
    for item in data.get("results", []):
        url = item.get("url", "")
        title = item.get("title", "")
        content = item.get("content", "")
        if not (url and title and content):
            continue
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            continue
        results.append(
            SearchResult(
                url=url,
                title=str(title),
                snippet=str(content),
                engine=item.get("engine"),
                score=_safe_float(item.get("score")),
                published_date=item.get("publishedDate"),
            )
        )

    return SearchResponse(
        query=data.get("query", ""),
        results=results,
        suggestions=data.get("suggestions", []),
        answers=data.get("answers", []),
    )
