import httpx
import pytest
import respx

from app.clients.lakeglimpse import LakeGlimpseClient


@pytest.fixture
def client():
    return LakeGlimpseClient(base_url="http://lakeglimpse:5000", timeout=5.0)


@respx.mock
async def test_builds_correct_url(client, lakeglimpse_html):
    route = respx.get("http://lakeglimpse:5000/search").mock(
        return_value=httpx.Response(200, text=lakeglimpse_html)
    )
    await client.search("python web framework")

    assert route.called
    request = route.calls[0].request
    assert "q=python+web+framework" in str(request.url)


@respx.mock
async def test_returns_search_response(client, lakeglimpse_html):
    respx.get("http://lakeglimpse:5000/search").mock(
        return_value=httpx.Response(200, text=lakeglimpse_html)
    )
    response = await client.search("python web framework")
    assert len(response.results) == 3
    assert response.results[0].url == "https://flask.palletsprojects.com/"


@respx.mock
async def test_raises_on_http_error(client):
    respx.get("http://lakeglimpse:5000/search").mock(
        return_value=httpx.Response(503, text="Service Unavailable")
    )
    with pytest.raises(httpx.HTTPStatusError):
        await client.search("test")


@respx.mock
async def test_raises_on_timeout(client):
    respx.get("http://lakeglimpse:5000/search").mock(side_effect=httpx.ReadTimeout("timeout"))
    with pytest.raises(httpx.ReadTimeout):
        await client.search("test")


@respx.mock
async def test_empty_html_response(client):
    respx.get("http://lakeglimpse:5000/search").mock(
        return_value=httpx.Response(200, text="")
    )
    response = await client.search("test")
    assert response.results == []
    assert response.query == "test"


@respx.mock
async def test_connect_error(client):
    respx.get("http://lakeglimpse:5000/search").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )
    with pytest.raises(httpx.ConnectError):
        await client.search("test")
