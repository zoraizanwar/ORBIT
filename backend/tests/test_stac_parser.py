from datetime import datetime, timezone
import pytest
from app.models.enums import SensingModality, EpistemicLevel
from app.services.eo.stac.parser import (
    parse_stac_item,
    sanitize_stac_geometry,
    parse_cloud_coverage,
)
from app.services.eo.stac.exceptions import STACGeometryError, STACMetadataValidationError


def test_parse_sentinel_2_item():
    mock_s2 = {
        "type": "Feature",
        "stac_version": "1.0.0",
        "id": "S2B_MSIL2A_20260718T140059_N0510_R067_T21LTC_20260718T181234",
        "collection": "sentinel-2-l2a",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-55.4, -12.1],
                    [-54.1, -12.1],
                    [-54.1, -10.9],
                    [-55.4, -10.9],
                    [-55.4, -12.1],
                ]
            ],
        },
        "bbox": [-55.4, -12.1, -54.1, -10.9],
        "properties": {
            "datetime": "2026-07-18T14:00:59Z",
            "platform": "Sentinel-2B",
            "instruments": ["MSI"],
            "eo:cloud_cover": 14.8,
            "processing_level": "Level-2A",
            "gsd": 10.0,
        },
        "assets": {
            "B02": {
                "href": "https://sentinel-cogs.s3.amazonaws.com/sentinel-s2-l2a-cogs/21/L/TC/2026/7/S2B_21LTC_20260718_0_L2A/B02.tif",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                "roles": ["data", "reflectance"],
                "title": "Band 2 - Blue - 10m",
                "eo:bands": [{"name": "B02", "common_name": "blue", "center_wavelength": 0.490}],
            },
            "B04": {
                "href": "https://sentinel-cogs.s3.amazonaws.com/sentinel-s2-l2a-cogs/21/L/TC/2026/7/S2B_21LTC_20260718_0_L2A/B04.tif",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                "roles": ["data", "reflectance"],
                "title": "Band 4 - Red - 10m",
                "eo:bands": [{"name": "B04", "common_name": "red", "center_wavelength": 0.665}],
            },
            "B08": {
                "href": "https://sentinel-cogs.s3.amazonaws.com/sentinel-s2-l2a-cogs/21/L/TC/2026/7/S2B_21LTC_20260718_0_L2A/B08.tif",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                "roles": ["data", "reflectance"],
                "title": "Band 8 - NIR - 10m",
                "eo:bands": [{"name": "B08", "common_name": "nir", "center_wavelength": 0.842}],
            },
            "thumbnail": {
                "href": "https://sentinel-cogs.s3.amazonaws.com/sentinel-s2-l2a-cogs/21/L/TC/2026/7/S2B_21LTC_20260718_0_L2A/thumbnail.jpg",
                "type": "image/jpeg",
                "roles": ["thumbnail"],
            },
        },
    }

    scene = parse_stac_item(mock_s2, provider_name="Element84 Earth Search")
    assert scene.item_id == "S2B_MSIL2A_20260718T140059_N0510_R067_T21LTC_20260718T181234"
    assert scene.platform == "Sentinel-2B"
    assert scene.sensor == "MSI"
    assert scene.modality == SensingModality.OPTICAL
    assert scene.dataset_id == "copernicus-s2-l2a"
    assert scene.cloud_cover == 14.8
    assert scene.spatial_resolution == 10.0
    assert "B02" in scene.assets
    assert "B08" in scene.assets
    assert scene.assets["B02"].is_cloud_optimized is True
    assert scene.thumbnail_url is not None
    assert "Copernicus Sentinel-2" in scene.attribution
    assert scene.epistemic_level == EpistemicLevel.OBSERVED


def test_parse_sentinel_1_item():
    mock_s1 = {
        "type": "Feature",
        "stac_version": "1.0.0",
        "id": "S1A_IW_GRDH_1SDV_20260715T214530_20260715T214555_054620_06A7C8_12AB",
        "collection": "sentinel-1-grd",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-55.2, -12.0],
                    [-54.0, -12.0],
                    [-54.0, -11.0],
                    [-55.2, -11.0],
                    [-55.2, -12.0],
                ]
            ],
        },
        "bbox": [-55.2, -12.0, -54.0, -11.0],
        "properties": {
            "datetime": "2026-07-15T21:45:30Z",
            "platform": "Sentinel-1A",
            "instruments": ["C-SAR"],
            "sar:instrument_mode": "IW",
            "sar:polarizations": ["VV", "VH"],
            "sar:product_type": "GRD",
            "sar:resolution_range": 10.0,
        },
        "assets": {
            "vv": {
                "href": "https://sentinel-1.s3.amazonaws.com/GRD/2026/7/15/IW/DV/S1A_.../measurement/vv.tiff",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                "roles": ["data"],
                "title": "VV Polarization",
            },
            "vh": {
                "href": "https://sentinel-1.s3.amazonaws.com/GRD/2026/7/15/IW/DV/S1A_.../measurement/vh.tiff",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                "roles": ["data"],
                "title": "VH Polarization",
            },
        },
    }

    scene = parse_stac_item(mock_s1, provider_name="Copernicus CDSE")
    assert scene.platform == "Sentinel-1A"
    assert scene.sensor == "C-SAR"
    assert scene.modality == SensingModality.SAR
    assert scene.dataset_id == "copernicus-s1-grd"
    # SAR has no optical cloud cover concept; must be None, NOT 0.0%
    assert scene.cloud_cover is None
    assert "Copernicus Sentinel-1" in scene.attribution


def test_missing_cloud_cover_preservation():
    props_no_cloud = {"datetime": "2026-06-01T12:00:00Z", "platform": "Satellite"}
    assert parse_cloud_coverage(props_no_cloud) is None


def test_sanitize_geometry_and_repair():
    # Valid polygon
    valid_poly = {
        "type": "Polygon",
        "coordinates": [
            [[-55.0, -12.0], [-54.0, -12.0], [-54.0, -11.0], [-55.0, -11.0], [-55.0, -12.0]]
        ],
    }
    geom, bbox, repaired = sanitize_stac_geometry(valid_poly)
    assert not repaired
    assert bbox == [-55.0, -12.0, -54.0, -11.0]

    # Bowtie self-intersecting polygon (should be deterministically repaired)
    bowtie = {
        "type": "Polygon",
        "coordinates": [
            [[-55.0, -12.0], [-54.0, -11.0], [-54.0, -12.0], [-55.0, -11.0], [-55.0, -12.0]]
        ],
    }
    geom_rep, bbox_rep, repaired_flag = sanitize_stac_geometry(bowtie)
    assert repaired_flag is True

    # Out of bounds geometry
    out_of_bounds = {
        "type": "Polygon",
        "coordinates": [
            [[-195.0, -12.0], [-54.0, -12.0], [-54.0, -11.0], [-195.0, -11.0], [-195.0, -12.0]]
        ],
    }
    with pytest.raises(STACGeometryError):
        sanitize_stac_geometry(out_of_bounds)
