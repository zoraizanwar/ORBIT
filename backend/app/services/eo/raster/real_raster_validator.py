import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import rasterio
from rasterio.errors import RasterioError

from app.core.logging import logger
from app.core.security_hardening import SecurityHardening


class RasterValidationReport(BaseModel):
    is_valid: bool
    source_uri: str
    file_size_bytes: int
    sha256_checksum: str
    driver: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    band_count: Optional[int] = None
    dtype: Optional[str] = None
    crs: Optional[str] = None
    bounds: Optional[List[float]] = None
    resolution_x: Optional[float] = None
    resolution_y: Optional[float] = None
    nodata_value: Optional[float] = None
    block_shapes: Optional[List[List[int]]] = None
    is_tiled: bool = False
    validation_issues: List[str] = []
    metadata_summary: Dict[str, Any] = {}


class RealRasterValidator:
    """
    Comprehensive Pre-Analytical Earth Observation Raster Validator.
    Inspects GeoTIFF / Cloud-Optimized GeoTIFF headers without loading the full pixel array into memory.
    """

    MAX_DIMENSION = 16384
    MAX_FILE_SIZE_BYTES = 1073741824  # 1 GB

    @classmethod
    def validate_raster(
        cls,
        source_uri: str,
        expected_sha256: Optional[str] = None,
    ) -> RasterValidationReport:
        """
        Validates raster file integrity, metadata soundness, and security bounds.
        """
        issues: List[str] = []

        # 1. Clean source path
        clean_path = source_uri.replace("file://", "")
        file_p = Path(clean_path)

        if not file_p.exists():
            return RasterValidationReport(
                is_valid=False,
                source_uri=source_uri,
                file_size_bytes=0,
                sha256_checksum="",
                validation_issues=[f"Raster file not found: {source_uri}"],
            )

        # 2. File size & Path safety
        file_size = file_p.stat().st_size
        if file_size == 0:
            issues.append("File is empty (0 bytes)")
        elif file_size > cls.MAX_FILE_SIZE_BYTES:
            issues.append(f"File size ({file_size} bytes) exceeds maximum limit ({cls.MAX_FILE_SIZE_BYTES} bytes)")

        # 3. Compute SHA-256 Checksum
        hasher = hashlib.sha256()
        with open(file_p, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        actual_sha256 = hasher.hexdigest()

        if expected_sha256 and expected_sha256.lower() != actual_sha256.lower():
            issues.append(f"Checksum mismatch: expected '{expected_sha256}', computed '{actual_sha256}'")

        # 4. Rasterio Header Inspection
        driver = None
        width = None
        height = None
        band_count = None
        dtype_str = None
        crs_str = None
        bounds_list = None
        res_x = None
        res_y = None
        nodata_val = None
        block_shapes = None
        is_tiled = False
        meta_dict = {}

        try:
            with rasterio.open(file_p) as src:
                driver = src.driver
                width = src.width
                height = src.height
                band_count = src.count
                dtype_str = src.dtypes[0] if src.dtypes else None
                crs_str = str(src.crs) if src.crs else None
                b = src.bounds
                bounds_list = [round(b.left, 6), round(b.bottom, 6), round(b.right, 6), round(b.top, 6)]
                res_x, res_y = abs(src.res[0]), abs(src.res[1])
                nodata_val = float(src.nodata) if src.nodata is not None else None
                block_shapes = [list(bs) for bs in src.block_shapes] if src.block_shapes else None
                is_tiled = bool(block_shapes and len(block_shapes) > 0 and (block_shapes[0][0] > 1 or block_shapes[0][1] > 1))

                meta_dict = {
                    "transform": [src.transform[i] for i in range(6)],
                    "interleave": src.profile.get("interleave", "pixel"),
                    "tags": dict(src.tags()),
                }

                # Dimensional validation
                if width <= 0 or height <= 0:
                    issues.append(f"Invalid dimensions: width={width}, height={height}")
                if width > cls.MAX_DIMENSION or height > cls.MAX_DIMENSION:
                    issues.append(
                        f"Raster dimensions ({width}x{height}) exceed maximum allowed dimension ({cls.MAX_DIMENSION})"
                    )

                # Band count validation
                if band_count <= 0:
                    issues.append(f"Invalid band count: {band_count}")

                # CRS validation
                if not src.crs:
                    issues.append("Missing Spatial Reference System (CRS)")

                # Transform validation
                if src.transform.is_degenerate:
                    issues.append("Affine geotransform is degenerate (zero determinant)")

                # Bounds validation
                if b.left >= b.right or b.bottom >= b.top:
                    issues.append(f"Inverted or invalid spatial bounds: {bounds_list}")

                # Resolution validation
                if res_x <= 0 or res_y <= 0:
                    issues.append(f"Invalid ground sample distance: ({res_x}, {res_y})")

        except RasterioError as r_err:
            issues.append(f"Rasterio header parsing error: {str(r_err)}")
        except Exception as e:
            issues.append(f"Unexpected inspection error: {str(e)}")

        is_valid = len(issues) == 0
        if not is_valid:
            logger.warning(f"Raster validation failed for {source_uri}: {issues}")

        return RasterValidationReport(
            is_valid=is_valid,
            source_uri=source_uri,
            file_size_bytes=file_size,
            sha256_checksum=actual_sha256,
            driver=driver,
            width=width,
            height=height,
            band_count=band_count,
            dtype=dtype_str,
            crs=crs_str,
            bounds=bounds_list,
            resolution_x=res_x,
            resolution_y=res_y,
            nodata_value=nodata_val,
            block_shapes=block_shapes,
            is_tiled=is_tiled,
            validation_issues=issues,
            metadata_summary=meta_dict,
        )
