from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.enums import EpistemicLevel
from app.services.eo.timeseries.models import TimePointMeasurement
from app.services.eo.change.thresholds import ChangeMetric, ChangeClass, ChangeThresholdConfig


class TemporalObservationPair(BaseModel):
    aoi_id: Optional[str] = None
    aoi_name: Optional[str] = None
    measurement_t1: TimePointMeasurement
    measurement_t2: TimePointMeasurement
    threshold_config: Optional[ChangeThresholdConfig] = None


class ChangeComparisonResult(BaseModel):
    aoi_id: Optional[str] = None
    aoi_name: Optional[str] = None
    metric: ChangeMetric
    unit: str
    t1_acquisition: datetime
    t2_acquisition: datetime
    interval_days: int
    t1_scene_id: str
    t2_scene_id: str
    t1_platform: str
    t2_platform: str
    t1_value: float
    t2_value: float
    absolute_delta: float
    relative_change: Optional[float] = None
    percentage_change: Optional[float] = None
    classification: ChangeClass
    is_significant: bool
    threshold_used: Dict[str, Any]
    quality_assessment: Dict[str, Any]
    provenance: Dict[str, Any]
    epistemic_level: EpistemicLevel = EpistemicLevel.CALCULATED


class SpatialChangeStatistics(BaseModel):
    valid_pixel_count: int
    nodata_pixel_count: int
    total_pixel_count: int
    valid_pixel_percentage: float

    no_change_pixels: int
    no_change_percentage: float
    no_change_area_km2: float

    increase_pixels: int
    increase_percentage: float
    increase_area_km2: float

    significant_increase_pixels: int
    significant_increase_percentage: float
    significant_increase_area_km2: float

    decrease_pixels: int
    decrease_percentage: float
    decrease_area_km2: float

    significant_decrease_pixels: int
    significant_decrease_percentage: float
    significant_decrease_area_km2: float

    min_delta: Optional[float] = None
    max_delta: Optional[float] = None
    mean_delta: Optional[float] = None
    median_delta: Optional[float] = None
    std_dev_delta: Optional[float] = None

    pixel_area_m2: float
    total_valid_area_km2: float
    area_calculation_method: str


class SpatialChangeMaskResult(BaseModel):
    metric: ChangeMetric
    t1_scene_id: str
    t2_scene_id: str
    t1_acquisition: Optional[datetime] = None
    t2_acquisition: Optional[datetime] = None
    dimensions: List[int]
    crs: str
    statistics: SpatialChangeStatistics
    threshold_config: Dict[str, Any]
    provenance: Dict[str, Any]
    epistemic_level: EpistemicLevel = EpistemicLevel.CALCULATED
    calculated_at: str
