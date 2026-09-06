from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import get_db


@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    async def _override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = _override_get_db
    yield mock_session
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_intelligence_analyze_endpoint(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "aoi_geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-54.7, -11.5],
                        [-54.6, -11.5],
                        [-54.6, -11.4],
                        [-54.7, -11.4],
                        [-54.7, -11.5],
                    ]
                ],
            },
            "target_start_date": "2023-07-15T00:00:00Z",
            "target_end_date": "2026-07-18T00:00:00Z",
            "ndvi_delta": -0.22,
            "ndbi_delta": 0.15,
            "affected_area_km2": 6.85,
            "primary_sensor": "Sentinel-2",
        }

        resp = await client.post("/api/v1/intelligence/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["intelligence_type"] == "URBAN_EXPANSION"
        assert data["evidence_strength"] == "STRONG"
        assert data["epistemic_level"] == "CALCULATED"
        assert "evidence_graph" in data
        assert len(data["evidence_graph"]["nodes"]) >= 3


@pytest.mark.asyncio
async def test_intelligence_events_query_endpoint(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/intelligence/events?limit=10&offset=0")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "items" in data


@pytest.mark.asyncio
async def test_evidence_query_endpoint(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "source_type": "SATELLITE_TELEMETRY",
            "limit": 10,
            "offset": 0,
        }
        resp = await client.post("/api/v1/intelligence/evidence/query", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "items" in data

