from typing import Optional, Tuple
import numpy as np


def apply_nodata_mask(
    data: np.ndarray,
    nodata_val: Optional[float] = None,
) -> np.ma.MaskedArray:
    """
    Wraps raw raster array into a MaskedArray, masking nodata, NaNs, and infinities.
    """
    float_data = data.astype(np.float32)
    invalid_mask = np.isnan(float_data) | np.isinf(float_data)

    if nodata_val is not None:
        invalid_mask = invalid_mask | np.isclose(float_data, nodata_val, atol=1e-4)

    return np.ma.masked_array(float_data, mask=invalid_mask)


def compute_normalized_ratio(
    band_a: np.ndarray,
    band_b: np.ndarray,
    nodata_a: Optional[float] = None,
    nodata_b: Optional[float] = None,
    clip_range: Tuple[float, float] = (-1.0, 1.0),
) -> np.ma.MaskedArray:
    """
    Computes (A - B) / (A + B) with strict zero-division and nodata handling.
    """
    ma_a = apply_nodata_mask(band_a, nodata_a)
    ma_b = apply_nodata_mask(band_b, nodata_b)

    numerator = ma_a - ma_b
    denominator = ma_a + ma_b

    # Identify zero / near-zero denominator to avoid divide-by-zero
    zero_denom_mask = np.isclose(denominator.filled(0), 0.0, atol=1e-7)

    # Combined mask
    total_mask = ma_a.mask | ma_b.mask | zero_denom_mask

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(total_mask, np.nan, numerator / denominator)

    if clip_range:
        ratio = np.clip(ratio, clip_range[0], clip_range[1])

    return np.ma.masked_array(ratio, mask=total_mask)
