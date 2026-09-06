from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.enums import EpistemicLevel
from app.services.eo.stac.real_discovery import SceneRankingCriteria, RankedImageryScene


class AOIValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


class JobStage(str, Enum):
    INITIALIZED = "INITIALIZED"
    RASTER_VALIDATION = "RASTER_VALIDATION"
    SPECTRAL_ANALYSIS = "SPECTRAL_ANALYSIS"
    CHANGE_DETECTION = "CHANGE_DETECTION"
    GEOSPATIAL_INTELLIGENCE = "GEOSPATIAL_INTELLIGENCE"
    FORECASTING = "FORECASTING"
    EVIDENCE_GRAPH = "EVIDENCE_GRAPH"
    GROUNDED_AI = "GROUNDED_AI"
    DOSSIER_GENERATION = "DOSSIER_GENERATION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class OperationalAOICreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    geometry: Dict[str, Any] = Field(..., description="GeoJSON geometry in EPSG:4326")
    description: Optional[str] = None


class OperationalAOIResponse(BaseModel):
    id: str
    name: str
    geometry: Dict[str, Any]
    bbox: List[float]
    area_km2: float
    is_valid: bool
    validation_message: Optional[str] = None
    created_at: str
    updated_at: str


class OperationalSceneSearchRequest(BaseModel):
    aoi_id: Optional[str] = None
    bbox: Optional[List[float]] = None
    datetime_start: Optional[str] = None
    datetime_end: Optional[str] = None
    cloud_cover_max: Optional[float] = Field(default=30.0, ge=0.0, le=100.0)
    platform: Optional[str] = None
    modality: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)


class OperationalSceneRankRequest(BaseModel):
    candidate_scenes: List[Dict[str, Any]]
    target_aoi_bbox: List[float]
    target_datetime: Optional[datetime] = None
    ranking_criteria: Optional[SceneRankingCriteria] = None


class ObservationPairSelectRequest(BaseModel):
    aoi_id: str
    t1_scene_id: str
    t1_datetime: datetime
    t1_band_paths: Dict[str, str]
    t2_scene_id: str
    t2_datetime: datetime
    t2_band_paths: Dict[str, str]
    platform: str = "Sentinel-2"
    sensor: str = "MSI"
    nearby_road_distance_m: Optional[float] = None
    is_test_fixture: bool = False


class ObservationPairSelectResponse(BaseModel):
    is_valid_pair: bool
    temporal_separation_days: float
    t1_scene_id: str
    t1_datetime: str
    t2_scene_id: str
    t2_datetime: str
    platform: str
    sensor: str
    validation_message: str
    is_test_fixture: bool


class OperationalJobCreateRequest(BaseModel):
    aoi_id: str
    aoi_name: str
    aoi_geometry: Dict[str, Any]
    t1_scene_id: str
    t1_band_paths: Dict[str, str]
    t1_datetime: datetime
    t2_scene_id: str
    t2_band_paths: Dict[str, str]
    t2_datetime: datetime
    platform: str = "Sentinel-2"
    sensor: str = "MSI"
    nearby_road_distance_m: Optional[float] = None
    is_test_fixture: bool = False


class OperationalJobStatusResponse(BaseModel):
    job_id: str
    aoi_id: str
    status: JobStatus
    current_stage: JobStage
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[float] = None
    error_metadata: Optional[Dict[str, Any]] = None
    is_test_fixture: bool
