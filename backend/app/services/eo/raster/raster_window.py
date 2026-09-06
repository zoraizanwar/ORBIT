from typing import Any, Dict, List, Optional, Tuple
import pyproj
import rasterio
from rasterio.windows import Window, from_bounds
from shapely.geometry import shape, box, Polygon
from shapely.ops import transform

from app.services.eo.raster.raster_exceptions import (
    InvalidAOIError,
    RasterOutOfBoundsError,
    RasterCRSMismatchError,
)
from app.services.eo.raster.raster_metadata import RasterWindowBounds


def calculate_aoi_raster_window(
    aoi_geometry: Dict[str, Any],
    raster_crs_str: str,
    raster_transform: rasterio.Affine,
    raster_width: int,
    raster_height: int,
    buffer_pixels: int = 2,
) -> Tuple[Window, rasterio.Affine, RasterWindowBounds]:
    """
    Projects AOI GeoJSON from EPSG:4326 to raster native CRS and extracts the optimal pixel reading Window.
    """
    if not aoi_geometry or not isinstance(aoi_geometry, dict):
        raise InvalidAOIError("AOI geometry must be a valid GeoJSON object")

    try:
        aoi_shp = shape(aoi_geometry)
        if not aoi_shp.is_valid:
            aoi_shp = aoi_shp.buffer(0)
    except Exception as e:
        raise InvalidAOIError(f"Failed to parse AOI geometry: {str(e)}") from e

    # 1. Transform AOI to Raster CRS
    try:
        transformer = pyproj.Transformer.from_crs("EPSG:4326", raster_crs_str, always_xy=True)
        aoi_proj = transform(transformer.transform, aoi_shp)
    except Exception as e:
        raise RasterCRSMismatchError(f"Failed to transform AOI from EPSG:4326 to {raster_crs_str}: {str(e)}") from e

    min_x, min_y, max_x, max_y = aoi_proj.bounds

    # 2. Compute raster bounds in native CRS
    r_left, r_top = raster_transform * (0, 0)
    r_right, r_bottom = raster_transform * (raster_width, raster_height)
    r_min_x, r_max_x = min(r_left, r_right), max(r_left, r_right)
    r_min_y, r_max_y = min(r_top, r_bottom), max(r_top, r_bottom)
    raster_box = box(r_min_x, r_min_y, r_max_x, r_max_y)

    # 3. Check spatial intersection
    if not aoi_proj.intersects(raster_box):
        raise RasterOutOfBoundsError(
            f"Requested AOI bounds [{min_x:.2f}, {min_y:.2f}, {max_x:.2f}, {max_y:.2f}] "
            f"do not intersect raster bounds [{r_min_x:.2f}, {r_min_y:.2f}, {r_max_x:.2f}, {r_max_y:.2f}]"
        )

    # 4. Calculate pixel window
    raw_window = from_bounds(min_x, min_y, max_x, max_y, transform=raster_transform)

    # Clamp window offsets and dimensions to raster boundaries with optional buffer
    col_off = max(0, int(raw_window.col_off) - buffer_pixels)
    row_off = max(0, int(raw_window.row_off) - buffer_pixels)
    col_end = min(raster_width, int(raw_window.col_off + raw_window.width) + buffer_pixels + 1)
    row_end = min(raster_height, int(raw_window.row_off + raw_window.height) + buffer_pixels + 1)

    win_width = max(1, col_end - col_off)
    win_height = max(1, row_end - row_off)

    clamped_window = Window(col_off, row_off, win_width, win_height)
    window_transform = rasterio.windows.transform(clamped_window, raster_transform)

    # Calculate actual window georeferenced bounds
    win_left, win_top = window_transform * (0, 0)
    win_right, win_bottom = window_transform * (win_width, win_height)
    win_min_x, win_max_x = min(win_left, win_right), max(win_left, win_right)
    win_min_y, win_max_y = min(win_top, win_bottom), max(win_top, win_bottom)

    # Transform window bounds back to WGS84 EPSG:4326 for reference
    inv_transformer = pyproj.Transformer.from_crs(raster_crs_str, "EPSG:4326", always_xy=True)
    wgs_min_lon, wgs_min_lat = inv_transformer.transform(win_min_x, win_min_y)
    wgs_max_lon, wgs_max_lat = inv_transformer.transform(win_max_x, win_max_y)

    bounds_meta = RasterWindowBounds(
        col_off=col_off,
        row_off=row_off,
        width=win_width,
        height=win_height,
        bounds_geo=[round(win_min_x, 3), round(win_min_y, 3), round(win_max_x, 3), round(win_max_y, 3)],
        bounds_wgs84=[round(wgs_min_lon, 6), round(wgs_min_lat, 6), round(wgs_max_lon, 6), round(wgs_max_lat, 6)],
    )

    return (clamped_window, window_transform, bounds_meta)
