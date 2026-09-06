from unittest.mock import AsyncMock, patch
import httpx
import pytest
from app.services.eo.stac.models import STACSearchRequest
from app.services.eo.stac.providers import EarthSearchAWSProvider
from app.services.eo.stac.exceptions import STACAuthenticationError


def test_build_stac_search_payload():
    provider = EarthSearchAWSProvider()
    req = STACSearchRequest(
        collections=["sentinel-2-l2a"],
        bbox=[-55.4, -12.1, -54.1, -10.9],
        cloud_cover_max=20.0,
        limit=10,
    )
    payload = provider._build_stac_search_payload(req)
    assert payload["collections"] == ["sentinel-2-l2a"]
    assert payload["bbox"] == [-55.4, -12.1, -54.1, -10.9]
    assert payload["query"]["eo:cloud_cover"]["lte"] == 20.0
    assert payload["limit"] == 10


@pytest.mark.asyncio
async def test_provider_transient_retry_success():
    provider = EarthSearchAWSProvider()
    provider._max_retries = 2

    # Mock responses: 1st fails with 500, 2nd succeeds with 200
    mock_500 = httpx.Response(status_code=500, request=httpx.Request("POST", "http://test"))
    mock_200 = httpx.Response(
        status_code=200,
        request=httpx.Request("POST", "http://test"),
        json={"type": "FeatureCollection", "features": [], "numberMatched": 0},
    )

    with patch("httpx.AsyncClient.post", side_effect=[mock_500, mock_200]):
        req = STACSearchRequest(bbox=[-55.4, -12.1, -54.1, -10.9])
        resp = await provider.search(req)
        assert resp.total_matched == 0
        assert resp.returned_count == 0


@pytest.mark.asyncio
async def test_provider_non_retriable_auth_error():
    provider = EarthSearchAWSProvider()
    provider._max_retries = 2

    mock_401 = httpx.Response(status_code=401, request=httpx.Request("POST", "http://test"))

    with patch("httpx.AsyncClient.post", side_effect=[mock_401]):
        req = STACSearchRequest(bbox=[-55.4, -12.1, -54.1, -10.9])
        resp = await provider.search(req)
        # Should gracefully return empty result with logged error rather than crashing
        assert resp.returned_count == 0
