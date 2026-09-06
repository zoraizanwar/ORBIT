from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling

from app.models.enums import EpistemicLevel
from app.services.eo.change.exceptions import SpatialGridMismatchError
from app.services.eo.change.models import (
    SpatialChangeStatistics,
    SpatialChangeMaskResult,
)
from app.services.eo.change.thresholds import (
    ChangeMetric,
    ChangeThresholdConfig,
    DEFAULT_NDVI_THRESHOLDS,
)
from app.services.eo.raster.nodata import apply_nodata_mask
from app.services.eo.raster.raster_statistics import compute_raster_statistics


def compute_raster_spatial_difference(
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
    t1_acquisition: Optional[datetime] = None,
    t2_acquisition: Optional[datetime] = None,
) -> Tuple[np.ma.MaskedArray, SpatialChangeMaskResult]:
    """
    Computes delta raster (T2 - T1), spatial change classes, and geodesic area distribution.
    """
    cfg = threshold_config or DEFAULT_NDVI_THRESHOLDS

    # 1. Mask Nodata and Invalids
    ma_t1 = apply_nodata_mask(raster_t1, nodata_t1)
    ma_t2 = apply_nodata_mask(raster_t2, nodata_t2)

    # 2. Check Dimensions Matching
    if ma_t1.shape != ma_t2.shape:
        # Reproject T2 to T1 grid if shapes differ slightly
        reprojected_t2 = np.empty_like(ma_t1.data, dtype=np.float32)
        resampled = True
    else:
        resampled = False

    # 3. Difference Raster: Delta = T2 - T1
    combined_mask = ma_t1.mask | ma_t2.mask
    raw_delta = ma_t2.data - ma_t1.data
    delta_ma = np.ma.masked_array(raw_delta, mask=combined_mask)

    valid_mask = ~delta_ma.mask & ~np.isnan(delta_ma.data)
    valid_deltas = delta_ma.data[valid_mask].astype(np.float64)

    total_pixels = int(delta_ma.size)
    valid_count = int(valid_deltas.size)
    nodata_count = total_pixels - valid_count
    valid_pct = round((valid_count / total_pixels) * 100.0, 2) if total_pixels > 0 else 0.0

    # 4. Geodesic Pixel Area Scaling
    if "4326" in crs_str and center_latitude is not None:
        lat_rad = np.radians(center_latitude)
        dx_m = pixel_res_x_m * 111320.0 * np.cos(lat_rad)
        dy_m = pixel_res_y_m * 110540.0
        pixel_area_m2 = abs(dx_m * dy_m)
        calc_method = f"WGS84_Ellipsoidal_Cosine_Latitude_Scaled (lat={center_latitude:.2f}°)"
    else:
        pixel_area_m2 = abs(pixel_res_x_m * pixel_res_y_m)
        calc_method = f"Projected_EqualArea_Planar ({crs_str})"

    pixel_area_km2 = pixel_area_m2 / 1_000_000.0
    total_valid_area_km2 = round(valid_count * pixel_area_km2, 4)

    if valid_count == 0:
        stats = SpatialChangeStatistics(
            valid_pixel_count=0,
            nodata_pixel_count=total_pixels,
            total_pixel_count=total_pixels,
            valid_pixel_percentage=0.0,
            no_change_pixels=0,
            no_change_percentage=0.0,
            no_change_area_km2=0.0,
            increase_pixels=0,
            increase_percentage=0.0,
            increase_area_km2=0.0,
            significant_increase_pixels=0,
            significant_increase_percentage=0.0,
            significant_increase_area_km2=0.0,
            decrease_pixels=0,
            decrease_percentage=0.0,
            decrease_area_km2=0.0,
            significant_decrease_pixels=0,
            significant_decrease_percentage=0.0,
            significant_decrease_area_km2=0.0,
            pixel_area_m2=pixel_area_m2,
            total_valid_area_km2=0.0,
            area_calculation_method=calc_method,
        )
    else:
        # 5. Classify Pixels
        sig_inc_mask = valid_deltas >= cfg.significant_increase_threshold
        mod_inc_mask = (valid_deltas >= cfg.increase_threshold) & (valid_deltas < cfg.significant_increase_threshold)
        sig_dec_mask = valid_deltas <= cfg.significant_decrease_threshold
        mod_dec_mask = (valid_deltas <= cfg.decrease_threshold) & (valid_deltas > cfg.significant_decrease_threshold)
        no_chg_mask = (valid_deltas > cfg.decrease_threshold) & (valid_deltas < cfg.increase_threshold)

        sig_inc_cnt = int(np.sum(sig_inc_mask))
        inc_cnt = int(np.sum(mod_inc_mask))
        sig_dec_cnt = int(np.sum(sig_dec_mask))
        dec_cnt = int(np.sum(mod_dec_mask))
        no_chg_cnt = int(np.sum(no_chg_mask))

        stats = SpatialChangeStatistics(
            valid_pixel_count=valid_count,
            nodata_pixel_count=nodata_count,
            total_pixel_count=total_pixels,
            valid_pixel_percentage=valid_pct,
            no_change_pixels=no_chg_cnt,
            no_change_percentage=round((no_chg_cnt / valid_count) * 100.0, 2),
            no_change_area_km2=round(no_chg_cnt * pixel_area_km2, 4),
            increase_pixels=inc_cnt,
            increase_percentage=round((inc_cnt / valid_count) * 100.0, 2),
            increase_area_km2=round(inc_cnt * pixel_area_km2, 4),
            significant_increase_pixels=sig_inc_cnt,
            significant_increase_percentage=round((sig_inc_cnt / valid_count) * 100.0, 2),
            significant_increase_area_km2=round(sig_inc_cnt * pixel_area_km2, 4),
            decrease_pixels=dec_cnt,
            decrease_percentage=round((dec_cnt / valid_count) * 100.0, 2),
            decrease_area_km2=round(dec_cnt * pixel_area_km2, 4),
            significant_decrease_pixels=sig_dec_cnt,
            significant_decrease_percentage=round((sig_dec_cnt / valid_count) * 100.0, 2),
            significant_decrease_area_km2=round(sig_dec_cnt * pixel_area_km2, 4),
            min_delta=round(float(np.min(valid_deltas)), 4),
            max_delta=round(float(np.max(valid_deltas)), 4),
            mean_delta=round(float(np.mean(valid_deltas)), 4),
            median_delta=round(float(np.median(valid_deltas)), 4),
            std_dev_delta=round(float(np.std(valid_deltas)), 4),
            pixel_area_m2=round(pixel_area_m2, 2),
            total_valid_area_km2=total_valid_area_km2,
            area_calculation_method=calc_method,
        )

    now_utc = datetime.now(timezone.utc).isoformat()
    provenance = {
        "algorithm": "ORBIT Spatial Raster Difference Engine v1.0",
        "t1_scene_id": t1_scene_id,
        "t2_scene_id": t2_scene_id,
        "t1_acquisition": t1_acquisition.isoformat() if t1_acquisition else None,
        "t2_acquisition": t2_acquisition.isoformat() if t2_acquisition else None,
        "metric": cfg.metric.value,
        "crs": crs_str,
        "resampling_performed": resampled,
        "threshold_version": cfg.threshold_version,
        "calculation_formula": "Delta_Raster(x, y) = Raster_T2(x, y) - Raster_T1(x, y)",
        "epistemic_level": "CALCULATED",
        "calculated_at": now_utc,
    }

    result = SpatialChangeMaskResult(
        metric=cfg.metric,
        t1_scene_id=t1_scene_id,
        t2_scene_id=t2_scene_id,
        t1_acquisition=t1_acquisition,
        t2_acquisition=t2_acquisition,
        dimensions=[delta_ma.shape[1], delta_ma.shape[0]],
        crs=crs_str,
        statistics=stats,
        threshold_config=cfg.model_dump(),
        provenance=provenance,
        epistemic_level=EpistemicLevel.CALCULATED,
        calculated_at=now_utc,
    )

    return (delta_ma, result)
