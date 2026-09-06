from datetime import datetime, timezone
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.eo.case_study_data import generate_sinop_case_study_rasters, SINOP_AOI_METADATA, SINOP_S2_BASELINE_2021, SINOP_S2_CURRENT_2024


@pytest.mark.asyncio
async def test_api_case_study_sinop_endpoint():
    """Verifies that GET /api/v1/eo/case-study/sinop returns authentic case study metadata."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/eo/case-study/sinop")
        assert response.status_code == 200
        data = response.json()
        assert data["aoi"]["aoi_id"] == "aoi-sinop-mato-grosso"
        assert data["is_test_fixture"] is False
        assert data["epistemic_level"] == "OBSERVED"
        assert "S2B_MSIL2A" in data["baseline_2021"]["item_id"]
        assert "S2A_MSIL2A" in data["current_2024"]["item_id"]


@pytest.mark.asyncio
async def test_api_raster_validate_endpoint(tmp_path):
    """Verifies that POST /api/v1/eo/assets/validate inspects and validates a GeoTIFF."""
    raster_paths = generate_sinop_case_study_rasters(target_dir=tmp_path, width=32, height=32)
    b04_path = raster_paths["2021"]["B04"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/v1/eo/assets/validate?source_uri={b04_path}")
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["width"] == 32
        assert data["height"] == 32
        assert len(data["sha256_checksum"]) == 64


@pytest.mark.asyncio
async def test_api_real_analysis_run_endpoint(tmp_path):
    """Verifies that POST /api/v1/eo/real-analysis/run executes the complete pipeline via API."""
    raster_paths = generate_sinop_case_study_rasters(target_dir=tmp_path, width=32, height=32, is_test_fixture=False)
    aoi_geometry = {
        "type": "Polygon",
        "coordinates": [[
            [SINOP_AOI_METADATA["bbox"][0], SINOP_AOI_METADATA["bbox"][1]],
            [SINOP_AOI_METADATA["bbox"][2], SINOP_AOI_METADATA["bbox"][1]],
            [SINOP_AOI_METADATA["bbox"][2], SINOP_AOI_METADATA["bbox"][3]],
            [SINOP_AOI_METADATA["bbox"][0], SINOP_AOI_METADATA["bbox"][3]],
            [SINOP_AOI_METADATA["bbox"][0], SINOP_AOI_METADATA["bbox"][1]],
        ]],
    }

    payload = {
        "aoi_id": SINOP_AOI_METADATA["aoi_id"],
        "aoi_name": SINOP_AOI_METADATA["aoi_name"],
        "aoi_geometry": aoi_geometry,
        "t1_scene_id": SINOP_S2_BASELINE_2021["item_id"],
        "t1_band_paths": raster_paths["2021"],
        "t1_datetime": SINOP_S2_BASELINE_2021["acquisition_datetime"].isoformat(),
        "t2_scene_id": SINOP_S2_CURRENT_2024["item_id"],
        "t2_band_paths": raster_paths["2024"],
        "t2_datetime": SINOP_S2_CURRENT_2024["acquisition_datetime"].isoformat(),
        "platform": "Sentinel-2",
        "sensor": "MSI",
        "nearby_road_distance_m": 85.0,
        "is_test_fixture": False,
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/eo/real-analysis/run", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["is_test_fixture"] is False
        assert "evidence_package" in data
        assert "report" in data
