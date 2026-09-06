from typing import Dict, Optional
import numpy as np
from pydantic import BaseModel, Field
from app.models.enums import EpistemicLevel
from app.services.eo.raster.raster_statistics import compute_raster_statistics, RasterDistributionStatistics


class VegetationClassificationThresholds(BaseModel):
    non_vegetated_max: float = 0.2
    low_vegetation_max: float = 0.4
    moderate_vegetation_max: float = 0.6
    dense_vegetation_min: float = 0.6


class VegetationIntelligenceSummary(BaseModel):
    index_name: str = "NDVI"
    distribution: RasterDistributionStatistics
    thresholds: VegetationClassificationThresholds
    non_vegetated_area_km2: float
    non_vegetated_percentage: float
    low_vegetation_area_km2: float
    low_vegetation_percentage: float
    moderate_vegetation_area_km2: float
    moderate_vegetation_percentage: float
    dense_vegetation_area_km2: float
    dense_vegetation_percentage: float
    total_vegetated_area_km2: float
    total_vegetated_percentage: float
    epistemic_level: EpistemicLevel = EpistemicLevel.CALCULATED


def analyze_vegetation_canopy(
    ndvi_array: np.ma.MaskedArray,
    pixel_res_x: float = 10.0,
    pixel_res_y: float = 10.0,
    crs_str: str = "EPSG:32621",
    center_latitude: Optional[float] = None,
    thresholds: Optional[VegetationClassificationThresholds] = None,
) -> VegetationIntelligenceSummary:
    """
    Computes deterministic vegetation canopy metrics and stratified cover classes from NDVI.
    """
    t = thresholds or VegetationClassificationThresholds()
    stats = compute_raster_statistics(
        data=ndvi_array,
        pixel_resolution_x_m=pixel_res_x,
        pixel_resolution_y_m=pixel_res_y,
        crs_str=crs_str,
        center_latitude=center_latitude,
    )

    valid_mask = ~ndvi_array.mask & ~np.isnan(ndvi_array.data)
    valid_data = ndvi_array.data[valid_mask]
    total_valid = len(valid_data)

    if total_valid == 0:
        return VegetationIntelligenceSummary(
            distribution=stats,
            thresholds=t,
            non_vegetated_area_km2=0.0,
            non_vegetated_percentage=0.0,
            low_vegetation_area_km2=0.0,
            low_vegetation_percentage=0.0,
            moderate_vegetation_area_km2=0.0,
            moderate_vegetation_percentage=0.0,
            dense_vegetation_area_km2=0.0,
            dense_vegetation_percentage=0.0,
            total_vegetated_area_km2=0.0,
            total_vegetated_percentage=0.0,
        )

    # Classify pixels
    non_veg_mask = valid_data < t.non_vegetated_max
    low_veg_mask = (valid_data >= t.non_vegetated_max) & (valid_data < t.low_vegetation_max)
    mod_veg_mask = (valid_data >= t.low_vegetation_max) & (valid_data < t.moderate_vegetation_max)
    dense_veg_mask = valid_data >= t.dense_vegetation_min

    non_count = int(np.sum(non_veg_mask))
    low_count = int(np.sum(low_veg_mask))
    mod_count = int(np.sum(mod_veg_mask))
    dense_count = int(np.sum(dense_veg_mask))
    veg_total_count = low_count + mod_count + dense_count

    pixel_area_km2 = stats.pixel_area_m2 / 1_000_000.0

    return VegetationIntelligenceSummary(
        distribution=stats,
        thresholds=t,
        non_vegetated_area_km2=round(non_count * pixel_area_km2, 4),
        non_vegetated_percentage=round((non_count / total_valid) * 100.0, 2),
        low_vegetation_area_km2=round(low_count * pixel_area_km2, 4),
        low_vegetation_percentage=round((low_count / total_valid) * 100.0, 2),
        moderate_vegetation_area_km2=round(mod_count * pixel_area_km2, 4),
        moderate_vegetation_percentage=round((mod_count / total_valid) * 100.0, 2),
        dense_vegetation_area_km2=round(dense_count * pixel_area_km2, 4),
        dense_vegetation_percentage=round((dense_count / total_valid) * 100.0, 2),
        total_vegetated_area_km2=round(veg_total_count * pixel_area_km2, 4),
        total_vegetated_percentage=round((veg_total_count / total_valid) * 100.0, 2),
        epistemic_level=EpistemicLevel.CALCULATED,
    )
