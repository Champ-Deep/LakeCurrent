from app.parsing.lakefilter_parser import parse


def test_parses_results(lakefilter_json):
    response = parse(lakefilter_json)
    assert len(response.results) == 3


def test_maps_fields_correctly(lakefilter_json):
    response = parse(lakefilter_json)
    first = response.results[0]
    assert first.url == "https://flask.palletsprojects.com/"
    assert first.title == "Flask – A Python Microframework"
    assert first.snippet == (
        "Flask is a lightweight WSGI web application framework. "
        "It is designed to make getting started quick and easy."
    )
    assert first.engine == "google"
    assert first.score == 0.92
    assert first.published_date == "2024-06-15"


def test_handles_null_published_date(lakefilter_json):
    response = parse(lakefilter_json)
    second = response.results[1]
    assert second.published_date is None


def test_handles_missing_published_date(lakefilter_json):
    response = parse(lakefilter_json)
    third = response.results[2]
    assert third.published_date is None


def test_extracts_query(lakefilter_json):
    response = parse(lakefilter_json)
    assert response.query == "python web framework"


def test_extracts_suggestions(lakefilter_json):
    response = parse(lakefilter_json)
    assert response.suggestions == [
        "best python web framework 2024",
        "python async web framework",
    ]


def test_extracts_answers(lakefilter_json):
    response = parse(lakefilter_json)
    assert response.answers == [
        "Popular Python web frameworks include Django, Flask, and FastAPI."
    ]


def test_empty_response_returns_empty_lists():
    response = parse({})
    assert response.results == []
    assert response.suggestions == []
    assert response.answers == []
    assert response.query == ""


def test_malformed_result_skipped():
    data = {
        "query": "test",
        "results": [
            {"url": "https://example.com"},  # missing title and content
            {"url": "https://good.com", "title": "Good", "content": "A good result"},
        ],
    }
    response = parse(data)
    assert len(response.results) == 1
    assert response.results[0].url == "https://good.com"


def test_unicode_in_results():
    data = {
        "query": "test",
        "results": [
            {
                "url": "https://example.com/",
                "title": "Results with emoji \U0001f600 and CJK \u4e16\u754c",
                "content": "Arabic \u0645\u0631\u062d\u0628\u0627 and accents caf\u00e9",
                "engine": "google",
            }
        ],
    }
    response = parse(data)
    assert len(response.results) == 1
    assert "\U0001f600" in response.results[0].title
    assert "caf\u00e9" in response.results[0].snippet


def test_score_as_string():
    data = {
        "query": "test",
        "results": [
            {
                "url": "https://example.com/",
                "title": "Test",
                "content": "Some content here",
                "score": "0.85",
            }
        ],
    }
    response = parse(data)
    assert response.results[0].score == 0.85


def test_score_invalid_string():
    data = {
        "query": "test",
        "results": [
            {
                "url": "https://example.com/",
                "title": "Test",
                "content": "Some content here",
                "score": "not-a-number",
            }
        ],
    }
    response = parse(data)
    assert response.results[0].score is None


def test_invalid_url_skipped():
    data = {
        "query": "test",
        "results": [
            {"url": "javascript:alert(1)", "title": "XSS", "content": "Bad result"},
            {"url": "/relative/path", "title": "Relative", "content": "No protocol"},
            {"url": "ftp://files.example.com", "title": "FTP", "content": "Wrong proto"},
            {"url": "https://good.com/", "title": "Good", "content": "Valid result"},
        ],
    }
    response = parse(data)
    assert len(response.results) == 1
    assert response.results[0].url == "https://good.com/"


def test_html_entities_in_content():
    data = {
        "query": "test",
        "results": [
            {
                "url": "https://example.com/",
                "title": "Tom &amp; Jerry",
                "content": 'She said &quot;hello&quot; &amp; waved',
            }
        ],
    }
    response = parse(data)
    # Parser stores raw text as-is (LakeFilter already decodes entities in JSON)
    assert len(response.results) == 1
