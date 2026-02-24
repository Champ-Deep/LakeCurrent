from __future__ import annotations

from bs4 import BeautifulSoup

from app.clients.base import SearchResponse, SearchResult


_MAX_DEPTH = 10          # Max parent-div levels to walk when finding snippets
_MIN_SNIPPET_LEN = 10    # Ignore sibling text shorter than this (navigation, labels)


def parse(html: str, query: str = "") -> SearchResponse:
    """Parse LakeGlimpse HTML response into a SearchResponse.

    Uses structural patterns (a > h3) rather than CSS class names,
    since Google changes class names frequently.
    """
    if not html:
        return SearchResponse(query=query)

    soup = BeautifulSoup(html, "html.parser")
    results: list[SearchResult] = []

    # Find all <a> tags that contain an <h3> child — these are result links
    for link in soup.find_all("a"):
        h3 = link.find("h3")
        if not h3:
            continue

        url = link.get("href", "")
        title = h3.get_text(strip=True)
        if not url or not title:
            continue
        if not url.startswith(("http://", "https://")):
            continue

        # Walk up past the <a>'s wrapper divs to the result-level container.
        # Structure: div.result > div(link-wrapper) > a > div > h3
        #                       > div(snippet-wrapper) > div > span
        snippet = ""
        # Go up from <a> through its wrapper divs until we find a container
        # that has sibling divs (the result-level block).
        depth = 0
        node = link.parent
        while node and depth < _MAX_DEPTH:
            depth += 1
            parent = node.parent
            if parent is None:
                break
            sibling_divs = [
                s for s in parent.find_all("div", recursive=False) if s is not node
            ]
            for sibling in sibling_divs:
                text = sibling.get_text(strip=True)
                if text and len(text) > _MIN_SNIPPET_LEN:
                    snippet = text
                    break
            if snippet:
                break
            node = parent

        results.append(
            SearchResult(
                url=url,
                title=title,
                snippet=snippet,
                engine="lakeglimpse",
            )
        )

    return SearchResponse(query=query, results=results)
