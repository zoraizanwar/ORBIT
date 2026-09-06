from pathlib import Path
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS

from app.services.eo.raster.real_raster_validator import (
    RealRasterValidator,
    RasterValidationReport,
)


def create_valid_test_geotiff(path: Path, width: int = 64, height: int = 64):
    transform = from_bounds(10.0, 50.0, 11.0, 51.0, width, height)
    crs = CRS.from_epsg(4326)
    arr = np.ones((height, width), dtype=np.uint16) * 500

    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 1,
        "dtype": rasterio.uint16,
        "crs": crs,
        "transform": transform,
        "nodata": 0,
        "tiled": True,
        "blockxsize": 32,
        "blockysize": 32,
    }
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(arr, 1)


def test_real_raster_validator_on_valid_geotiff(tmp_path):
    """Verifies that a well-formed GeoTIFF with CRS, transform, and tiles passes validation."""
    tif_path = tmp_path / "valid_band.tif"
    create_valid_test_geotiff(tif_path)

    report = RealRasterValidator.validate_raster(str(tif_path))
    assert report.is_valid is True
    assert report.width == 64
    assert report.height == 64
    assert report.band_count == 1
    assert "4326" in str(report.crs)
    assert report.is_tiled is True
    assert len(report.sha256_checksum) == 64
    assert len(report.validation_issues) == 0


def test_real_raster_validator_checksum_matching(tmp_path):
    """Verifies that expected checksum matches and mismatches are correctly identified."""
    tif_path = tmp_path / "chk_band.tif"
    create_valid_test_geotiff(tif_path)

    report1 = RealRasterValidator.validate_raster(str(tif_path))
    actual_hash = report1.sha256_checksum

    # Correct hash
    report_pass = RealRasterValidator.validate_raster(str(tif_path), expected_sha256=actual_hash)
    assert report_pass.is_valid is True

    # Bad hash
    report_fail = RealRasterValidator.validate_raster(str(tif_path), expected_sha256="0000000000000000000000000000000000000000000000000000000000000000")
    assert report_fail.is_valid is False
    assert any("mismatch" in issue.lower() for issue in report_fail.validation_issues)


def test_real_raster_validator_rejects_nonexistent_or_empty(tmp_path):
    """Verifies that missing or empty files are rejected."""
    missing_report = RealRasterValidator.validate_raster(str(tmp_path / "nonexistent.tif"))
    assert missing_report.is_valid is False
    assert "not found" in missing_report.validation_issues[0].lower()

    empty_path = tmp_path / "empty.tif"
    empty_path.write_bytes(b"")
    empty_report = RealRasterValidator.validate_raster(str(empty_path))
    assert empty_report.is_valid is False
    assert any("empty" in issue.lower() for issue in empty_report.validation_issues)
