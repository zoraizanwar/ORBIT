import enum
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.enums import EpistemicLevel, EvidenceStrength


class ForecastMetric(str, enum.Enum):
    NDVI = "NDVI"
    NDWI = "NDWI"
    NDBI = "NDBI"
    SAVI = "SAVI"
    VEGETATED_AREA = "VEGETATED_AREA"
    SURFACE_WATER_AREA = "SURFACE_WATER_AREA"
    BUILT_UP_AREA = "BUILT_UP_AREA"
    CUSTOM = "CUSTOM"


class TemporalResolution(str, enum.Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUAL = "ANNUAL"


class AggregationMethod(str, enum.Enum):
    MEAN = "MEAN"
    MEDIAN = "MEDIAN"
    SUM = "SUM"


class ForecastScenarioType(str, enum.Enum):
    BASELINE_TREND = "BASELINE_TREND"
    SSP2_45_BUSINESS_AS_USUAL = "SSP2-4.5_BUSINESS_AS_USUAL"
    CONSERVATION_POLICY = "CONSERVATION_POLICY"
    USER_DEFINED = "USER_DEFINED"


class ForecastStatus(str, enum.Enum):
    COMPLETED = "COMPLETED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    FAILED = "FAILED"


class HistoricalObservation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    aoi_id: str
    metric: ForecastMetric
    value: float
    unit: str = "index_value"
    acquisition_datetime: datetime
    sensor: str = "Sentinel-2"
    scene_id: Optional[str] = None
    valid_pixel_pct: float = 100.0
    cloud_cover: Optional[float] = None
    epistemic_level: EpistemicLevel = EpistemicLevel.CALCULATED
    provenance: Dict[str, Any] = Field(default_factory=dict)


class QualityFilterReport(BaseModel):
    total_raw_observations: int
    accepted_count: int
    rejected_count: int
    rejection_reasons: Dict[str, int] = Field(default_factory=dict)
    validity_status: str = "PASSED"


class AggregatedObservation(BaseModel):
    period_key: str  # e.g. "2024", "2024-Q2", "2024-06"
    year: int
    month: Optional[int] = None
    quarter: Optional[int] = None
    value: float
    observation_count: int
    aggregation_method: AggregationMethod
    date_start: datetime
    date_end: datetime
    epistemic_level: EpistemicLevel = EpistemicLevel.CALCULATED
    source_observation_ids: List[str] = Field(default_factory=list)


class FeatureVector(BaseModel):
    time_coordinate: float  # e.g. elapsed years from start baseline
    year: int
    value: float
    rolling_mean_3: Optional[float] = None
    rolling_std_3: Optional[float] = None


class ForecastPredictionPoint(BaseModel):
    target_year: int
    target_date: str
    predicted_value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    confidence_level: float = 0.95
    epistemic_level: EpistemicLevel = EpistemicLevel.PREDICTED
    uncertainty_status: str = "CALCULATED"


class ModelEvaluationMetrics(BaseModel):
    mae: float
    rmse: float
    r_squared: float
    sample_size: int


class BacktestSplitResult(BaseModel):
    train_start_year: int
    train_end_year: int
    val_year: int
    actual_value: float
    predicted_value: float
    error: float
    absolute_error: float


class BacktestReport(BaseModel):
    status: str
    splits_count: int
    splits: List[BacktestSplitResult] = Field(default_factory=list)
    overall_metrics: Optional[ModelEvaluationMetrics] = None
    model_name: str
    model_version: str


class ForecastRunResult(BaseModel):
    run_id: str
    aoi_id: str
    metric: ForecastMetric
    unit: str
    model_name: str
    model_version: str
    scenario: ForecastScenarioType
    training_start_year: int
    training_end_year: int
    training_observation_count: int
    forecast_horizon_years: int
    predictions: List[ForecastPredictionPoint]
    backtest: BacktestReport
    quality_filter_report: QualityFilterReport
    provenance: Dict[str, Any]
    epistemic_level: EpistemicLevel = EpistemicLevel.PREDICTED
    evidence_strength: EvidenceStrength = EvidenceStrength.MODERATE
    status: ForecastStatus
    created_at: str


class PrepareSeriesPayload(BaseModel):
    aoi_id: str
    metric: ForecastMetric
    observations: List[HistoricalObservation]
    temporal_resolution: TemporalResolution = TemporalResolution.ANNUAL
    aggregation_method: AggregationMethod = AggregationMethod.MEDIAN
    max_cloud_cover: float = 30.0
    min_valid_pixel_pct: float = 80.0


class RunForecastPayload(BaseModel):
    project_id: Optional[uuid.UUID] = None
    aoi_id: str
    metric: ForecastMetric
    observations: List[HistoricalObservation]
    forecast_start_year: int
    forecast_end_year: int
    model_name: str = "LINEAR_TREND"
    model_version: str = "ORBIT-LT-v1"
    scenario: ForecastScenarioType = ForecastScenarioType.BASELINE_TREND
    temporal_resolution: TemporalResolution = TemporalResolution.ANNUAL
    aggregation_method: AggregationMethod = AggregationMethod.MEDIAN
    confidence_level: float = 0.95
    min_observations: int = 4
    min_span_years: float = 2.0
    run_backtest: bool = True
