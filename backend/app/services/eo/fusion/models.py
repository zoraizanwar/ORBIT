import hashlib
import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from app.models.enums import SensingModality, EpistemicLevel


class AlignmentStatus(str, Enum):
    ALIGNED = "ALIGNED"
    PARTIALLY_ALIGNED = "PARTIALLY_ALIGNED"
    INCOMPATIBLE = "INCOMPATIBLE"


class FusionRelationship(str, Enum):
    SUPPORTED = "SUPPORTED"
    CORROBORATED = "CORROBORATED"
    CONTRADICTED = "CONTRADICTED"
    INCONCLUSIVE = "INCONCLUSIVE"


class TemporalSeriesState(str, Enum):
    NO_CHANGE = "NO_CHANGE"
    INCREASING = "INCREASING"
    DECREASING = "DECREASING"
    PERSISTENT_CHANGE = "PERSISTENT_CHANGE"
    TEMPORARY_CHANGE = "TEMPORARY_CHANGE"
    RECOVERY = "RECOVERY"
    OSCILLATING = "OSCILLATING"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ObservationSource(BaseModel):
    id: str
    scene_id: str
    catalog: str = "Element84-AWS"
    collection: str = "sentinel-2-l2a"
    platform: str = "Sentinel-2"
    sensor: str = "MSI"
    modality: SensingModality = SensingModality.OPTICAL
    acquisition_datetime: datetime
    geometry: Dict[str, Any]
    bbox: List[float]
    gsd_meters: float = 10.0
    crs: str = "EPSG:4326"
    cloud_cover: Optional[float] = None
    asset_references: Dict[str, str] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    epistemic_level: EpistemicLevel = EpistemicLevel.OBSERVED
    is_test_fixture: bool = False


class ObservationMeasurement(BaseModel):
    observation_id: str
    metric: str  # e.g., "NDVI", "NDBI", "NDWI", "SAR_BACKSCATTER_VV", "SAR_BACKSCATTER_VH"
    value: Optional[float] = None
    statistics: Optional[Dict[str, float]] = None
    unit: str = "ratio"
    valid_pixel_percentage: float = 100.0
    nodata_percentage: float = 0.0
    uncertainty: float = 0.05
    timestamp: datetime
    algorithm_version: str = "ORBIT-Spectral-v1.2.0"
    provenance: Dict[str, Any] = Field(default_factory=dict)


class AlignmentReport(BaseModel):
    source_observation_id: str
    target_observation_id: str
    temporal_offset_days: float
    spatial_overlap_percentage: float
    source_gsd_m: float
    target_gsd_m: float
    resolution_ratio: float
    status: AlignmentStatus
    reasons: List[str] = Field(default_factory=list)
    resampling_applied: bool = False
    resampling_method: Optional[str] = None
    is_test_fixture: bool = False


class TemporalStepAnalysis(BaseModel):
    step_index: int
    t_start: str
    t_end: str
    delta_days: float
    start_value: float
    end_value: float
    absolute_delta: float
    relative_delta_percentage: float
    step_direction: str  # "INCREASING", "DECREASING", "STABLE"


class MultiTemporalSeriesAnalysis(BaseModel):
    metric: str
    observation_count: int
    valid_observation_count: int
    time_span_days: float
    baseline_value: float
    latest_value: float
    net_absolute_delta: float
    net_relative_delta_percentage: float
    overall_state: TemporalSeriesState
    persistence_ratio: float
    recovery_detected: bool
    steps: List[TemporalStepAnalysis] = Field(default_factory=list)
    rule_id: str = "RULE-MULTI-TEMPORAL-SERIES-001"
    algorithm_version: str = "ORBIT-MultiTemporal-v1.0.0"
    threshold_version: str = "v1.0"


class ContradictionFinding(BaseModel):
    finding_id: str
    relationship: FusionRelationship
    primary_sensor: str
    primary_metric: str
    primary_value: float
    secondary_sensor: str
    secondary_metric: str
    secondary_value: float
    explanation: str
    evidence_ids: List[str]


class EvidenceFusionScore(BaseModel):
    evidence_strength_score: float = Field(..., ge=0.0, le=1.0)
    observation_quality_score: float
    independent_observation_count_score: float
    temporal_consistency_score: float
    spatial_consistency_score: float
    cross_sensor_corroboration_score: float
    contradiction_penalty: float
    scoring_inputs: Dict[str, Any]
    epistemic_label: str = "EVIDENCE_STRENGTH_SCORE"


class MultiSourceFusionResult(BaseModel):
    fusion_id: str
    aoi_id: str
    analysis_run_id: str
    status: str
    corroboration_state: FusionRelationship
    temporal_series: Dict[str, MultiTemporalSeriesAnalysis]
    contradictions: List[ContradictionFinding]
    evidence_score: EvidenceFusionScore
    alignments: List[AlignmentReport]
    supporting_observation_ids: List[str]
    contradictory_observation_ids: List[str]
    provenance_hash_sha256: str
    is_test_fixture: bool = False
    timestamp: str
