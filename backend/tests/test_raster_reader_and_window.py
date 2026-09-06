import os
import tempfile
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from app.services.eo.raster.raster_reader import RasterReader
from app.services.eo.raster.raster_window import calculate_aoi_raster_window
from app.services.eo.raster.raster_exceptions import (
    RasterNotFoundError,
    RasterOutOfBoundsError,
    InvalidAOIError,
)


@pytest.fixture
def sample_geotiff():
    """
    Creates a temporary 100x100 synthetic GeoTIFF in EPSG:4326.
    Extents: [-55.0, -12.0] to [-54.0, -11.0].
    """
    temp_dir = tempfile.mkdtemp()
    tif_path = os.path.join(temp_dir, "sample_synthetic_band.tif")

    transform = from_origin(-55.0, -11.0, 0.01, 0.01)
    data = np.full((100, 100), 2500, dtype=np.uint16)
    # Set nodata pixel in corner
    data[0, 0] = 0

    with rasterio.open(
        tif_path,
        "w",
        driver="GTiff",
        height=100,
        width=100,
        count=1,
        dtype=np.uint16,
        crs="EPSG:4326",
        transform=transform,
        nodata=0,
    ) as dst:
        dst.write(data, 1)

    yield tif_path

    # Cleanup
    if os.path.exists(tif_path):
        os.remove(tif_path)
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)


def test_inspect_raster_metadata(sample_geotiff):
    meta = RasterReader.inspect_metadata(sample_geotiff)
    assert meta.width == 100
    assert meta.height == 100
    assert meta.band_count == 1
    assert meta.nodata == 0.0
    assert "4326" in meta.crs
    assert meta.bounds[0] == -55.0
    assert meta.bounds[3] == -11.0


def test_calculate_aoi_raster_window_and_read(sample_geotiff):
    aoi_geom = {
        "type": "Polygon",
        "coordinates": [
            [
                [-54.8, -11.8],
                [-54.2, -11.8],
                [-54.2, -11.2],
                [-54.8, -11.2],
                [-54.8, -11.8],
            ]
        ],
    }
    meta = RasterReader.inspect_metadata(sample_geotiff)
    trans_obj = rasterio.Affine(*meta.transform)

    window, win_trans, bounds_meta = calculate_aoi_raster_window(
        aoi_geometry=aoi_geom,
        raster_crs_str=meta.crs,
        raster_transform=trans_obj,
        raster_width=meta.width,
        raster_height=meta.height,
    )

    assert window.width > 0
    assert window.height > 0
    assert bounds_meta.bounds_wgs84 is not None

    # Read slice with window
    arr, nodata_val, slice_trans = RasterReader.read_band(sample_geotiff, band_index=1, window=window)
    assert arr.shape == (window.height, window.width)
    assert nodata_val == 0.0


def test_out_of_bounds_aoi_raises_error(sample_geotiff):
    out_aoi = {
        "type": "Polygon",
        "coordinates": [
            [
                [-10.0, 50.0],
                [-9.0, 50.0],
                [-9.0, 51.0],
                [-10.0, 51.0],
                [-10.0, 50.0],
            ]
        ],
    }
    meta = RasterReader.inspect_metadata(sample_geotiff)
    trans_obj = rasterio.Affine(*meta.transform)

    with pytest.raises(RasterOutOfBoundsError):
        calculate_aoi_raster_window(
            aoi_geometry=out_aoi,
            raster_crs_str=meta.crs,
            raster_transform=trans_obj,
            raster_width=meta.width,
            raster_height=meta.height,
        )


def test_unreachable_raster_raises_not_found():
    with pytest.raises(RasterNotFoundError):
        RasterReader.inspect_metadata("/path/to/non_existent_file.tif")
