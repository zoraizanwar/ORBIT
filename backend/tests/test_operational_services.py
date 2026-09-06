import pytest
from datetime import datetime, timezone
from app.services.eo.operational.aoi_service import OperationalAOIService
from app.services.eo.operational.pair_service import ObservationPairService
from app.services.eo.operational.ranking_service import SceneSelectionService
from app.services.eo.operational.models import ObservationPairSelectRequest
from app.services.eo.stac.models import NormalizedImageryScene
from app.models.enums import SensingModality


def test_operational_aoi_service_valid_polygon():
    """Verifies that a valid WGS84 polygon is parsed, area computed, and session stored."""
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
    aoi = OperationalAOIService.validate_and_create_aoi("Test AOI Sinop", geom)
    assert aoi.name == "Test AOI Sinop"
    assert aoi.is_valid is True
    assert aoi.area_km2 > 0
    assert len(aoi.bbox) == 4
    assert aoi.bbox == [-55.55, -11.90, -55.45, -11.82]

    # Verify retrieval
    retrieved = OperationalAOIService.get_aoi(aoi.id)
    assert retrieved is not None
    assert retrieved.id == aoi.id


def test_operational_aoi_service_rejects_invalid_geometry():
    """Verifies that non-polygon or out-of-bounds geometries are rejected."""
    # Point instead of Polygon
    with pytest.raises(ValueError) as exc:
        OperationalAOIService.validate_and_create_aoi("Point AOI", {"type": "Point", "coordinates": [0, 0]})
    assert "Must be 'Polygon' or 'MultiPolygon'" in str(exc.value)

    # Out of bounds lat
    with pytest.raises(ValueError):
        OperationalAOIService.validate_and_create_aoi("Bad Lat", {
            "type": "Polygon",
            "coordinates": [[[0, 100], [1, 100], [1, 101], [0, 101], [0, 100]]],
        })


def test_observation_pair_service_valid_and_temporal_invariants():
    """Verifies T1 < T2 enforcement, band check, and days separation calculation."""
    t1 = datetime(2021, 6, 15, 14, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2024, 6, 20, 14, 0, 0, tzinfo=timezone.utc)

    req = ObservationPairSelectRequest(
        aoi_id="aoi-001",
        t1_scene_id="S2B_2021",
        t1_datetime=t1,
        t1_band_paths={"B04": "path/B04.tif", "B08": "path/B08.tif"},
        t2_scene_id="S2A_2024",
        t2_datetime=t2,
        t2_band_paths={"B04": "path/B04.tif", "B08": "path/B08.tif"},
    )
    resp = ObservationPairService.validate_and_select_pair(req)
    assert resp.is_valid_pair is True
    assert resp.temporal_separation_days > 1000.0
    assert resp.t1_scene_id == "S2B_2021"
    assert resp.t2_scene_id == "S2A_2024"

    # Reversed timestamps (T1 > T2) must fail
    req_reversed = ObservationPairSelectRequest(
        aoi_id="aoi-001",
        t1_scene_id="S2A_2024",
        t1_datetime=t2,
        t1_band_paths={"B04": "path/B04.tif", "B08": "path/B08.tif"},
        t2_scene_id="S2B_2021",
        t2_datetime=t1,
        t2_band_paths={"B04": "path/B04.tif", "B08": "path/B08.tif"},
    )
    with pytest.raises(ValueError) as exc:
        ObservationPairService.validate_and_select_pair(req_reversed)
    assert "must strictly precede" in str(exc.value)


def test_scene_selection_ranking_service():
    """Verifies that SceneSelectionService deterministically ranks candidate scenes."""
    scene1 = NormalizedImageryScene(
        provider="Element84",
        dataset_id="s2",
        collection_id="s2-l2a",
        item_id="S2_SCENE_CLEAR",
        platform="Sentinel-2B",
        sensor="MSI",
        modality=SensingModality.OPTICAL,
        acquisition_datetime=datetime(2024, 6, 20, 14, 0, 0, tzinfo=timezone.utc),
        geometry={"type": "Polygon", "coordinates": [[[-55.6, -11.9], [-55.4, -11.9], [-55.4, -11.8], [-55.6, -11.8], [-55.6, -11.9]]]},
        bbox=[-55.6, -11.9, -55.4, -11.8],
        cloud_cover=2.0,
        spatial_resolution=10.0,
        processing_level="Level-2A",
        license="Copernicus Open Data",
        attribution="ESA",
    )
    scene2 = NormalizedImageryScene(
        provider="Element84",
        dataset_id="s2",
        collection_id="s2-l2a",
        item_id="S2_SCENE_CLOUDY",
        platform="Sentinel-2A",
        sensor="MSI",
        modality=SensingModality.OPTICAL,
        acquisition_datetime=datetime(2024, 6, 20, 14, 0, 0, tzinfo=timezone.utc),
        geometry={"type": "Polygon", "coordinates": [[[-55.6, -11.9], [-55.4, -11.9], [-55.4, -11.8], [-55.6, -11.8], [-55.6, -11.9]]]},
        bbox=[-55.6, -11.9, -55.4, -11.8],
        cloud_cover=45.0,
        spatial_resolution=10.0,
        processing_level="Level-2A",
        license="Copernicus Open Data",
        attribution="ESA",
    )

    ranked = SceneSelectionService.rank_candidate_scenes(
        candidate_scenes=[scene2, scene1],
        target_aoi_bbox=[-55.55, -11.90, -55.45, -11.82],
    )
    assert len(ranked) == 2
    # Clear scene must rank first
    assert ranked[0].scene.item_id == "S2_SCENE_CLEAR"
    assert ranked[0].rank_score > ranked[1].rank_score
