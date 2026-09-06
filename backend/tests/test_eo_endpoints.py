from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import get_db
from app.models.enums import SensingModality


@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_result.fetchall.return_value = []
    mock_result.fetchone.return_value = None
    mock_session.execute.return_value = mock_result

    async def _override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = _override_get_db
    yield mock_session
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_get_providers_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/eo/providers")
        assert resp.status_code == 200
        providers = resp.json()
        assert len(providers) >= 2
        keys = [p["key"] for p in providers]
        assert "earth-search" in keys


@pytest.mark.asyncio
async def test_get_collections_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/eo/collections")
        assert resp.status_code == 200
        collections = resp.json()
        ids = [c["id"] for c in collections]
        assert "sentinel-2-l2a" in ids
        assert "sentinel-1-grd" in ids


@pytest.mark.asyncio
async def test_post_search_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "collections": ["sentinel-2-l2a"],
            "bbox": [-55.4, -12.1, -54.1, -10.9],
            "limit": 5,
        }
        with patch("app.services.eo.stac.providers.BaseSTACProvider.search") as mock_search:
            from app.services.eo.stac.models import STACSearchResponse, STACSearchRequest
            mock_search.return_value = STACSearchResponse(
                query=STACSearchRequest(**payload),
                total_matched=0,
                returned_count=0,
                scenes=[],
                providers_contacted=["Element84 Earth Search"],
                attribution_summary=["© European Union, Copernicus Sentinel-2 data"],
            )
            resp = await client.post("/api/v1/eo/search", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            assert data["total_matched"] == 0
            assert "attribution_summary" in data


@pytest.mark.asyncio
async def test_post_modality_assessment_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Send empty scene list
        resp = await client.post("/api/v1/eo/modality-assessment", json=[])
        assert resp.status_code == 200
        assessment = resp.json()
        assert assessment["epistemic_level"] == "CALCULATED"
        assert assessment["recommended_modality"] == "OPTICAL"
