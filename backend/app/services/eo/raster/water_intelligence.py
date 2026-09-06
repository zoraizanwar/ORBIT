from typing import Optional
import numpy as np
from pydantic import BaseModel
from app.models.enums import EpistemicLevel
from app.services.eo.raster.raster_statistics import compute_raster_statistics, RasterDistributionStatistics


class WaterClassificationThresholds(BaseModel):
    water_threshold_min: float = 0.0  # NDWI >= 0.0 indicates candidate surface water


class WaterIntelligenceSummary(BaseModel):
    index_name: str = "NDWI"
    distribution: RasterDistributionStatistics
    thresholds: WaterClassificationThresholds
    water_candidate_pixel_count: int
    water_candidate_area_km2: float
    water_candidate_percentage: float
    non_water_area_km2: float
    non_water_percentage: float
    epistemic_level: EpistemicLevel = EpistemicLevel.CALCULATED


def analyze_water_coverage(
    ndwi_array: np.ma.MaskedArray,
    pixel_res_x: float = 10.0,
    pixel_res_y: float = 10.0,
    crs_str: str = "EPSG:32621",
    center_latitude: Optional[float] = None,
    thresholds: Optional[WaterClassificationThresholds] = None,
) -> WaterIntelligenceSummary:
    """
    Computes deterministic water body candidate statistics based on NDWI.
    """
    t = thresholds or WaterClassificationThresholds()
    stats = compute_raster_statistics(
        data=ndwi_array,
        pixel_resolution_x_m=pixel_res_x,
        pixel_resolution_y_m=pixel_res_y,
        crs_str=crs_str,
        center_latitude=center_latitude,
    )

    valid_mask = ~ndwi_array.mask & ~np.isnan(ndwi_array.data)
    valid_data = ndwi_array.data[valid_mask]
    total_valid = len(valid_data)

    if total_valid == 0:
        return WaterIntelligenceSummary(
            distribution=stats,
            thresholds=t,
            water_candidate_pixel_count=0,
            water_candidate_area_km2=0.0,
            water_candidate_percentage=0.0,
            non_water_area_km2=0.0,
            non_water_percentage=0.0,
        )

    water_mask = valid_data >= t.water_threshold_min
    water_count = int(np.sum(water_mask))
    non_water_count = total_valid - water_count

    pixel_area_km2 = stats.pixel_area_m2 / 1_000_000.0

    return WaterIntelligenceSummary(
        distribution=stats,
        thresholds=t,
        water_candidate_pixel_count=water_count,
        water_candidate_area_km2=round(water_count * pixel_area_km2, 4),
        water_candidate_percentage=round((water_count / total_valid) * 100.0, 2),
        non_water_area_km2=round(non_water_count * pixel_area_km2, 4),
        non_water_percentage=round((non_water_count / total_valid) * 100.0, 2),
        epistemic_level=EpistemicLevel.CALCULATED,
    )
