import numpy as np
import pytest
from app.models.enums import EpistemicLevel
from app.services.eo.change.spatial_mask import compute_raster_spatial_difference
from app.services.eo.change.thresholds import (
    ChangeThresholdConfig,
    ChangeMetric,
)


def test_spatial_difference_pixel_classification():
    # 5 pixels:
    # 1. Sig decrease: -0.25 (0.50 -> 0.25)
    # 2. Moderate decrease: -0.08 (0.50 -> 0.42)
    # 3. No change: 0.01 (0.50 -> 0.51)
    # 4. Moderate increase: 0.08 (0.50 -> 0.58)
    # 5. Sig increase: 0.25 (0.50 -> 0.75)
    r_t1 = np.array([[0.50, 0.50, 0.50, 0.50, 0.50]], dtype=np.float32)
    r_t2 = np.array([[0.25, 0.42, 0.51, 0.58, 0.75]], dtype=np.float32)

    delta_ma, result = compute_raster_spatial_difference(
        raster_t1=r_t1,
        raster_t2=r_t2,
        pixel_res_x_m=10.0,
        pixel_res_y_m=10.0,
        crs_str="EPSG:32621",
    )

    stats = result.statistics
    assert stats.valid_pixel_count == 5
    assert stats.nodata_pixel_count == 0
    assert stats.significant_decrease_pixels == 1
    assert stats.decrease_pixels == 1
    assert stats.no_change_pixels == 1
    assert stats.increase_pixels == 1
    assert stats.significant_increase_pixels == 1
    assert stats.min_delta == -0.25
    assert stats.max_delta == 0.25
    assert result.epistemic_level == EpistemicLevel.CALCULATED


def test_spatial_difference_nodata_preservation():
    # 4 pixels: one is nodata (masked)
    r_t1 = np.array([[0.50, 0.50], [0.50, np.nan]], dtype=np.float32)
    r_t2 = np.array([[0.70, 0.50], [0.30, 0.50]], dtype=np.float32)

    delta_ma, result = compute_raster_spatial_difference(
        raster_t1=r_t1,
        raster_t2=r_t2,
        nodata_t1=np.nan,
        pixel_res_x_m=10.0,
        pixel_res_y_m=10.0,
    )

    stats = result.statistics
    assert stats.valid_pixel_count == 3
    assert stats.nodata_pixel_count == 1
    assert stats.valid_pixel_percentage == 75.0
    # Nodata must never be counted as no_change
    assert stats.no_change_pixels == 1
    assert stats.significant_increase_pixels == 1
    assert stats.significant_decrease_pixels == 1


def test_spatial_difference_nan_inf_safety():
    # Test with Inf and NaN values
    r_t1 = np.array([[0.50, np.inf], [0.50, 0.50]], dtype=np.float32)
    r_t2 = np.array([[0.70, 0.50], [-np.inf, 0.50]], dtype=np.float32)

    delta_ma, result = compute_raster_spatial_difference(
        raster_t1=r_t1,
        raster_t2=r_t2,
        pixel_res_x_m=10.0,
        pixel_res_y_m=10.0,
    )

    stats = result.statistics
    # Only 2 finite valid pixels
    assert stats.valid_pixel_count == 2
    assert stats.nodata_pixel_count == 2
    assert stats.significant_increase_pixels == 1
    assert stats.no_change_pixels == 1


def test_spatial_difference_valid_pixel_sum_invariants():
    r_t1 = np.random.uniform(0.2, 0.8, size=(20, 20)).astype(np.float32)
    r_t2 = np.random.uniform(0.2, 0.8, size=(20, 20)).astype(np.float32)

    # Sprinkle nodata
    r_t1[0:5, 0:5] = np.nan

    delta_ma, result = compute_raster_spatial_difference(
        raster_t1=r_t1,
        raster_t2=r_t2,
        nodata_t1=np.nan,
        pixel_res_x_m=10.0,
        pixel_res_y_m=10.0,
    )

    stats = result.statistics
    sum_classes = (
        stats.no_change_pixels
        + stats.increase_pixels
        + stats.significant_increase_pixels
        + stats.decrease_pixels
        + stats.significant_decrease_pixels
    )

    assert sum_classes == stats.valid_pixel_count
    assert stats.valid_pixel_count + stats.nodata_pixel_count == stats.total_pixel_count

