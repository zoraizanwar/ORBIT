import pytest
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.enums import SensingModality


@pytest.mark.asyncio
async def test_fusion_align_and_temporal_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Align endpoint
        align_payload = {
            "source": {
                "id": "obs-1",
                "scene_id": "S2_2021",
                "acquisition_datetime": "2021-06-15T14:00:00Z",
                "geometry": {"type": "Polygon", "coordinates": [[[-55.6, -11.9], [-55.4, -11.9], [-55.4, -11.8], [-55.6, -11.8], [-55.6, -11.9]]]},
                "bbox": [-55.6, -11.9, -55.4, -11.8],
                "gsd_meters": 10.0,
                "crs": "EPSG:4326",
                "is_test_fixture": True,
            },
            "target": {
                "id": "obs-2",
                "scene_id": "S2_2024",
                "acquisition_datetime": "2024-06-20T14:00:00Z",
                "geometry": {"type": "Polygon", "coordinates": [[[-55.6, -11.9], [-55.4, -11.9], [-55.4, -11.8], [-55.6, -11.8], [-55.6, -11.9]]]},
                "bbox": [-55.6, -11.9, -55.4, -11.8],
                "gsd_meters": 10.0,
                "crs": "EPSG:4326",
                "is_test_fixture": True,
            },
            "temporal_window_days": 1500.0,
            "min_spatial_overlap_pct": 10.0,
        }
        res_align = await client.post("/api/v1/fusion/align", json=align_payload)
        assert res_align.status_code == 200
        assert res_align.json()["status"] == "ALIGNED"

        # 2. Temporal Series endpoint
        ts_payload = {
            "metric": "NDVI",
            "measurements": [
                {"observation_id": "obs-1", "metric": "NDVI", "value": 0.85, "timestamp": "2021-06-15T14:00:00Z"},
                {"observation_id": "obs-2", "metric": "NDVI", "value": 0.65, "timestamp": "2022-06-15T14:00:00Z"},
                {"observation_id": "obs-3", "metric": "NDVI", "value": 0.45, "timestamp": "2023-06-15T14:00:00Z"},
            ],
        }
        res_ts = await client.post("/api/v1/fusion/temporal-series", json=ts_payload)
        assert res_ts.status_code == 200
        ts_data = res_ts.json()
        assert ts_data["overall_state"] == "PERSISTENT_CHANGE"
        assert ts_data["valid_observation_count"] == 3


@pytest.mark.asyncio
async def test_fusion_analyze_provenance_and_evidence():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "aoi_id": "aoi-sinop-mato-grosso",
            "observations": [
                {
                    "id": "obs-t1",
                    "scene_id": "S2_2021",
                    "acquisition_datetime": "2021-06-15T14:00:00Z",
                    "geometry": {"type": "Polygon", "coordinates": [[[-55.6, -11.9], [-55.4, -11.9], [-55.4, -11.8], [-55.6, -11.8], [-55.6, -11.9]]]},
                    "bbox": [-55.6, -11.9, -55.4, -11.8],
                    "gsd_meters": 10.0,
                    "crs": "EPSG:4326",
                    "is_test_fixture": False,
                },
                {
                    "id": "obs-t2",
                    "scene_id": "S2_2024",
                    "acquisition_datetime": "2024-06-20T14:00:00Z",
                    "geometry": {"type": "Polygon", "coordinates": [[[-55.6, -11.9], [-55.4, -11.9], [-55.4, -11.8], [-55.6, -11.8], [-55.6, -11.9]]]},
                    "bbox": [-55.6, -11.9, -55.4, -11.8],
                    "gsd_meters": 10.0,
                    "crs": "EPSG:4326",
                    "is_test_fixture": False,
                },
            ],
            "measurements": {
                "NDVI": [
                    {"observation_id": "obs-t1", "metric": "NDVI", "value": 0.852, "timestamp": "2021-06-15T14:00:00Z"},
                    {"observation_id": "obs-t2", "metric": "NDVI", "value": 0.481, "timestamp": "2024-06-20T14:00:00Z"},
                ]
            },
            "infrastructure_context": {
                "nearest_road_distance_meters": 350.0,
            },
            "is_test_fixture": False,
        }

        # 1. Analyze
        res = await client.post("/api/v1/fusion/analyze", json=payload)
        assert res.status_code == 201
        data = res.json()
        fusion_id = data["fusion_id"]
        assert data["status"] == "COMPLETED"
        assert len(data["provenance_hash_sha256"]) == 64
        assert data["corroboration_state"] == "CORROBORATED"

        # 2. Get result
        res_get = await client.get(f"/api/v1/fusion/{fusion_id}")
        assert res_get.status_code == 200
        assert res_get.json()["fusion_id"] == fusion_id

        # 3. Get provenance
        res_prov = await client.get(f"/api/v1/fusion/{fusion_id}/provenance")
        assert res_prov.status_code == 200
        assert res_prov.json()["provenance_hash_sha256"] == data["provenance_hash_sha256"]
        assert res_prov.json()["is_test_fixture"] is False

        # 4. Get evidence
        res_ev = await client.get(f"/api/v1/fusion/{fusion_id}/evidence")
        assert res_ev.status_code == 200
        assert len(res_ev.json()["alignments"]) >= 1


def test_alembic_migration_0010_script_validity():
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    head_rev = script.get_current_head()

    assert head_rev == "0010_multi_source_fusion"
    rev = script.get_revision("0010_multi_source_fusion")
    assert rev is not None
    assert rev.down_revision == "0009_operational_workstation"
