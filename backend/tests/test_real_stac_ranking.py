from datetime import datetime, timezone
import pytest
from app.models.enums import SensingModality, EpistemicLevel
from app.services.eo.stac.models import NormalizedImageryScene, RasterAssetReference
from app.services.eo.stac.real_discovery import (
    DeterministicSceneRanker,
    SceneRankingCriteria,
    RankedImageryScene,
)


def create_sample_scene(
    item_id: str,
    acq_dt: datetime,
    cloud_cover: float,
    resolution: float = 10.0,
    bbox: list = None,
    modality: SensingModality = SensingModality.OPTICAL,
) -> NormalizedImageryScene:
    return NormalizedImageryScene(
        provider="Copernicus / AWS Open Data",
        dataset_id="copernicus-s2-l2a",
        collection_id="sentinel-2-l2a",
        item_id=item_id,
        platform="Sentinel-2A",
        sensor="MSI",
        modality=modality,
        acquisition_datetime=acq_dt,
        geometry={"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]},
        bbox=bbox or [0.0, 0.0, 1.0, 1.0],
        cloud_cover=cloud_cover,
        spatial_resolution=resolution,
        processing_level="Level-2A",
        license="EU Copernicus Open Data Policy",
        attribution="© European Union, Copernicus Sentinel-2 data",
        epistemic_level=EpistemicLevel.OBSERVED,
    )


def test_deterministic_scene_ranking_cloud_cover_preference():
    """Verifies that lower cloud cover receives higher rank when dates and resolution are equal."""
    dt = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    sc1 = create_sample_scene("sc_cloud_high", dt, cloud_cover=45.0)
    sc2 = create_sample_scene("sc_cloud_low", dt, cloud_cover=2.5)

    ranked = DeterministicSceneRanker.rank_scenes([sc1, sc2], target_datetime=dt)
    assert len(ranked) == 2
    assert ranked[0].scene.item_id == "sc_cloud_low"
    assert ranked[0].cloud_cover_score > ranked[1].cloud_cover_score
    assert ranked[0].rank_score > ranked[1].rank_score


def test_deterministic_scene_ranking_temporal_proximity():
    """Verifies that scenes closer to target date receive higher temporal scores."""
    target_dt = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    sc_near = create_sample_scene("sc_near", datetime(2024, 6, 3, tzinfo=timezone.utc), cloud_cover=5.0)
    sc_far = create_sample_scene("sc_far", datetime(2024, 4, 1, tzinfo=timezone.utc), cloud_cover=5.0)

    ranked = DeterministicSceneRanker.rank_scenes([sc_near, sc_far], target_datetime=target_dt)
    assert ranked[0].scene.item_id == "sc_near"
    assert ranked[0].temporal_score > ranked[1].temporal_score


def test_deterministic_scene_ranking_spatial_overlap():
    """Verifies that spatial intersection percentage correctly scales spatial score."""
    dt = datetime(2024, 6, 15, tzinfo=timezone.utc)
    aoi_bbox = [0.0, 0.0, 1.0, 1.0]
    sc_full = create_sample_scene("sc_full", dt, cloud_cover=5.0, bbox=[0.0, 0.0, 1.0, 1.0])
    sc_partial = create_sample_scene("sc_partial", dt, cloud_cover=5.0, bbox=[0.5, 0.5, 1.5, 1.5])

    ranked = DeterministicSceneRanker.rank_scenes([sc_full, sc_partial], target_datetime=dt, aoi_bbox=aoi_bbox)
    assert ranked[0].scene.item_id == "sc_full"
    assert ranked[0].spatial_score == 1.0
    assert ranked[1].spatial_score < 1.0


def test_deterministic_scene_ranking_order_stability():
    """Verifies that ranking returns identical deterministic order across multiple invocations."""
    dt = datetime(2024, 6, 15, tzinfo=timezone.utc)
    scenes = [
        create_sample_scene(f"sc_{i}", datetime(2024, 6, i + 1, tzinfo=timezone.utc), cloud_cover=float(i * 5))
        for i in range(5)
    ]

    ranked_1 = DeterministicSceneRanker.rank_scenes(scenes, target_datetime=dt)
    ranked_2 = DeterministicSceneRanker.rank_scenes(scenes, target_datetime=dt)

    assert [r.scene.item_id for r in ranked_1] == [r.scene.item_id for r in ranked_2]
    assert [r.rank_score for r in ranked_1] == [r.rank_score for r in ranked_2]
