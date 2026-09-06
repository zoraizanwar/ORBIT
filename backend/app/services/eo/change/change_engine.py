from typing import Any, Dict, Optional, Tuple
import numpy as np

from app.services.eo.change.models import (
    TemporalObservationPair,
    ChangeComparisonResult,
    SpatialChangeMaskResult,
)
from app.services.eo.change.temporal_comparator import TemporalComparator
from app.services.eo.change.spatial_mask import compute_raster_spatial_difference
from app.services.eo.change.thresholds import ChangeThresholdConfig


class ChangeDetectionEngine:
    """
    Unified Change Detection Engine coordinating tabular temporal comparisons and spatial raster difference operations.
    """

    @staticmethod
    def compare_measurements(pair: TemporalObservationPair) -> ChangeComparisonResult:
        """
        Executes pairwise temporal measurement comparison and classification.
        """
        return TemporalComparator.compare_observations(pair)

    @staticmethod
    def compute_spatial_change(
        raster_t1: np.ndarray,
        raster_t2: np.ndarray,
        nodata_t1: Optional[float] = None,
        nodata_t2: Optional[float] = None,
        pixel_res_x_m: float = 10.0,
        pixel_res_y_m: float = 10.0,
        crs_str: str = "EPSG:32621",
        center_latitude: Optional[float] = None,
        threshold_config: Optional[ChangeThresholdConfig] = None,
        t1_scene_id: str = "SCENE_T1",
        t2_scene_id: str = "SCENE_T2",
    ) -> Tuple[np.ma.MaskedArray, SpatialChangeMaskResult]:
        """
        Executes spatial raster difference analysis and pixel-level classification.
        """
        return compute_raster_spatial_difference(
            raster_t1=raster_t1,
            raster_t2=raster_t2,
            nodata_t1=nodata_t1,
            nodata_t2=nodata_t2,
            pixel_res_x_m=pixel_res_x_m,
            pixel_res_y_m=pixel_res_y_m,
            crs_str=crs_str,
            center_latitude=center_latitude,
            threshold_config=threshold_config,
            t1_scene_id=t1_scene_id,
            t2_scene_id=t2_scene_id,
        )
