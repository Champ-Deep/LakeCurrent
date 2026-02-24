import httpx
import respx
from httpx import ASGITransport, AsyncClient

import pytest

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@respx.mock
async def test_default_mode_routes_to_lakefilter(client, lakefilter_json):
    route = respx.get("http://lakefilter:8080/search").mock(
        return_value=httpx.Response(200, json=lakefilter_json)
    )
    response = await client.get("/search", params={"q": "test"})
    assert response.status_code == 200
    assert route.called
    data = response.json()
    assert len(data["results"]) > 0


@respx.mock
async def test_glimpse_mode_routes_to_lakeglimpse(client, lakeglimpse_html):
    route = respx.get("http://lakeglimpse:5000/search").mock(
        return_value=httpx.Response(200, text=lakeglimpse_html)
    )
    response = await client.get("/search", params={"q": "test", "mode": "glimpse"})
    assert response.status_code == 200
    assert route.called
    data = response.json()
    assert len(data["results"]) > 0


@respx.mock
async def test_lakefilter_failure_returns_502(client):
    respx.get("http://lakefilter:8080/search").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )
    response = await client.get("/search", params={"q": "test"})
    assert response.status_code == 502
    assert "detail" in response.json()


@respx.mock
async def test_lakeglimpse_failure_returns_503(client):
    respx.get("http://lakeglimpse:5000/search").mock(
        return_value=httpx.Response(503, text="Service Unavailable")
    )
    response = await client.get("/search", params={"q": "test", "mode": "glimpse"})
    assert response.status_code == 503
    assert "detail" in response.json()


@respx.mock
async def test_missing_query_returns_422(client):
    response = await client.get("/search")
    assert response.status_code == 422


@respx.mock
async def test_limit_param_caps_results(client, lakefilter_json):
    respx.get("http://lakefilter:8080/search").mock(
        return_value=httpx.Response(200, json=lakefilter_json)
    )
    response = await client.get("/search", params={"q": "test", "limit": 1})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1


# --- Health endpoint tests ---


@respx.mock
async def test_health_endpoint_healthy(client):
    respx.get("http://lakefilter:8080/").mock(return_value=httpx.Response(200))
    respx.get("http://lakeglimpse:5000/").mock(return_value=httpx.Response(200))
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["components"]["LakeFilter"] == "ok"
    assert data["components"]["LakeGlimpse"] == "ok"


@respx.mock
async def test_health_endpoint_degraded(client):
    respx.get("http://lakefilter:8080/").mock(return_value=httpx.Response(200))
    respx.get("http://lakeglimpse:5000/").mock(side_effect=httpx.ConnectError("down"))
    response = await client.get("/health")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "degraded"
    assert data["components"]["LakeFilter"] == "ok"
    assert data["components"]["LakeGlimpse"] == "down"


# --- Error handling tests ---


@respx.mock
async def test_lakefilter_returns_invalid_json(client):
    respx.get("http://lakefilter:8080/search").mock(
        return_value=httpx.Response(200, text="not valid json {{{")
    )
    response = await client.get("/search", params={"q": "test"})
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal search error"


@respx.mock
async def test_lakeglimpse_timeout_returns_503(client):
    respx.get("http://lakeglimpse:5000/search").mock(
        side_effect=httpx.ReadTimeout("timeout")
    )
    response = await client.get("/search", params={"q": "test", "mode": "glimpse"})
    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


@respx.mock
async def test_error_does_not_leak_internals(client):
    respx.get("http://lakefilter:8080/search").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )
    response = await client.get("/search", params={"q": "test"})
    detail = response.json()["detail"]
    assert "http://lakefilter:8080" not in detail
    assert "Internal Server Error" not in detail


# --- Input validation tests ---


@respx.mock
async def test_query_too_long_returns_422(client):
    response = await client.get("/search", params={"q": "a" * 501})
    assert response.status_code == 422


@respx.mock
async def test_pageno_too_high_returns_422(client):
    response = await client.get("/search", params={"q": "test", "pageno": 101})
    assert response.status_code == 422


@respx.mock
async def test_pageno_zero_returns_422(client):
    response = await client.get("/search", params={"q": "test", "pageno": 0})
    assert response.status_code == 422


# --- Parameter forwarding test ---


@respx.mock
async def test_categories_param_forwarded(client, lakefilter_json):
    route = respx.get("http://lakefilter:8080/search").mock(
        return_value=httpx.Response(200, json=lakefilter_json)
    )
    response = await client.get(
        "/search", params={"q": "test", "categories": "news"}
    )
    assert response.status_code == 200
    assert route.called
    request_url = str(route.calls[0].request.url)
    assert "categories=news" in request_url
