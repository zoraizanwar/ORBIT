from enum import Enum
from typing import Dict, List, Optional
from app.services.eo.raster.raster_exceptions import BandNotFoundError


class CanonicalBand(str, Enum):
    COASTAL_AEROSOL = "COASTAL_AEROSOL"
    BLUE = "BLUE"
    GREEN = "GREEN"
    RED = "RED"
    RED_EDGE_1 = "RED_EDGE_1"
    RED_EDGE_2 = "RED_EDGE_2"
    RED_EDGE_3 = "RED_EDGE_3"
    NIR = "NIR"
    NIR_NARROW = "NIR_NARROW"
    SWIR_1 = "SWIR_1"
    SWIR_2 = "SWIR_2"
    THERMAL = "THERMAL"
    SAR_VV = "SAR_VV"
    SAR_VH = "SAR_VH"
    SAR_HH = "SAR_HH"
    SAR_HV = "SAR_HV"


# Sensor-specific candidate key mapping
SENSOR_BAND_MAPPINGS: Dict[str, Dict[CanonicalBand, List[str]]] = {
    "SENTINEL-2": {
        CanonicalBand.COASTAL_AEROSOL: ["B01", "B1", "coastal"],
        CanonicalBand.BLUE: ["B02", "B2", "blue"],
        CanonicalBand.GREEN: ["B03", "B3", "green"],
        CanonicalBand.RED: ["B04", "B4", "red"],
        CanonicalBand.RED_EDGE_1: ["B05", "B5", "rededge1"],
        CanonicalBand.RED_EDGE_2: ["B06", "B6", "rededge2"],
        CanonicalBand.RED_EDGE_3: ["B07", "B7", "rededge3"],
        CanonicalBand.NIR: ["B08", "B8", "nir"],
        CanonicalBand.NIR_NARROW: ["B8A", "nir08", "nir_narrow"],
        CanonicalBand.SWIR_1: ["B11", "swir16", "swir1"],
        CanonicalBand.SWIR_2: ["B12", "swir22", "swir2"],
    },
    "LANDSAT": {
        CanonicalBand.COASTAL_AEROSOL: ["B1", "SR_B1", "coastal"],
        CanonicalBand.BLUE: ["B2", "SR_B2", "blue"],
        CanonicalBand.GREEN: ["B3", "SR_B3", "green"],
        CanonicalBand.RED: ["B4", "SR_B4", "red"],
        CanonicalBand.NIR: ["B5", "SR_B5", "nir08", "nir"],
        CanonicalBand.SWIR_1: ["B6", "SR_B6", "swir16", "swir1"],
        CanonicalBand.SWIR_2: ["B7", "SR_B7", "swir22", "swir2"],
        CanonicalBand.THERMAL: ["B10", "ST_B10", "lwir11", "thermal"],
    },
    "SENTINEL-1": {
        CanonicalBand.SAR_VV: ["vv", "VV", "measurement/vv.tiff"],
        CanonicalBand.SAR_VH: ["vh", "VH", "measurement/vh.tiff"],
        CanonicalBand.SAR_HH: ["hh", "HH", "measurement/hh.tiff"],
        CanonicalBand.SAR_HV: ["hv", "HV", "measurement/hv.tiff"],
    },
}


def normalize_sensor_family(platform_or_sensor: str) -> str:
    """Normalizes platform/sensor name into standard sensor family key."""
    p_lower = platform_or_sensor.lower()
    if "sentinel-2" in p_lower or "s2" in p_lower or "msi" in p_lower:
        return "SENTINEL-2"
    elif "landsat" in p_lower or "oli" in p_lower:
        return "LANDSAT"
    elif "sentinel-1" in p_lower or "s1" in p_lower or "c-sar" in p_lower or "sar" in p_lower:
        return "SENTINEL-1"
    return "SENTINEL-2"


def resolve_asset_key_for_band(
    canonical_band: CanonicalBand,
    available_asset_keys: List[str],
    platform_or_sensor: str,
) -> str:
    """
    Translates a canonical band concept into the exact matching asset key from the available assets.
    """
    family = normalize_sensor_family(platform_or_sensor)
    candidates = SENSOR_BAND_MAPPINGS.get(family, {}).get(canonical_band, [])

    # Exact case-sensitive match
    for cand in candidates:
        if cand in available_asset_keys:
            return cand

    # Case-insensitive match
    keys_lower = {k.lower(): k for k in available_asset_keys}
    for cand in candidates:
        if cand.lower() in keys_lower:
            return keys_lower[cand.lower()]

    raise BandNotFoundError(
        f"Unable to resolve canonical band {canonical_band.value} for {platform_or_sensor}. "
        f"Available assets: {available_asset_keys}"
    )
