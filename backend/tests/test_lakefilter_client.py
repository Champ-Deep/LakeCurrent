import httpx
import pytest
import respx

from app.clients.lakefilter import LakeFilterClient


@pytest.fixture
def client():
    return LakeFilterClient(base_url="http://lakefilter:8080", timeout=5.0)


@respx.mock
async def test_builds_correct_url(client, lakefilter_json):
    route = respx.get("http://lakefilter:8080/search").mock(
        return_value=httpx.Response(200, json=lakefilter_json)
    )
    await client.search("python web framework")

    assert route.called
    request = route.calls[0].request
    assert "q=python+web+framework" in str(request.url)
    assert "format=json" in str(request.url)


@respx.mock
async def test_returns_search_response(client, lakefilter_json):
    respx.get("http://lakefilter:8080/search").mock(
        return_value=httpx.Response(200, json=lakefilter_json)
    )
    response = await client.search("python web framework")
    assert response.query == "python web framework"
    assert len(response.results) == 3


@respx.mock
async def test_passes_optional_params(client, lakefilter_json):
    route = respx.get("http://lakefilter:8080/search").mock(
        return_value=httpx.Response(200, json=lakefilter_json)
    )
    await client.search("test", categories="news", language="en", pageno=2)

    request = route.calls[0].request
    url = str(request.url)
    assert "categories=news" in url
    assert "language=en" in url
    assert "pageno=2" in url


@respx.mock
async def test_raises_on_http_error(client):
    respx.get("http://lakefilter:8080/search").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )
    with pytest.raises(httpx.HTTPStatusError):
        await client.search("test")


@respx.mock
async def test_raises_on_timeout(client):
    respx.get("http://lakefilter:8080/search").mock(side_effect=httpx.ReadTimeout("timeout"))
    with pytest.raises(httpx.ReadTimeout):
        await client.search("test")


@respx.mock
async def test_malformed_json_raises(client):
    respx.get("http://lakefilter:8080/search").mock(
        return_value=httpx.Response(200, text="not valid json {{{")
    )
    with pytest.raises(Exception):
        await client.search("test")


@respx.mock
async def test_connect_error(client):
    respx.get("http://lakefilter:8080/search").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )
    with pytest.raises(httpx.ConnectError):
        await client.search("test")
