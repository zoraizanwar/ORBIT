import numpy as np
import pytest
from app.services.eo.raster.spectral_indices import SpectralIndexEngine


def test_calculate_ndvi_standard():
    # NIR: 4000, RED: 1000 -> (4000 - 1000) / (4000 + 1000) = 3000 / 5000 = 0.60
    nir = np.array([[4000, 3000], [1000, 500]], dtype=np.float32)
    red = np.array([[1000, 1000], [1000, 1500]], dtype=np.float32)

    ndvi = SpectralIndexEngine.calculate_ndvi(nir, red)

    assert round(float(ndvi[0, 0]), 2) == 0.60
    assert round(float(ndvi[0, 1]), 2) == 0.50
    assert round(float(ndvi[1, 0]), 2) == 0.00
    assert round(float(ndvi[1, 1]), 2) == -0.50


def test_calculate_ndwi_standard():
    # GREEN: 3000, NIR: 1000 -> (3000 - 1000) / (3000 + 1000) = 2000 / 4000 = 0.50
    green = np.array([[3000, 500]], dtype=np.float32)
    nir = np.array([[1000, 4000]], dtype=np.float32)

    ndwi = SpectralIndexEngine.calculate_ndwi(green, nir)
    assert round(float(ndwi[0, 0]), 2) == 0.50
    assert round(float(ndwi[0, 1]), 2) == -0.78


def test_calculate_ndbi_standard():
    # SWIR: 3500, NIR: 1500 -> (3500 - 1500) / (3500 + 1500) = 2000 / 5000 = 0.40
    swir = np.array([[3500, 1000]], dtype=np.float32)
    nir = np.array([[1500, 4000]], dtype=np.float32)

    ndbi = SpectralIndexEngine.calculate_ndbi(swir, nir)
    assert round(float(ndbi[0, 0]), 2) == 0.40
    assert round(float(ndbi[0, 1]), 2) == -0.60


def test_divide_by_zero_and_nodata_handling():
    # NIR: 0, RED: 0 -> sum is 0
    nir = np.array([[0, 2000], [3000, 0]], dtype=np.float32)
    red = np.array([[0, 1000], [0, 0]], dtype=np.float32)

    ndvi = SpectralIndexEngine.calculate_ndvi(nir, red, nodata_nir=0, nodata_red=0)

    # Pixel [0, 0] must be masked because of nodata & zero sum
    assert ndvi.mask[0, 0]
    # Pixel [0, 1] is valid (NIR=2000, RED=1000 -> 0.33)
    assert not ndvi.mask[0, 1]
    assert round(float(ndvi[0, 1]), 2) == 0.33
    # Pixel [1, 1] (both 0) is masked
    assert ndvi.mask[1, 1]
