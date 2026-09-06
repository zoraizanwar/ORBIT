from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.enums import SensingModality, EpistemicLevel
from app.services.eo.stac.models import NormalizedImageryScene


class ModalitySuitabilityAssessment(BaseModel):
    recommended_modality: SensingModality
    alternative_modality: Optional[SensingModality] = None
    optical_scene_count: int = 0
    sar_scene_count: int = 0
    average_cloud_cover: Optional[float] = None
    reason: str
    limitations: List[str] = []
    supporting_scene_ids: List[str] = []
    epistemic_level: EpistemicLevel = EpistemicLevel.CALCULATED


def assess_modality_suitability(
    scenes: List[NormalizedImageryScene],
    target_modality_preference: Optional[str] = None,
) -> ModalitySuitabilityAssessment:
    """
    Evaluates candidate scenes and calculates initial sensor suitability metrics.
    Output is strictly CALCULATED (derived from empirical metadata, not an observed sensor value).
    """
    if not scenes:
        return ModalitySuitabilityAssessment(
            recommended_modality=SensingModality.OPTICAL,
            reason="No candidate scenes found in search window",
            limitations=["Zero candidate scenes available"],
            epistemic_level=EpistemicLevel.CALCULATED,
        )

    optical_scenes = [s for s in scenes if s.modality == SensingModality.OPTICAL]
    sar_scenes = [s for s in scenes if s.modality == SensingModality.SAR]

    cloud_values = [s.cloud_cover for s in optical_scenes if s.cloud_cover is not None]
    avg_cloud = sum(cloud_values) / len(cloud_values) if cloud_values else None

    # Decision heuristics
    if target_modality_preference == "SAR_MICROWAVE" and sar_scenes:
        return ModalitySuitabilityAssessment(
            recommended_modality=SensingModality.SAR,
            alternative_modality=SensingModality.OPTICAL if optical_scenes else None,
            optical_scene_count=len(optical_scenes),
            sar_scene_count=len(sar_scenes),
            average_cloud_cover=avg_cloud,
            reason="SAR microwave explicitly preferred for all-weather penetration / structural analysis",
            supporting_scene_ids=[s.item_id for s in sar_scenes],
            epistemic_level=EpistemicLevel.CALCULATED,
        )

    if avg_cloud is not None and avg_cloud > 60.0 and sar_scenes:
        return ModalitySuitabilityAssessment(
            recommended_modality=SensingModality.SAR,
            alternative_modality=SensingModality.OPTICAL,
            optical_scene_count=len(optical_scenes),
            sar_scene_count=len(sar_scenes),
            average_cloud_cover=avg_cloud,
            reason=f"High optical cloud obscuration ({avg_cloud:.1f}% avg). C-band SAR recommended for ground penetration.",
            limitations=["SAR backscatter requires speckle filtering and terrain correction in Phase 9"],
            supporting_scene_ids=[s.item_id for s in sar_scenes],
            epistemic_level=EpistemicLevel.CALCULATED,
        )

    # Default to optical multispectral
    rec = SensingModality.OPTICAL if optical_scenes else SensingModality.SAR
    alt = SensingModality.SAR if optical_scenes and sar_scenes else None

    return ModalitySuitabilityAssessment(
        recommended_modality=rec,
        alternative_modality=alt,
        optical_scene_count=len(optical_scenes),
        sar_scene_count=len(sar_scenes),
        average_cloud_cover=avg_cloud,
        reason="Optical multispectral suitable for standard vegetative, water, and land-surface analysis.",
        supporting_scene_ids=[s.item_id for s in (optical_scenes if rec == SensingModality.OPTICAL else sar_scenes)],
        epistemic_level=EpistemicLevel.CALCULATED,
    )
