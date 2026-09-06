from datetime import datetime, date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.enums import EpistemicLevel


class TimePointMeasurement(BaseModel):
    acquisition_datetime: datetime
    metric_name: str = Field(..., description="e.g. NDVI_MEAN, NDWI_MEAN, VEGETATED_AREA_KM2")
    value: float
    unit: str = Field(..., description="e.g. index_value, km2, percent")
    source_scene_id: str
    platform: str
    sensor: str
    cloud_cover: Optional[float] = None
    valid_pixel_percentage: float = 100.0
    epistemic_level: EpistemicLevel = EpistemicLevel.CALCULATED


class MissingObservationGap(BaseModel):
    gap_start: datetime
    gap_end: datetime
    duration_days: int
    reason: str = "NO_CLOUD_FREE_OBSERVATION"


class TemporalMeasurementSeries(BaseModel):
    aoi_id: Optional[str] = None
    aoi_name: Optional[str] = None
    metric_name: str
    unit: str
    data_points: List[TimePointMeasurement] = []
    total_observations: int
    temporal_coverage_start: Optional[datetime] = None
    temporal_coverage_end: Optional[datetime] = None
    trend_slope_per_year: Optional[float] = None
    observation_gaps: List[MissingObservationGap] = []
    quality_summary: Dict[str, Any] = {}
    epistemic_level: EpistemicLevel = EpistemicLevel.CALCULATED


class FuturePredictionForecastContract(BaseModel):
    """
    Contract interface prepared for Phase 12 forecasting models.
    Defines the strict schema required to convert historical measurement series into a FuturePrediction.
    """
    aoi_id: str
    target_year: int = Field(..., description="Must be > training_end_year")
    scenario_name: str = Field(..., description="e.g. SSP2-4.5_BUSINESS_AS_USUAL")
    metric_target: str
    training_start_year: int
    training_end_year: int
    minimum_historical_observations: int = 5
    historical_baseline_points: List[TimePointMeasurement]
    forecast_model_name: str
    forecast_model_version: str
    epistemic_level: EpistemicLevel = EpistemicLevel.PREDICTED
