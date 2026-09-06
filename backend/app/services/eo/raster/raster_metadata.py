from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class RasterWindowBounds(BaseModel):
    col_off: int = Field(..., description="Pixel column offset from top-left")
    row_off: int = Field(..., description="Pixel row offset from top-left")
    width: int = Field(..., ge=1, description="Window pixel width")
    height: int = Field(..., ge=1, description="Window pixel height")
    bounds_geo: Optional[List[float]] = Field(
        None, description="Georeferenced bounding box [min_x, min_y, max_x, max_y] in raster CRS"
    )
    bounds_wgs84: Optional[List[float]] = Field(
        None, description="Bounding box [min_lon, min_lat, max_lon, max_lat] in EPSG:4326"
    )


class RasterMetadata(BaseModel):
    source_uri: str
    driver: str
    width: int
    height: int
    band_count: int
    dtype: str
    crs: str
    is_projected: bool
    nodata: Optional[float] = None
    bounds: List[float] = Field(..., description="[min_x, min_y, max_x, max_y] in native CRS")
    bounds_wgs84: Optional[List[float]] = Field(
        None, description="[min_lon, min_lat, max_lon, max_lat] in EPSG:4326"
    )
    resolution_x: float
    resolution_y: float
    transform: List[float] = Field(..., description="Affine transform 6-tuple [a, b, c, d, e, f]")
    is_tiled: bool = True
    block_size: Optional[Tuple[int, int]] = None
    color_interpretation: List[str] = []
    tags: Dict[str, Any] = {}
