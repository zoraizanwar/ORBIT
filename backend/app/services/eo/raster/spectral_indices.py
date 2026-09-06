from typing import Any, Dict, Optional, Tuple
import numpy as np
from app.services.eo.raster.nodata import compute_normalized_ratio, apply_nodata_mask


class SpectralIndexEngine:
    """
    Deterministic spectral index calculator with strict zero-division and nodata handling.
    """

    @staticmethod
    def calculate_ndvi(
        nir_band: np.ndarray,
        red_band: np.ndarray,
        nodata_nir: Optional[float] = None,
        nodata_red: Optional[float] = None,
    ) -> np.ma.MaskedArray:
        """
        Normalized Difference Vegetation Index: (NIR - RED) / (NIR + RED)
        Formula: Rouse et al. (1974)
        """
        return compute_normalized_ratio(
            band_a=nir_band,
            band_b=red_band,
            nodata_a=nodata_nir,
            nodata_b=nodata_red,
            clip_range=(-1.0, 1.0),
        )

    @staticmethod
    def calculate_ndwi(
        green_band: np.ndarray,
        nir_band: np.ndarray,
        nodata_green: Optional[float] = None,
        nodata_nir: Optional[float] = None,
    ) -> np.ma.MaskedArray:
        """
        Normalized Difference Water Index: (GREEN - NIR) / (GREEN + NIR)
        Formula: McFeeters (1996)
        """
        return compute_normalized_ratio(
            band_a=green_band,
            band_b=nir_band,
            nodata_a=nodata_green,
            nodata_b=nodata_nir,
            clip_range=(-1.0, 1.0),
        )

    @staticmethod
    def calculate_ndbi(
        swir_band: np.ndarray,
        nir_band: np.ndarray,
        nodata_swir: Optional[float] = None,
        nodata_nir: Optional[float] = None,
    ) -> np.ma.MaskedArray:
        """
        Normalized Difference Built-up Index: (SWIR - NIR) / (SWIR + NIR)
        Formula: Zha et al. (2003)
        """
        return compute_normalized_ratio(
            band_a=swir_band,
            band_b=nir_band,
            nodata_a=nodata_swir,
            nodata_b=nodata_nir,
            clip_range=(-1.0, 1.0),
        )

    @staticmethod
    def calculate_savi(
        nir_band: np.ndarray,
        red_band: np.ndarray,
        l_factor: float = 0.5,
        nodata_nir: Optional[float] = None,
        nodata_red: Optional[float] = None,
    ) -> np.ma.MaskedArray:
        """
        Soil Adjusted Vegetation Index: ((NIR - RED) / (NIR + RED + L)) * (1 + L)
        Formula: Huete (1988)
        """
        ma_nir = apply_nodata_mask(nir_band, nodata_nir)
        ma_red = apply_nodata_mask(red_band, nodata_red)

        numerator = ma_nir - ma_red
        denominator = ma_nir + ma_red + l_factor

        zero_denom = np.isclose(denominator.filled(0), 0.0, atol=1e-7)
        mask = ma_nir.mask | ma_red.mask | zero_denom

        with np.errstate(divide="ignore", invalid="ignore"):
            savi = np.where(mask, np.nan, (numerator / denominator) * (1.0 + l_factor))

        return np.ma.masked_array(np.clip(savi, -1.0, 1.0), mask=mask)
