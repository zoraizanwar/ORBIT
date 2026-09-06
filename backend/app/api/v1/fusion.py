import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

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
from app.services.eo.fusion.fusion_orchestrator import MultiSourceFusionOrchestrator

router = APIRouter(prefix="/fusion", tags=["Multi-Source Earth Observation Fusion"])

# In-memory storage for active fusion runs
_FUSION_STORE: Dict[str, MultiSourceFusionResult] = {}


class AlignRequest(BaseModel):
    source: ObservationSource
    target: ObservationSource
    temporal_window_days: float = 14.0
    min_spatial_overlap_pct: float = 10.0


class TemporalSeriesRequest(BaseModel):
    metric: str
    measurements: List[ObservationMeasurement]


class CrossSensorCorroborationRequest(BaseModel):
    optical_measurements: Dict[str, float]
    sar_measurements: Optional[Dict[str, float]] = None
    infrastructure_context: Optional[Dict[str, Any]] = None
    observation_ids: Optional[List[str]] = None


class FusionAnalysisRequest(BaseModel):
    aoi_id: str = "aoi-sinop-mato-grosso"
    analysis_run_id: Optional[str] = None
    observations: List[ObservationSource]
    measurements: Dict[str, List[ObservationMeasurement]]
    sar_measurements: Optional[Dict[str, float]] = None
    infrastructure_context: Optional[Dict[str, Any]] = None
    is_test_fixture: bool = False


@router.post(
    "/align",
    response_model=AlignmentReport,
    summary="Align Multi-Source Observations",
    description="Evaluates spatial intersection, temporal proximity, compatible CRS, and GSD resolution ratio.",
)
async def align_observations_endpoint(req: AlignRequest) -> AlignmentReport:
    try:
        return ObservationAlignmentService.align_observations(
            source=req.source,
            target=req.target,
            temporal_window_days=req.temporal_window_days,
            min_spatial_overlap_pct=req.min_spatial_overlap_pct,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Observation alignment failed: {str(e)}",
        ) from e


@router.post(
    "/temporal-series",
    response_model=MultiTemporalSeriesAnalysis,
    summary="Analyze Multi-Temporal Change Series",
    description="Computes step-by-step delta trajectories, directional persistence, recovery, and oscillation.",
)
async def analyze_temporal_series_endpoint(
    req: TemporalSeriesRequest,
) -> MultiTemporalSeriesAnalysis:
    try:
        return MultiTemporalChangeAnalyzer.analyze_series(
            metric_name=req.metric,
            measurements=req.measurements,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Temporal series analysis failed: {str(e)}",
        ) from e


@router.post(
    "/corroboration",
    response_model=List[ContradictionFinding],
    summary="Evaluate Cross-Sensor Corroboration",
    description="Evaluates multi-modal evidence across Optical, SAR, and Vector infrastructure.",
)
async def evaluate_corroboration_endpoint(
    req: CrossSensorCorroborationRequest,
) -> List[ContradictionFinding]:
    try:
        return CrossSensorContradictionEngine.evaluate_cross_sensor_evidence(
            optical_measurements=req.optical_measurements,
            sar_measurements=req.sar_measurements,
            infrastructure_context=req.infrastructure_context,
            observation_ids=req.observation_ids,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Corroboration evaluation failed: {str(e)}",
        ) from e


@router.post(
    "/contradictions",
    response_model=List[ContradictionFinding],
    summary="Detect Cross-Sensor Contradictions",
    description="Returns identified contradiction findings across sensor modalities.",
)
async def detect_contradictions_endpoint(
    req: CrossSensorCorroborationRequest,
) -> List[ContradictionFinding]:
    try:
        findings = CrossSensorContradictionEngine.evaluate_cross_sensor_evidence(
            optical_measurements=req.optical_measurements,
            sar_measurements=req.sar_measurements,
            infrastructure_context=req.infrastructure_context,
            observation_ids=req.observation_ids,
        )
        return [f for f in findings if f.relationship == FusionRelationship.CONTRADICTED]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contradiction detection failed: {str(e)}",
        ) from e


@router.post(
    "/analyze",
    response_model=MultiSourceFusionResult,
    status_code=status.HTTP_201_CREATED,
    summary="Execute Full Multi-Source Fusion",
    description="Performs alignment, multi-temporal series, cross-sensor corroboration, and deterministic evidence scoring.",
)
async def execute_fusion_analysis_endpoint(
    req: FusionAnalysisRequest,
) -> MultiSourceFusionResult:
    try:
        run_id = req.analysis_run_id or str(uuid.uuid4())
        result = MultiSourceFusionOrchestrator.execute_fusion_analysis(
            aoi_id=req.aoi_id,
            analysis_run_id=run_id,
            observations=req.observations,
            measurements=req.measurements,
            sar_measurements=req.sar_measurements,
            infrastructure_context=req.infrastructure_context,
            is_test_fixture=req.is_test_fixture,
        )
        _FUSION_STORE[result.fusion_id] = result
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Multi-source fusion execution failed: {str(e)}",
        ) from e


@router.get(
    "/{fusion_id}",
    response_model=MultiSourceFusionResult,
    summary="Retrieve Multi-Source Fusion Result",
)
async def get_fusion_result_endpoint(fusion_id: str) -> MultiSourceFusionResult:
    if fusion_id not in _FUSION_STORE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fusion result '{fusion_id}' not found.",
        )
    return _FUSION_STORE[fusion_id]


@router.get(
    "/{fusion_id}/provenance",
    summary="Retrieve Fusion Cryptographic Provenance",
)
async def get_fusion_provenance_endpoint(fusion_id: str) -> Dict[str, Any]:
    if fusion_id not in _FUSION_STORE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fusion result '{fusion_id}' not found.",
        )
    res = _FUSION_STORE[fusion_id]
    return {
        "fusion_id": res.fusion_id,
        "analysis_run_id": res.analysis_run_id,
        "aoi_id": res.aoi_id,
        "provenance_hash_sha256": res.provenance_hash_sha256,
        "is_test_fixture": res.is_test_fixture,
        "timestamp": res.timestamp,
        "supporting_observations": res.supporting_observation_ids,
        "contradictory_findings": res.contradictory_observation_ids,
        "evidence_strength_score": res.evidence_score.evidence_strength_score,
    }


@router.get(
    "/{fusion_id}/evidence",
    summary="Retrieve Fusion Supporting & Contradictory Evidence",
)
async def get_fusion_evidence_endpoint(fusion_id: str) -> Dict[str, Any]:
    if fusion_id not in _FUSION_STORE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fusion result '{fusion_id}' not found.",
        )
    res = _FUSION_STORE[fusion_id]
    return {
        "fusion_id": res.fusion_id,
        "corroboration_state": res.corroboration_state,
        "evidence_score": res.evidence_score,
        "contradiction_findings": res.contradictions,
        "alignments": res.alignments,
        "supporting_observation_ids": res.supporting_observation_ids,
        "contradictory_observation_ids": res.contradictory_observation_ids,
    }
