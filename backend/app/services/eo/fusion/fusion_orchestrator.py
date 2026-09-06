import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.eo.fusion.models import (
    ObservationSource,
    ObservationMeasurement,
    AlignmentReport,
    MultiTemporalSeriesAnalysis,
    ContradictionFinding,
    EvidenceFusionScore,
    MultiSourceFusionResult,
    FusionRelationship,
)
from app.services.eo.fusion.alignment_service import ObservationAlignmentService
from app.services.eo.fusion.multi_temporal_analyzer import MultiTemporalChangeAnalyzer
from app.services.eo.fusion.contradiction_engine import CrossSensorContradictionEngine
from app.services.eo.fusion.evidence_scorer import EvidenceFusionScorer


class MultiSourceFusionOrchestrator:
    """
    Multi-Source Earth Observation Fusion & Advanced Change Orchestrator.
    Integrates optical (Sentinel-2), SAR (Sentinel-1), and vector infrastructure (OSM).
    Generates multi-temporal trajectories, cross-sensor corroborations, and cryptographic provenance digests.
    """

    @classmethod
    def execute_fusion_analysis(
        cls,
        aoi_id: str,
        analysis_run_id: str,
        observations: List[ObservationSource],
        measurements: Dict[str, List[ObservationMeasurement]],  # metric_name -> measurements
        sar_measurements: Optional[Dict[str, float]] = None,
        infrastructure_context: Optional[Dict[str, Any]] = None,
        is_test_fixture: bool = False,
    ) -> MultiSourceFusionResult:
        """
        Executes end-to-end multi-source fusion analysis.
        """
        fusion_id = f"fusion-{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Observation Alignments (pairwise across sequential sources)
        alignments: List[AlignmentReport] = []
        if len(observations) >= 2:
            for i in range(len(observations) - 1):
                report = ObservationAlignmentService.align_observations(
                    source=observations[i],
                    target=observations[i + 1],
                )
                alignments.append(report)

        # 2. Multi-Temporal Series Analysis for each provided metric
        temporal_series: Dict[str, MultiTemporalSeriesAnalysis] = {}
        for metric, meas_list in measurements.items():
            analysis = MultiTemporalChangeAnalyzer.analyze_series(
                metric_name=metric,
                measurements=meas_list,
            )
            temporal_series[metric] = analysis

        # 3. Cross-Sensor Contradiction & Corroboration Engine
        optical_deltas: Dict[str, float] = {}
        if "NDVI" in temporal_series:
            optical_deltas["NDVI_DELTA"] = temporal_series["NDVI"].net_absolute_delta
        if "NDWI" in temporal_series:
            optical_deltas["NDWI_DELTA"] = temporal_series["NDWI"].net_absolute_delta
        if "NDBI" in temporal_series:
            optical_deltas["NDBI_DELTA"] = temporal_series["NDBI"].net_absolute_delta

        obs_ids = [obs.id for obs in observations]
        findings = CrossSensorContradictionEngine.evaluate_cross_sensor_evidence(
            optical_measurements=optical_deltas,
            sar_measurements=sar_measurements,
            infrastructure_context=infrastructure_context,
            observation_ids=obs_ids,
        )

        # Determine overall corroboration state
        corroborations = [f for f in findings if f.relationship == FusionRelationship.CORROBORATED]
        contradictions = [f for f in findings if f.relationship == FusionRelationship.CONTRADICTED]

        if contradictions:
            overall_state = FusionRelationship.CONTRADICTED
        elif corroborations:
            overall_state = FusionRelationship.CORROBORATED
        else:
            overall_state = FusionRelationship.SUPPORTED if len(observations) >= 2 else FusionRelationship.INCONCLUSIVE

        # 4. Deterministic Evidence Scoring
        valid_obs_count = sum(
            ts.valid_observation_count for ts in temporal_series.values()
        ) // (len(temporal_series) or 1)

        evidence_score = EvidenceFusionScorer.calculate_evidence_score(
            valid_observation_count=valid_obs_count,
            mean_valid_pixel_pct=98.0,
            mean_cloud_cover_pct=min([obs.cloud_cover or 0.0 for obs in observations] or [0.0]),
            mean_spatial_overlap_pct=sum([a.spatial_overlap_percentage for a in alignments]) / (len(alignments) or 1),
            temporal_regularity_score=0.90,
            findings=findings,
        )

        # 5. Cryptographic Provenance Digest
        prov_payload = {
            "fusion_id": fusion_id,
            "aoi_id": aoi_id,
            "analysis_run_id": analysis_run_id,
            "observation_ids": obs_ids,
            "corroboration_state": overall_state.value,
            "evidence_score": evidence_score.evidence_strength_score,
            "is_test_fixture": is_test_fixture,
            "timestamp": now_iso,
        }
        prov_hash = hashlib.sha256(json.dumps(prov_payload, sort_keys=True).encode("utf-8")).hexdigest()

        return MultiSourceFusionResult(
            fusion_id=fusion_id,
            aoi_id=aoi_id,
            analysis_run_id=analysis_run_id,
            status="COMPLETED",
            corroboration_state=overall_state,
            temporal_series=temporal_series,
            contradictions=findings,
            evidence_score=evidence_score,
            alignments=alignments,
            supporting_observation_ids=[obs.id for obs in observations if not is_test_fixture] or obs_ids,
            contradictory_observation_ids=[f.finding_id for f in contradictions],
            provenance_hash_sha256=prov_hash,
            is_test_fixture=is_test_fixture,
            timestamp=now_iso,
        )
