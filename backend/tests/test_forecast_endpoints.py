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
async def test_forecast_prepare_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "aoi_id": "aoi-sinop",
            "metric": "NDVI",
            "observations": [
                {
                    "aoi_id": "aoi-sinop",
                    "metric": "NDVI",
                    "value": 0.72,
                    "acquisition_datetime": "2020-07-01T00:00:00Z",
                },
                {
                    "aoi_id": "aoi-sinop",
                    "metric": "NDVI",
                    "value": 0.68,
                    "acquisition_datetime": "2021-07-01T00:00:00Z",
                },
            ],
            "temporal_resolution": "ANNUAL",
            "aggregation_method": "MEDIAN",
        }

        resp = await client.post("/api/v1/forecast/prepare", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["aggregated_count"] == 2
        assert "quality_report" in data


@pytest.mark.asyncio
async def test_forecast_run_endpoint(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "aoi_id": "aoi-sinop",
            "metric": "NDVI",
            "observations": [
                {
                    "aoi_id": "aoi-sinop",
                    "metric": "NDVI",
                    "value": 0.72,
                    "acquisition_datetime": "2020-07-01T00:00:00Z",
                },
                {
                    "aoi_id": "aoi-sinop",
                    "metric": "NDVI",
                    "value": 0.68,
                    "acquisition_datetime": "2021-07-01T00:00:00Z",
                },
                {
                    "aoi_id": "aoi-sinop",
                    "metric": "NDVI",
                    "value": 0.64,
                    "acquisition_datetime": "2022-07-01T00:00:00Z",
                },
                {
                    "aoi_id": "aoi-sinop",
                    "metric": "NDVI",
                    "value": 0.60,
                    "acquisition_datetime": "2023-07-01T00:00:00Z",
                },
            ],
            "forecast_start_year": 2024,
            "forecast_end_year": 2028,
            "scenario": "BASELINE_TREND",
        }

        resp = await client.post("/api/v1/forecast/run", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "COMPLETED"
        assert len(data["predictions"]) == 5
        assert data["epistemic_level"] == "PREDICTED"


@pytest.mark.asyncio
async def test_forecast_run_insufficient_data_returns_422():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "aoi_id": "aoi-sinop",
            "metric": "NDVI",
            "observations": [
                {
                    "aoi_id": "aoi-sinop",
                    "metric": "NDVI",
                    "value": 0.72,
                    "acquisition_datetime": "2020-07-01T00:00:00Z",
                },
                {
                    "aoi_id": "aoi-sinop",
                    "metric": "NDVI",
                    "value": 0.68,
                    "acquisition_datetime": "2021-07-01T00:00:00Z",
                },
            ],
            "forecast_start_year": 2024,
            "forecast_end_year": 2028,
        }

        resp = await client.post("/api/v1/forecast/run", json=payload)
        assert resp.status_code == 422
        data = resp.json()
        error_obj = data.get("error", {})
        details = error_obj.get("details", {})
        assert details.get("status") == "INSUFFICIENT_DATA"
        assert details.get("required_observations") == 4
        assert details.get("available_observations") == 2


@pytest.mark.asyncio
async def test_forecast_series_query(mock_db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/forecast/series?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "items" in data
