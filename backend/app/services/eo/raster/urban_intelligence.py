from typing import Optional
import numpy as np
from pydantic import BaseModel
from app.models.enums import EpistemicLevel
from app.services.eo.raster.raster_statistics import compute_raster_statistics, RasterDistributionStatistics


class UrbanClassificationThresholds(BaseModel):
    built_up_threshold_min: float = 0.0  # NDBI > 0.0 generally indicates built-up / bare impervious surfaces


class UrbanIntelligenceSummary(BaseModel):
    index_name: str = "NDBI"
    distribution: RasterDistributionStatistics
    thresholds: UrbanClassificationThresholds
    built_up_candidate_pixel_count: int
    built_up_candidate_area_km2: float
    built_up_candidate_percentage: float
    non_built_up_area_km2: float
    non_built_up_percentage: float
    epistemic_level: EpistemicLevel = EpistemicLevel.CALCULATED


def analyze_built_up_coverage(
    ndbi_array: np.ma.MaskedArray,
    pixel_res_x: float = 10.0,
    pixel_res_y: float = 10.0,
    crs_str: str = "EPSG:32621",
    center_latitude: Optional[float] = None,
    thresholds: Optional[UrbanClassificationThresholds] = None,
) -> UrbanIntelligenceSummary:
    """
    Computes deterministic built-up and impervious surface candidate metrics based on NDBI.
    """
    t = thresholds or UrbanClassificationThresholds()
    stats = compute_raster_statistics(
        data=ndbi_array,
        pixel_resolution_x_m=pixel_res_x,
        pixel_resolution_y_m=pixel_res_y,
        crs_str=crs_str,
        center_latitude=center_latitude,
    )

    valid_mask = ~ndbi_array.mask & ~np.isnan(ndbi_array.data)
    valid_data = ndbi_array.data[valid_mask]
    total_valid = len(valid_data)

    if total_valid == 0:
        return UrbanIntelligenceSummary(
            distribution=stats,
            thresholds=t,
            built_up_candidate_pixel_count=0,
            built_up_candidate_area_km2=0.0,
            built_up_candidate_percentage=0.0,
            non_built_up_area_km2=0.0,
            non_built_up_percentage=0.0,
        )

    built_mask = valid_data >= t.built_up_threshold_min
    built_count = int(np.sum(built_mask))
    non_built_count = total_valid - built_count

    pixel_area_km2 = stats.pixel_area_m2 / 1_000_000.0

    return UrbanIntelligenceSummary(
        distribution=stats,
        thresholds=t,
        built_up_candidate_pixel_count=built_count,
        built_up_candidate_area_km2=round(built_count * pixel_area_km2, 4),
        built_up_candidate_percentage=round((built_count / total_valid) * 100.0, 2),
        non_built_up_area_km2=round(non_built_count * pixel_area_km2, 4),
        non_built_up_percentage=round((non_built_count / total_valid) * 100.0, 2),
        epistemic_level=EpistemicLevel.CALCULATED,
    )
