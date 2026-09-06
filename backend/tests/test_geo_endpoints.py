from unittest.mock import AsyncMock, MagicMock
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import get_db


@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock()
    # Mock execute result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = b""
    mock_result.fetchall.return_value = []
    mock_result.fetchone.return_value = None
    mock_session.execute.return_value = mock_result

    async def _override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = _override_get_db
    yield mock_session
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_get_road_vector_tile_invalid_coordinates(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Invalid zoom level
        resp = await client.get("/api/v1/geo/tiles/roads/25/0/0.pbf")
        assert resp.status_code == 400
        data = resp.json()
        assert "out of bounds" in data["error"]["message"]

        # Invalid X index for Z=1
        resp = await client.get("/api/v1/geo/tiles/roads/1/10/0.pbf")
        assert resp.status_code == 400
        data = resp.json()
        assert "out of bounds" in data["error"]["message"]


@pytest.mark.asyncio
async def test_get_road_vector_tile_valid_empty(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/geo/tiles/roads/0/0/0.pbf")
        assert resp.status_code == 204


@pytest.mark.asyncio
async def test_get_aoi_road_stats_not_found(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Non-existent UUID
        resp = await client.get("/api/v1/geo/roads/stats/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
        data = resp.json()
        assert "not found" in data["error"]["message"].lower()


@pytest.mark.asyncio
async def test_ingest_empty_roads_batch(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/v1/geo/roads/ingest", json=[])
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_processed"] == 0
        assert data["attribution"] == "© OpenStreetMap contributors (ODbL 1.0)"
