import enum
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.enums import EpistemicLevel, EvidenceStrength


class IntelligenceType(str, enum.Enum):
    VEGETATION_CHANGE = "VEGETATION_CHANGE"
    WATER_CHANGE = "WATER_CHANGE"
    URBAN_EXPANSION = "URBAN_EXPANSION"
    URBAN_REDUCTION = "URBAN_REDUCTION"
    INFRASTRUCTURE_CHANGE = "INFRASTRUCTURE_CHANGE"
    ROAD_CHANGE = "ROAD_CHANGE"
    LAND_USE_CHANGE = "LAND_USE_CHANGE"
    ENVIRONMENTAL_CHANGE = "ENVIRONMENTAL_CHANGE"
    SPATIAL_ANOMALY = "SPATIAL_ANOMALY"
    MULTI_INDICATOR_EVENT = "MULTI_INDICATOR_EVENT"


class EvidenceType(str, enum.Enum):
    RAW_SCENE = "RAW_SCENE"
    RASTER_ASSET = "RASTER_ASSET"
    MEASUREMENT = "MEASUREMENT"
    CHANGE_EVENT = "CHANGE_EVENT"
    SPATIAL_MASK = "SPATIAL_MASK"
    ROAD_DATA = "ROAD_DATA"
    INFRASTRUCTURE_DATA = "INFRASTRUCTURE_DATA"
    HISTORICAL_SOURCE = "HISTORICAL_SOURCE"
    DERIVED_STATISTIC = "DERIVED_STATISTIC"
    ANALYSIS_RESULT = "ANALYSIS_RESULT"


class EvidenceRelationshipType(str, enum.Enum):
    DERIVED_FROM = "DERIVED_FROM"
    SUPPORTS = "SUPPORTS"
    CORROBORATES = "CORROBORATES"
    CONTRADICTS = "CONTRADICTS"
    LOCATED_IN = "LOCATED_IN"
    TEMPORALLY_ALIGNS = "TEMPORALLY_ALIGNS"
    SPATIALLY_OVERLAPS = "SPATIALLY_OVERLAPS"
    SOURCE_OF = "SOURCE_OF"


class EvidenceNode(BaseModel):
    id: str
    node_type: EvidenceType
    label: str
    source_identifier: str
    epistemic_level: EpistemicLevel
    evidence_strength: EvidenceStrength
    acquisition_datetime: Optional[datetime] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class EvidenceEdge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_node_id: str
    target_node_id: str
    relationship_type: EvidenceRelationshipType
    weight: float = 1.0
    metadata_payload: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)


class EvidenceGraphResult(BaseModel):
    nodes: List[EvidenceNode]
    edges: List[EvidenceEdge]
    has_contradictions: bool = False
    contradiction_count: int = 0


class SpatialContextResult(BaseModel):
    nearby_roads_count: int = 0
    closest_road_name: Optional[str] = None
    closest_road_class: Optional[str] = None
    distance_to_closest_road_m: Optional[float] = None
    intersects_road_corridor: bool = False
    road_corridor_buffer_m: float = 500.0
    spatial_relationship: str = "DISJOINT"


class TemporalContextResult(BaseModel):
    start_date: datetime
    end_date: datetime
    interval_days: int
    temporal_alignment: str
    temporal_tolerance_days: int = 45


class IntelligenceObjectResult(BaseModel):
    id: str
    analysis_run_id: str
    area_of_interest_id: Optional[str] = None
    intelligence_type: IntelligenceType
    title: str
    affected_area_km2: float
    start_date: datetime
    end_date: datetime
    evidence_strength: EvidenceStrength
    epistemic_level: EpistemicLevel
    confidence: float
    rule_id: str
    rule_version: str
    algorithm_version: str
    spatial_context: SpatialContextResult
    temporal_context: TemporalContextResult
    quality_metadata: Dict[str, Any]
    provenance: Dict[str, Any]
    evidence_graph: EvidenceGraphResult
    status: str = "ACTIVE"
    created_at: str


class RuleEvaluationInput(BaseModel):
    aoi_id: Optional[str] = None
    aoi_geometry: Dict[str, Any]
    target_start_date: datetime
    target_end_date: datetime
    ndvi_delta: Optional[float] = None
    ndwi_delta: Optional[float] = None
    ndbi_delta: Optional[float] = None
    affected_area_km2: float = 0.0
    nearby_road_distance_m: Optional[float] = None
    primary_sensor: str = "Sentinel-2"
    secondary_sensor: Optional[str] = None
    secondary_sensor_signal_delta: Optional[float] = None
