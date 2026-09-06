import pytest
from httpx import AsyncClient, ASGITransport
from pathlib import Path
from app.main import app
from app.services.eo.case_study_data import (
    generate_sinop_case_study_rasters,
    SINOP_AOI_METADATA,
    SINOP_S2_BASELINE_2021,
    SINOP_S2_CURRENT_2024,
)


@pytest.mark.asyncio
async def test_operational_aoi_api_lifecycle():
    """Verifies that an AOI session can be created, validated, and fetched via REST API."""
    geom = {
        "type": "Polygon",
        "coordinates": [[
            [-55.55, -11.90],
            [-55.45, -11.90],
            [-55.45, -11.82],
            [-55.55, -11.82],
            [-55.55, -11.90],
        ]],
    }
    payload = {"name": "Sinop Municipality AOI", "geometry": geom}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create AOI
        resp = await client.post("/api/v1/operational/aoi", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        aoi_id = data["id"]
        assert data["name"] == "Sinop Municipality AOI"
        assert data["is_valid"] is True
        assert len(data["bbox"]) == 4

        # Retrieve AOI
        get_resp = await client.get(f"/api/v1/operational/aoi/{aoi_id}")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["id"] == aoi_id
        assert get_data["area_km2"] == data["area_km2"]


@pytest.mark.asyncio
async def test_operational_pair_select_endpoint():
    """Verifies that T1/T2 selection validates temporal order and band availability via API."""
    payload = {
        "aoi_id": "aoi-sinop",
        "t1_scene_id": "S2B_2021",
        "t1_datetime": "2021-06-15T14:00:51Z",
        "t1_band_paths": {"B04": "data/S2_2021_B04.tif", "B08": "data/S2_2021_B08.tif"},
        "t2_scene_id": "S2A_2024",
        "t2_datetime": "2024-06-20T14:01:01Z",
        "t2_band_paths": {"B04": "data/S2_2024_B04.tif", "B08": "data/S2_2024_B08.tif"},
        "platform": "Sentinel-2",
        "sensor": "MSI",
        "is_test_fixture": False,
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/v1/operational/pair/select", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_valid_pair"] is True
        assert data["temporal_separation_days"] > 1000.0


@pytest.mark.asyncio
async def test_operational_job_creation_execution_results_and_provenance(tmp_path):
    """Verifies the complete analysis job lifecycle: create -> execute -> results -> provenance."""
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

    job_payload = {
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
        # 1. Create Job
        create_resp = await client.post("/api/v1/operational/jobs", json=job_payload)
        assert create_resp.status_code == 201
        job_data = create_resp.json()
        job_id = job_data["job_id"]
        assert job_data["status"] == "PENDING"

        # 2. Get Job Status
        status_resp = await client.get(f"/api/v1/operational/jobs/{job_id}")
        assert status_resp.status_code == 200
        assert status_resp.json()["job_id"] == job_id

        # 3. Execute Job
        exec_resp = await client.post(f"/api/v1/operational/jobs/{job_id}/execute")
        assert exec_resp.status_code == 200
        assert exec_resp.json()["status"] == "SUCCESS"

        # 4. Get Job Results
        results_resp = await client.get(f"/api/v1/operational/jobs/{job_id}/results")
        assert results_resp.status_code == 200
        res = results_resp.json()
        assert res["intelligence_event"]["title"] is not None
        assert res["forecast"]["status"] == "INSUFFICIENT_DATA"
        assert res["ai_interpretation"]["epistemic_level"] == "AI_INTERPRETED"

        # 5. Get Provenance
        prov_resp = await client.get(f"/api/v1/operational/jobs/{job_id}/provenance")
        assert prov_resp.status_code == 200
        prov = prov_resp.json()
        assert prov["job_id"] == job_id
        assert prov["is_test_fixture"] is False
        assert len(prov["provenance_records"]) >= 1


def test_alembic_migration_0009_script_validity():
    """Verifies that Alembic migration 0009 exists, is syntactically valid, and connects to 0008."""
    import importlib.util
    migration_file = Path(__file__).parent.parent / "alembic" / "versions" / "0009_operational_workstation.py"
    assert migration_file.exists(), "0009_operational_workstation.py must exist"

    spec = importlib.util.spec_from_file_location("migration_0009", str(migration_file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert hasattr(mod, "upgrade"), "Migration 0009 must define upgrade()"
    assert hasattr(mod, "downgrade"), "Migration 0009 must define downgrade()"
    assert mod.down_revision == "0008_grounded_ai_intelligence", "0009 must revise 0008"
    assert mod.revision == "0009_operational_workstation"
