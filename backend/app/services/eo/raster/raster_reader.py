import os
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pyproj
import rasterio
from rasterio.windows import Window

from app.services.eo.raster.raster_exceptions import (
    RasterNotFoundError,
    RasterCorruptedError,
    RasterError,
)
from app.services.eo.raster.raster_metadata import RasterMetadata


class RasterReader:
    """
    Local-first and Cloud-Optimized GeoTIFF (COG) reader with windowed extraction support.
    """

    @staticmethod
    def inspect_metadata(source_uri: str) -> RasterMetadata:
        """
        Reads GeoTIFF header and metadata without reading the full raster payload into memory.
        """
        try:
            with rasterio.open(source_uri) as src:
                crs_str = src.crs.to_string() if src.crs else "EPSG:4326"
                is_proj = src.crs.is_projected if src.crs else False

                # Calculate bounds
                bounds_native = [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top]

                # Convert bounds to WGS84 EPSG:4326 if needed
                bounds_wgs84 = bounds_native
                if src.crs and not src.crs.to_epsg() == 4326:
                    try:
                        transformer = pyproj.Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True)
                        min_lon, min_lat = transformer.transform(src.bounds.left, src.bounds.bottom)
                        max_lon, max_lat = transformer.transform(src.bounds.right, src.bounds.top)
                        bounds_wgs84 = [round(min_lon, 6), round(min_lat, 6), round(max_lon, 6), round(max_lat, 6)]
                    except Exception:
                        bounds_wgs84 = None

                # Transform tuple
                t = src.transform
                transform_tuple = [t.a, t.b, t.c, t.d, t.e, t.f]

                res_x, res_y = abs(src.res[0]), abs(src.res[1])

                color_interp = [ci.name for ci in src.colorinterp] if src.colorinterp else []

                return RasterMetadata(
                    source_uri=source_uri,
                    driver=src.driver,
                    width=src.width,
                    height=src.height,
                    band_count=src.count,
                    dtype=str(src.dtypes[0]),
                    crs=crs_str,
                    is_projected=is_proj,
                    nodata=float(src.nodata) if src.nodata is not None else None,
                    bounds=bounds_native,
                    bounds_wgs84=bounds_wgs84,
                    resolution_x=res_x,
                    resolution_y=res_y,
                    transform=transform_tuple,
                    is_tiled=bool(src.block_shapes and len(src.block_shapes) > 0 and src.block_shapes[0][0] > 1 and src.block_shapes[0][1] > 1),
                    block_size=src.block_shapes[0] if src.block_shapes else None,
                    color_interpretation=color_interp,
                    tags=dict(src.tags()),
                )
        except rasterio.errors.RasterioIOError as e:
            if "does not exist" in str(e).lower() or "404" in str(e):
                raise RasterNotFoundError(f"Raster source not found or unreachable: {source_uri}") from e
            raise RasterCorruptedError(f"Failed to read raster header: {str(e)}") from e
        except Exception as e:
            raise RasterError(f"Unexpected error inspecting raster {source_uri}: {str(e)}") from e

    @staticmethod
    def read_band(
        source_uri: str,
        band_index: int = 1,
        window: Optional[Window] = None,
    ) -> Tuple[np.ndarray, Optional[float], rasterio.Affine]:
        """
        Reads a 2D numpy array for a specified band and optional window.
        Returns (array, nodata_val, affine_transform).
        """
        try:
            with rasterio.open(source_uri) as src:
                if band_index < 1 or band_index > src.count:
                    raise RasterError(f"Band index {band_index} out of range (1 - {src.count}) for {source_uri}")

                arr = src.read(band_index, window=window)
                nodata = src.nodata

                # Compute affine transform for this slice
                if window is not None:
                    trans = rasterio.windows.transform(window, src.transform)
                else:
                    trans = src.transform

                return (arr, nodata, trans)
        except rasterio.errors.RasterioIOError as e:
            if "does not exist" in str(e).lower() or "404" in str(e):
                raise RasterNotFoundError(f"Raster source not found: {source_uri}") from e
            raise RasterCorruptedError(f"Error reading raster {source_uri}: {str(e)}") from e
        except Exception as e:
            raise RasterError(f"Failed to read band {band_index} from {source_uri}: {str(e)}") from e
