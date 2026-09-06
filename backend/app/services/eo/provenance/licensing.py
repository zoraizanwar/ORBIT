from typing import Dict, Optional, Any
from app.models.enums import SensingModality


DEFAULT_DATASET_LICENSES: Dict[str, Dict[str, str]] = {
    "copernicus-s2-l2a": {
        "dataset_name": "Copernicus Sentinel-2 MSI Level-2A",
        "provider": "European Space Agency / Copernicus Programme",
        "license": "EU Copernicus Open Data Policy",
        "attribution_template": "© European Union, Copernicus Sentinel-2 data [{year}]",
        "redistribution_allowed": True,
        "commercial_use_allowed": True,
    },
    "copernicus-s1-grd": {
        "dataset_name": "Copernicus Sentinel-1 C-SAR GRD",
        "provider": "European Space Agency / Copernicus Programme",
        "license": "EU Copernicus Open Data Policy",
        "attribution_template": "© European Union, Copernicus Sentinel-1 data [{year}]",
        "redistribution_allowed": True,
        "commercial_use_allowed": True,
    },
    "usgs-landsat-c2l2": {
        "dataset_name": "USGS Landsat Collection 2 Level-2",
        "provider": "U.S. Geological Survey / NASA",
        "license": "Public Domain",
        "attribution_template": "USGS/NASA Landsat data [{year}]",
        "redistribution_allowed": True,
        "commercial_use_allowed": True,
    },
}


def get_canonical_attribution(dataset_id: str, acquisition_year: int) -> str:
    """
    Returns legal attribution text for a dataset and acquisition year.
    """
    meta = DEFAULT_DATASET_LICENSES.get(dataset_id)
    if meta:
        return meta["attribution_template"].format(year=acquisition_year)
    return f"Earth Observation Data [{acquisition_year}]"


def get_dataset_license_info(dataset_id: str) -> Dict[str, Any]:
    """
    Returns licensing and attribution metadata dictionary for a dataset ID.
    """
    return DEFAULT_DATASET_LICENSES.get(dataset_id, {
        "dataset_name": "Open Earth Observation Data",
        "provider": "Public STAC Catalog",
        "license": "Open Data",
        "attribution_template": "Earth Observation Data [{year}]",
        "redistribution_allowed": True,
        "commercial_use_allowed": True,
    })
