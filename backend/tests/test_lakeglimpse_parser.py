from app.parsing.lakeglimpse_parser import parse


def test_parses_results(lakeglimpse_html):
    results = parse(lakeglimpse_html)
    assert len(results.results) == 3


def test_extracts_urls(lakeglimpse_html):
    results = parse(lakeglimpse_html)
    assert results.results[0].url == "https://flask.palletsprojects.com/"
    assert results.results[1].url == "https://www.djangoproject.com/"
    assert results.results[2].url == "https://fastapi.tiangolo.com/"


def test_extracts_titles(lakeglimpse_html):
    results = parse(lakeglimpse_html)
    assert results.results[0].title == "Flask – A Python Microframework"
    assert results.results[1].title == "Django – The Web framework for perfectionists with deadlines"


def test_extracts_snippets(lakeglimpse_html):
    results = parse(lakeglimpse_html)
    assert "lightweight WSGI" in results.results[0].snippet
    assert "Django makes it easier" in results.results[1].snippet


def test_engine_is_lakeglimpse(lakeglimpse_html):
    results = parse(lakeglimpse_html)
    for r in results.results:
        assert r.engine == "lakeglimpse"


def test_empty_html_returns_empty():
    results = parse("")
    assert results.results == []


def test_html_without_results():
    results = parse("<html><body><div>No results</div></body></html>")
    assert results.results == []


def test_unicode_in_results():
    html = """
    <div><div>
      <a href="https://example.com/">
        <h3>Emoji \U0001f600 and CJK \u4e16\u754c</h3>
      </a>
    </div></div>
    """
    results = parse(html)
    assert len(results.results) == 1
    assert "\U0001f600" in results.results[0].title


def test_missing_snippet_div():
    html = """
    <div>
      <a href="https://example.com/"><h3>Title Only</h3></a>
    </div>
    """
    results = parse(html)
    assert len(results.results) == 1
    assert results.results[0].snippet == ""


def test_link_without_href():
    html = """
    <div>
      <a><h3>No href attribute</h3></a>
      <a href="https://good.com/"><h3>Has href</h3></a>
    </div>
    """
    results = parse(html)
    assert len(results.results) == 1
    assert results.results[0].url == "https://good.com/"


def test_max_depth_traversal():
    """Deeply nested HTML should not hang — depth is capped."""
    # Build 20 levels of nesting (exceeds _MAX_DEPTH of 10)
    inner = '<a href="https://example.com/"><h3>Deep</h3></a>'
    for _ in range(20):
        inner = f"<div>{inner}</div>"
    html = f"<html><body>{inner}<div>Snippet text that is long enough</div></body></html>"
    results = parse(html)
    assert len(results.results) == 1


def test_relative_url_skipped():
    html = """
    <div><div>
      <a href="/relative/path"><h3>Relative URL</h3></a>
    </div></div>
    <div><div>
      <a href="https://good.com/"><h3>Absolute URL</h3></a>
    </div></div>
    """
    results = parse(html)
    assert len(results.results) == 1
    assert results.results[0].url == "https://good.com/"
