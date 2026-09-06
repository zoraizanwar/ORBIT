import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.models.enums import SensingModality, EpistemicLevel
from app.services.eo.stac.models import (
    STACSearchRequest,
    NormalizedImageryScene,
    NormalizedBand,
    RasterAssetReference,
)


class SceneRankingCriteria(BaseModel):
    temporal_proximity_weight: float = 0.35
    cloud_cover_weight: float = 0.35
    spatial_coverage_weight: float = 0.15
    resolution_weight: float = 0.15


class RankedImageryScene(BaseModel):
    scene: NormalizedImageryScene
    rank_score: float = Field(..., ge=0.0, le=1.0, description="Deterministic overall ranking score [0.0 - 1.0]")
    temporal_score: float = Field(..., ge=0.0, le=1.0)
    cloud_cover_score: float = Field(..., ge=0.0, le=1.0)
    spatial_score: float = Field(..., ge=0.0, le=1.0)
    resolution_score: float = Field(..., ge=0.0, le=1.0)
    ranking_explanation: str
    is_test_fixture: bool = False


class DeterministicSceneRanker:
    """
    Deterministic Earth Observation Scene Ranking Engine.
    Evaluates candidate satellite scenes against rigorous operational criteria without non-deterministic heuristics.
    """

    @classmethod
    def rank_scenes(
        cls,
        scenes: List[NormalizedImageryScene],
        target_datetime: Optional[datetime] = None,
        aoi_bbox: Optional[List[float]] = None,
        preferred_modality: Optional[SensingModality] = None,
        criteria: Optional[SceneRankingCriteria] = None,
    ) -> List[RankedImageryScene]:
        """
        Ranks candidate imagery scenes using strict mathematical criteria.
        """
        if not scenes:
            return []

        crit = criteria or SceneRankingCriteria()
        target_dt = target_datetime or datetime.now(timezone.utc)
        if target_dt.tzinfo is None:
            target_dt = target_dt.replace(tzinfo=timezone.utc)

        ranked: List[RankedImageryScene] = []

        for sc in scenes:
            # 1. Temporal score: exponential decay based on absolute day difference
            sc_dt = sc.acquisition_datetime
            if sc_dt.tzinfo is None:
                sc_dt = sc_dt.replace(tzinfo=timezone.utc)
            
            day_diff = abs((target_dt - sc_dt).total_seconds()) / 86400.0
            # Half-life of 30 days
            temporal_score = max(0.0, min(1.0, math.exp(-day_diff / 30.0)))

            # 2. Cloud cover score: 1.0 for 0% cloud, 0.0 for 100% cloud (or SAR where cloud=None -> 1.0)
            if sc.modality == SensingModality.SAR or sc.cloud_cover is None:
                cloud_score = 1.0
            else:
                cloud_score = max(0.0, min(1.0, (100.0 - sc.cloud_cover) / 100.0))

            # 3. Spatial score: Bounding box intersection ratio if AOI provided
            if aoi_bbox and len(aoi_bbox) == 4 and sc.bbox and len(sc.bbox) == 4:
                spatial_score = cls._calculate_bbox_overlap(aoi_bbox, sc.bbox)
            else:
                spatial_score = 1.0

            # 4. Resolution score: 10m -> 1.0, 30m -> 0.7, 60m -> 0.4
            res = sc.spatial_resolution if sc.spatial_resolution > 0 else 10.0
            resolution_score = max(0.1, min(1.0, 10.0 / res))

            # Modality preference multiplier
            modality_multiplier = 1.0
            if preferred_modality and sc.modality != preferred_modality:
                modality_multiplier = 0.85

            # Weighted sum
            composite_score = (
                (crit.temporal_proximity_weight * temporal_score)
                + (crit.cloud_cover_weight * cloud_score)
                + (crit.spatial_coverage_weight * spatial_score)
                + (crit.resolution_weight * resolution_score)
            ) * modality_multiplier

            composite_score = round(max(0.0, min(1.0, composite_score)), 4)

            # Generate structured human-verifiable explanation
            cloud_str = f"{sc.cloud_cover:.1f}%" if sc.cloud_cover is not None else "N/A (SAR)"
            explanation = (
                f"Platform: {sc.platform} ({sc.sensor}) | Date: {sc_dt.strftime('%Y-%m-%d')} "
                f"(Δ{day_diff:.1f}d, score={temporal_score:.2f}) | Cloud: {cloud_str} (score={cloud_score:.2f}) | "
                f"Resolution: {res:.1f}m (score={resolution_score:.2f}) | Spatial Overlap: {spatial_score * 100:.1f}%"
            )

            is_simulated = "[TEST FIXTURE" in (sc.metadata_payload.get("notes", "") + sc.attribution) or sc.item_id.startswith("sim_")

            ranked.append(
                RankedImageryScene(
                    scene=sc,
                    rank_score=composite_score,
                    temporal_score=round(temporal_score, 4),
                    cloud_cover_score=round(cloud_score, 4),
                    spatial_score=round(spatial_score, 4),
                    resolution_score=round(resolution_score, 4),
                    ranking_explanation=explanation,
                    is_test_fixture=is_simulated,
                )
            )

        # Sort deterministically: descending by rank_score, then descending by acquisition_datetime, then item_id
        ranked.sort(
            key=lambda x: (x.rank_score, x.scene.acquisition_datetime.timestamp(), x.scene.item_id),
            reverse=True,
        )
        return ranked

    @staticmethod
    def _calculate_bbox_overlap(bbox_a: List[float], bbox_b: List[float]) -> float:
        """
        Calculates Intersection-over-Minimum (overlap proportion) between two EPSG:4326 bounding boxes.
        """
        min_lon_a, min_lat_a, max_lon_a, max_lat_a = bbox_a
        min_lon_b, min_lat_b, max_lon_b, max_lat_b = bbox_b

        inter_min_lon = max(min_lon_a, min_lon_b)
        inter_min_lat = max(min_lat_a, min_lat_b)
        inter_max_lon = min(max_lon_a, max_lon_b)
        inter_max_lat = min(max_lat_a, max_lat_b)

        if inter_max_lon <= inter_min_lon or inter_max_lat <= inter_min_lat:
            return 0.0

        inter_area = (inter_max_lon - inter_min_lon) * (inter_max_lat - inter_min_lat)
        area_a = (max_lon_a - min_lon_a) * (max_lat_a - min_lat_a)

        if area_a <= 0:
            return 0.0

        return max(0.0, min(1.0, inter_area / area_a))
