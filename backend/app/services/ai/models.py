import enum
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.enums import EpistemicLevel, EvidenceStrength


class AIInterpretationType(str, enum.Enum):
    URBAN_EXPANSION_SYNTHESIS = "URBAN_EXPANSION_SYNTHESIS"
    CANOPY_CHANGE_SYNTHESIS = "CANOPY_CHANGE_SYNTHESIS"
    WATER_DYNAMICS_SYNTHESIS = "WATER_DYNAMICS_SYNTHESIS"
    INFRASTRUCTURE_CORRIDOR_SYNTHESIS = "INFRASTRUCTURE_CORRIDOR_SYNTHESIS"
    FORECAST_SYNTHESIS = "FORECAST_SYNTHESIS"
    GENERAL_EVALUATION = "GENERAL_EVALUATION"


class ClaimType(str, enum.Enum):
    OBSERVATION = "OBSERVATION"
    MEASUREMENT = "MEASUREMENT"
    CHANGE = "CHANGE"
    CORRELATION = "CORRELATION"
    FORECAST = "FORECAST"
    INTERPRETATION = "INTERPRETATION"
    UNCERTAINTY = "UNCERTAINTY"
    RECOMMENDATION = "RECOMMENDATION"


class SupportStatus(str, enum.Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"


class RecommendationCategory(str, enum.Enum):
    MONITOR = "MONITOR"
    INVESTIGATE = "INVESTIGATE"
    COLLECT_MORE_DATA = "COLLECT_MORE_DATA"
    REVIEW_CONTRADICTION = "REVIEW_CONTRADICTION"
    PRIORITIZE_SURVEY = "PRIORITIZE_SURVEY"
    REASSESS_AFTER_NEW_OBSERVATION = "REASSESS_AFTER_NEW_OBSERVATION"


class RecommendationPriority(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ReportFormat(str, enum.Enum):
    JSON = "JSON"
    MARKDOWN = "MARKDOWN"
    PDF = "PDF"


class EvidenceItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # e.g. "SCENE", "INDEX_MEASUREMENT", "CHANGE_MASK", "ROAD_CORRIDOR", "INTELLIGENCE_EVENT", "FORECAST_PROJECTION"
    epistemic_level: EpistemicLevel
    source_id: str
    source_type: str
    value: Optional[float] = None
    unit: Optional[str] = None
    timestamp: Optional[str] = None
    geometry_reference: Optional[str] = None
    quality_score: float = 1.0
    evidence_strength: EvidenceStrength = EvidenceStrength.MODERATE
    description: str
    provenance: Dict[str, Any] = Field(default_factory=dict)


class EvidenceRelationshipItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    relationship_type: str  # e.g. "DERIVED_FROM", "SUPPORTS", "CORROBORATES", "CONTRADICTS", "LOCATED_IN"
    weight: float = 1.0
    description: Optional[str] = None


class EvidencePackage(BaseModel):
    package_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    aoi_id: str
    aoi_name: str
    analysis_run_id: Optional[str] = None
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    relationships: List[EvidenceRelationshipItem] = Field(default_factory=list)
    has_contradictions: bool = False
    contradiction_count: int = 0
    package_hash_sha256: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Claim(BaseModel):
    claim_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    claim_text: str
    claim_type: ClaimType
    epistemic_level: str = "AI_INTERPRETED"
    evidence_ids: List[str] = Field(default_factory=list)
    support_status: SupportStatus = SupportStatus.SUPPORTED
    confidence: float = 0.95
    validation_details: Dict[str, Any] = Field(default_factory=dict)


class Recommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: RecommendationCategory
    recommendation_text: str
    reason: str
    priority: RecommendationPriority
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    uncertainty_note: Optional[str] = None


class AIInterpretationResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    aoi_id: str
    analysis_run_id: Optional[str] = None
    intelligence_event_id: Optional[str] = None
    title: str
    interpretation_type: AIInterpretationType
    executive_summary: str
    claims: List[Claim] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    uncertainty_statement: str
    contradiction_statement: Optional[str] = None
    temporal_interpretation: Optional[str] = None
    spatial_interpretation: Optional[str] = None
    forecast_interpretation: Optional[str] = None
    evidence_package_hash: str
    provider_info: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    epistemic_level: str = "AI_INTERPRETED"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class InterpretRequestPayload(BaseModel):
    aoi_id: str
    analysis_run_id: Optional[str] = None
    intelligence_event_id: Optional[str] = None
    interpretation_type: AIInterpretationType = AIInterpretationType.GENERAL_EVALUATION
    user_prompt: Optional[str] = None
    target_start_date: Optional[str] = None
    target_end_date: Optional[str] = None


class ValidateClaimsPayload(BaseModel):
    evidence_package: EvidencePackage
    claims: List[Claim]


class ReportRequestPayload(BaseModel):
    aoi_id: str
    interpretation_id: Optional[str] = None
    title: str = "ORBIT Intelligence & Earth Monitoring Report"
    report_type: str = "EXECUTIVE_BRIEF"
    report_format: ReportFormat = ReportFormat.MARKDOWN
    include_decision_support: bool = True
    include_provenance_audit: bool = True


class ReportResult(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    aoi_id: str
    title: str
    report_type: str
    report_format: ReportFormat
    content_text: str
    content_pdf_base64: Optional[str] = None
    provenance_hash_sha256: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
