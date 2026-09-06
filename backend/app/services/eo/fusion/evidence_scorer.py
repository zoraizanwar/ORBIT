from typing import Any, Dict, List, Optional
from app.services.eo.fusion.models import (
    EvidenceFusionScore,
    ContradictionFinding,
    FusionRelationship,
)


class EvidenceFusionScorer:
    """
    Deterministic Evidence Fusion Scorer.
    Calculates transparent, reproducible evidence strength score [0.0 - 1.0].
    Takes into account observation quality, independent observation counts, temporal consistency,
    spatial overlap, and cross-sensor corroborations/contradictions.
    Never presents scores as statistical certainty without mathematical justification.
    """

    @classmethod
    def calculate_evidence_score(
        cls,
        valid_observation_count: int,
        mean_valid_pixel_pct: float = 95.0,
        mean_cloud_cover_pct: float = 5.0,
        mean_spatial_overlap_pct: float = 85.0,
        temporal_regularity_score: float = 0.85,
        findings: Optional[List[ContradictionFinding]] = None,
    ) -> EvidenceFusionScore:
        """
        Computes composite evidence strength score.
        """
        # 1. Observation Quality (0.0 to 1.0)
        quality_score = max(
            0.0,
            min(1.0, (mean_valid_pixel_pct / 100.0) * (1.0 - (mean_cloud_cover_pct / 100.0))),
        )

        # 2. Independent Observation Count Score (saturates at 4 observations)
        obs_count_score = min(1.0, valid_observation_count / 4.0)

        # 3. Temporal Consistency
        temp_score = max(0.0, min(1.0, temporal_regularity_score))

        # 4. Spatial Consistency
        spatial_score = max(0.0, min(1.0, mean_spatial_overlap_pct / 100.0))

        # 5. Cross-Sensor Corroboration & Contradiction Penalty
        corroboration_bonus = 0.0
        contradiction_penalty = 0.0

        if findings:
            for f in findings:
                if f.relationship == FusionRelationship.CORROBORATED:
                    corroboration_bonus += 0.15
                elif f.relationship == FusionRelationship.CONTRADICTED:
                    contradiction_penalty += 0.30

        # Cap bonuses/penalties
        corroboration_score = min(0.30, corroboration_bonus)
        contradiction_penalty = min(0.60, contradiction_penalty)

        # Weighted calculation
        raw_score = (
            (0.25 * quality_score)
            + (0.25 * obs_count_score)
            + (0.20 * temp_score)
            + (0.15 * spatial_score)
            + (0.15 * (1.0 if corroboration_score > 0 else 0.5))
            - contradiction_penalty
        )

        final_score = round(max(0.0, min(1.0, raw_score)), 3)

        scoring_inputs = {
            "valid_observation_count": valid_observation_count,
            "mean_valid_pixel_pct": mean_valid_pixel_pct,
            "mean_cloud_cover_pct": mean_cloud_cover_pct,
            "mean_spatial_overlap_pct": mean_spatial_overlap_pct,
            "temporal_regularity_score": temporal_regularity_score,
            "corroboration_bonus_raw": corroboration_bonus,
            "contradiction_penalty_raw": contradiction_penalty,
        }

        return EvidenceFusionScore(
            evidence_strength_score=final_score,
            observation_quality_score=round(quality_score, 3),
            independent_observation_count_score=round(obs_count_score, 3),
            temporal_consistency_score=round(temp_score, 3),
            spatial_consistency_score=round(spatial_score, 3),
            cross_sensor_corroboration_score=round(corroboration_score, 3),
            contradiction_penalty=round(contradiction_penalty, 3),
            scoring_inputs=scoring_inputs,
            epistemic_label="EVIDENCE_STRENGTH_SCORE",
        )
