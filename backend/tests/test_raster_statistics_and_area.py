import numpy as np
import pytest
from app.services.eo.raster.raster_statistics import compute_raster_statistics


def test_compute_raster_statistics_distribution():
    # 100 valid pixels: numbers from 1 to 100
    data = np.arange(1, 101, dtype=np.float32).reshape(10, 10)
    stats = compute_raster_statistics(
        data=data,
        pixel_resolution_x_m=10.0,
        pixel_resolution_y_m=10.0,
        crs_str="EPSG:32621",
    )

    assert stats.min == 1.0
    assert stats.max == 100.0
    assert stats.mean == 50.5
    assert stats.median == 50.5
    assert stats.valid_pixel_count == 100
    assert stats.nodata_pixel_count == 0
    assert stats.valid_pixel_percentage == 100.0
    assert stats.pixel_area_m2 == 100.0
    assert stats.total_valid_area_km2 == 0.01


def test_compute_raster_statistics_with_masked_nodata():
    raw_data = np.array([[10.0, 20.0], [np.nan, 30.0]], dtype=np.float32)
    stats = compute_raster_statistics(
        data=raw_data,
        nodata_val=np.nan,
        pixel_resolution_x_m=10.0,
        pixel_resolution_y_m=10.0,
    )

    assert stats.valid_pixel_count == 3
    assert stats.nodata_pixel_count == 1
    assert stats.valid_pixel_percentage == 75.0
    assert stats.min == 10.0
    assert stats.max == 30.0
    assert stats.mean == 20.0


def test_geodesic_area_calculation_geographic_cosine_scaling():
    # Latitude = -11.5° (Mato Grosso)
    data = np.ones((100, 100), dtype=np.float32)
    stats = compute_raster_statistics(
        data=data,
        pixel_resolution_x_m=0.0001,
        pixel_resolution_y_m=0.0001,
        crs_str="EPSG:4326",
        center_latitude=-11.5,
    )

    assert "Cosine_Latitude" in stats.area_calculation_method
    assert stats.pixel_area_m2 > 0.0
    assert stats.total_valid_area_km2 > 0.0
