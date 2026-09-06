from unittest.mock import AsyncMock, MagicMock
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import get_db


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
async def test_search_coordinate_query(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/geo/search?q=31.5204,%2074.3587")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_results"] >= 1
        first = data["results"][0]
        assert first["entity_type"] == "COORDINATE"
        assert first["coordinates"]["lat"] == 31.5204
        assert first["coordinates"]["lng"] == 74.3587
        assert first["relevance_score"] == 1.0


@pytest.mark.asyncio
async def test_search_text_query_structure(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/geo/search?q=Lahore")
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "Lahore"
        assert data["normalized_query"] == "lahore"
        assert "attribution_notice" in data


@pytest.mark.asyncio
async def test_get_entity_not_found(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/geo/entities/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
        data = resp.json()
        assert "not found" in data["error"]["message"].lower()


@pytest.mark.asyncio
async def test_reverse_geocode_endpoint(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/geo/reverse?lat=31.5204&lon=74.3587&radius_km=15")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
