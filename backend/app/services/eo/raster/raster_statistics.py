from typing import Any, Dict, List, Optional
import numpy as np
import pyproj
from pydantic import BaseModel, Field
from shapely.geometry import shape, Polygon
import pyproj.geod


class RasterDistributionStatistics(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    mean: Optional[float] = None
    median: Optional[float] = None
    std_dev: Optional[float] = None
    percentile_10: Optional[float] = None
    percentile_25: Optional[float] = None
    percentile_50: Optional[float] = None
    percentile_75: Optional[float] = None
    percentile_90: Optional[float] = None
    valid_pixel_count: int
    nodata_pixel_count: int
    total_pixel_count: int
    valid_pixel_percentage: float
    pixel_area_m2: float
    total_valid_area_km2: float
    area_calculation_method: str


def compute_raster_statistics(
    data: np.ndarray,
    nodata_val: Optional[float] = None,
    pixel_resolution_x_m: float = 10.0,
    pixel_resolution_y_m: float = 10.0,
    crs_str: str = "EPSG:32621",
    center_latitude: Optional[float] = None,
) -> RasterDistributionStatistics:
    """
    Computes statistical distribution and geodesically valid area on a raster array.
    """
    if isinstance(data, np.ma.MaskedArray):
        valid_mask = ~data.mask & ~np.isnan(data.data) & ~np.isinf(data.data)
        flat_valid = data.data[valid_mask].astype(np.float64)
    else:
        invalid_mask = np.isnan(data) | np.isinf(data)
        if nodata_val is not None:
            invalid_mask = invalid_mask | np.isclose(data, nodata_val, atol=1e-4)
        flat_valid = data[~invalid_mask].astype(np.float64)

    total_pixels = int(data.size)
    valid_count = int(flat_valid.size)
    nodata_count = total_pixels - valid_count
    valid_pct = round((valid_count / total_pixels) * 100.0, 2) if total_pixels > 0 else 0.0

    # 1. Geodesic Area Calculation Method
    # If geographic EPSG:4326, adjust pixel area by cos(latitude)
    if "4326" in crs_str and center_latitude is not None:
        lat_rad = np.radians(center_latitude)
        # 1 degree lat approx 111,320m; 1 deg lon approx 111,320 * cos(lat)
        dx_m = pixel_resolution_x_m * 111320.0 * np.cos(lat_rad)
        dy_m = pixel_resolution_y_m * 110540.0
        pixel_area_m2 = abs(dx_m * dy_m)
        calc_method = f"WGS84_Ellipsoidal_Cosine_Latitude_Scaled (lat={center_latitude:.2f}°)"
    else:
        pixel_area_m2 = abs(pixel_resolution_x_m * pixel_resolution_y_m)
        calc_method = f"Projected_EqualArea_Planar ({crs_str})"

    total_valid_area_km2 = round((valid_count * pixel_area_m2) / 1_000_000.0, 4)

    if valid_count == 0:
        return RasterDistributionStatistics(
            min=None,
            max=None,
            mean=None,
            median=None,
            std_dev=None,
            percentile_10=None,
            percentile_25=None,
            percentile_50=None,
            percentile_75=None,
            percentile_90=None,
            valid_pixel_count=0,
            nodata_pixel_count=total_pixels,
            total_pixel_count=total_pixels,
            valid_pixel_percentage=0.0,
            pixel_area_m2=pixel_area_m2,
            total_valid_area_km2=0.0,
            area_calculation_method=calc_method,
        )

    # 2. Distribution Statistics
    min_val = float(np.min(flat_valid))
    max_val = float(np.max(flat_valid))
    mean_val = float(np.mean(flat_valid))
    median_val = float(np.median(flat_valid))
    std_val = float(np.std(flat_valid))

    p10, p25, p50, p75, p90 = np.percentile(flat_valid, [10, 25, 50, 75, 90])

    return RasterDistributionStatistics(
        min=round(min_val, 4),
        max=round(max_val, 4),
        mean=round(mean_val, 4),
        median=round(median_val, 4),
        std_dev=round(std_val, 4),
        percentile_10=round(float(p10), 4),
        percentile_25=round(float(p25), 4),
        percentile_50=round(float(p50), 4),
        percentile_75=round(float(p75), 4),
        percentile_90=round(float(p90), 4),
        valid_pixel_count=valid_count,
        nodata_pixel_count=nodata_count,
        total_pixel_count=total_pixels,
        valid_pixel_percentage=valid_pct,
        pixel_area_m2=round(pixel_area_m2, 2),
        total_valid_area_km2=total_valid_area_km2,
        area_calculation_method=calc_method,
    )
