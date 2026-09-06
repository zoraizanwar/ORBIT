import pytest
from app.services.eo.raster.band_resolver import (
    CanonicalBand,
    resolve_asset_key_for_band,
    normalize_sensor_family,
)
from app.services.eo.raster.raster_exceptions import BandNotFoundError


def test_normalize_sensor_family():
    assert normalize_sensor_family("Sentinel-2A") == "SENTINEL-2"
    assert normalize_sensor_family("Sentinel-2B") == "SENTINEL-2"
    assert normalize_sensor_family("MSI") == "SENTINEL-2"
    assert normalize_sensor_family("Landsat-8") == "LANDSAT"
    assert normalize_sensor_family("Landsat-9") == "LANDSAT"
    assert normalize_sensor_family("OLI-2") == "LANDSAT"
    assert normalize_sensor_family("Sentinel-1A") == "SENTINEL-1"
    assert normalize_sensor_family("C-SAR") == "SENTINEL-1"


def test_resolve_sentinel_2_bands():
    available = ["B02", "B03", "B04", "B08", "B11", "B12", "visual", "thumbnail"]

    assert resolve_asset_key_for_band(CanonicalBand.BLUE, available, "Sentinel-2B") == "B02"
    assert resolve_asset_key_for_band(CanonicalBand.GREEN, available, "Sentinel-2B") == "B03"
    assert resolve_asset_key_for_band(CanonicalBand.RED, available, "Sentinel-2B") == "B04"
    assert resolve_asset_key_for_band(CanonicalBand.NIR, available, "Sentinel-2B") == "B08"
    assert resolve_asset_key_for_band(CanonicalBand.SWIR_1, available, "Sentinel-2B") == "B11"
    assert resolve_asset_key_for_band(CanonicalBand.SWIR_2, available, "Sentinel-2B") == "B12"


def test_resolve_landsat_bands():
    available = ["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7", "ST_B10"]

    assert resolve_asset_key_for_band(CanonicalBand.BLUE, available, "Landsat-9") == "SR_B2"
    assert resolve_asset_key_for_band(CanonicalBand.GREEN, available, "Landsat-9") == "SR_B3"
    assert resolve_asset_key_for_band(CanonicalBand.RED, available, "Landsat-9") == "SR_B4"
    assert resolve_asset_key_for_band(CanonicalBand.NIR, available, "Landsat-9") == "SR_B5"
    assert resolve_asset_key_for_band(CanonicalBand.SWIR_1, available, "Landsat-9") == "SR_B6"
    assert resolve_asset_key_for_band(CanonicalBand.THERMAL, available, "Landsat-9") == "ST_B10"


def test_resolve_sar_bands():
    available = ["vv", "vh", "metadata"]

    assert resolve_asset_key_for_band(CanonicalBand.SAR_VV, available, "Sentinel-1A") == "vv"
    assert resolve_asset_key_for_band(CanonicalBand.SAR_VH, available, "Sentinel-1A") == "vh"


def test_resolve_missing_band_raises_error():
    available = ["B02", "B03"]  # Missing NIR and RED
    with pytest.raises(BandNotFoundError):
        resolve_asset_key_for_band(CanonicalBand.NIR, available, "Sentinel-2A")
