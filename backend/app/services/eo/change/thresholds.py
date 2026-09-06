from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field, model_validator
from app.services.eo.change.exceptions import InvalidThresholdError


class ChangeMetric(str, Enum):
    NDVI = "NDVI"
    NDWI = "NDWI"
    NDBI = "NDBI"
    SAVI = "SAVI"
    SURFACE_WATER_AREA = "SURFACE_WATER_AREA"
    VEGETATED_AREA = "VEGETATED_AREA"
    BUILT_UP_AREA = "BUILT_UP_AREA"
    CUSTOM = "CUSTOM"


class ChangeClass(str, Enum):
    NO_CHANGE = "NO_CHANGE"
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"
    SIGNIFICANT_INCREASE = "SIGNIFICANT_INCREASE"
    SIGNIFICANT_DECREASE = "SIGNIFICANT_DECREASE"
    INVALID = "INVALID"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ChangeThresholdConfig(BaseModel):
    metric: ChangeMetric = ChangeMetric.NDVI
    significant_increase_threshold: float = 0.15
    increase_threshold: float = 0.05
    decrease_threshold: float = -0.05
    significant_decrease_threshold: float = -0.15
    threshold_version: str = "1.0.0"
    min_valid_pixel_percentage: float = 70.0
    max_cloud_cover_percentage: float = 25.0
    allow_cross_sensor: bool = True

    @model_validator(mode="after")
    def validate_threshold_hierarchy(self) -> "ChangeThresholdConfig":
        if not (
            self.significant_increase_threshold
            > self.increase_threshold
            >= self.decrease_threshold
            > self.significant_decrease_threshold
        ):
            raise InvalidThresholdError(
                f"Threshold hierarchy violation: significant_increase ({self.significant_increase_threshold}) "
                f"> increase ({self.increase_threshold}) >= decrease ({self.decrease_threshold}) "
                f"> significant_decrease ({self.significant_decrease_threshold})"
            )
        return self


# Default Standard Profiles
DEFAULT_NDVI_THRESHOLDS = ChangeThresholdConfig(
    metric=ChangeMetric.NDVI,
    significant_increase_threshold=0.15,
    increase_threshold=0.05,
    decrease_threshold=-0.05,
    significant_decrease_threshold=-0.15,
    threshold_version="NDVI_CANOPY_v1",
)

DEFAULT_NDWI_THRESHOLDS = ChangeThresholdConfig(
    metric=ChangeMetric.NDWI,
    significant_increase_threshold=0.20,
    increase_threshold=0.05,
    decrease_threshold=-0.05,
    significant_decrease_threshold=-0.20,
    threshold_version="NDWI_WATER_v1",
)

DEFAULT_NDBI_THRESHOLDS = ChangeThresholdConfig(
    metric=ChangeMetric.NDBI,
    significant_increase_threshold=0.15,
    increase_threshold=0.05,
    decrease_threshold=-0.05,
    significant_decrease_threshold=-0.15,
    threshold_version="NDBI_URBAN_v1",
)

METRIC_DEFAULT_THRESHOLDS: Dict[ChangeMetric, ChangeThresholdConfig] = {
    ChangeMetric.NDVI: DEFAULT_NDVI_THRESHOLDS,
    ChangeMetric.NDWI: DEFAULT_NDWI_THRESHOLDS,
    ChangeMetric.NDBI: DEFAULT_NDBI_THRESHOLDS,
}


def get_default_thresholds_for_metric(metric: ChangeMetric) -> ChangeThresholdConfig:
    return METRIC_DEFAULT_THRESHOLDS.get(metric, DEFAULT_NDVI_THRESHOLDS)
