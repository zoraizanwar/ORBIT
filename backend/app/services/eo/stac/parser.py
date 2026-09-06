from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from shapely.geometry import shape, mapping
from shapely.validation import make_valid

from app.models.enums import SensingModality, EpistemicLevel
from app.services.eo.stac.exceptions import (
    STACInvalidResponseError,
    STACGeometryError,
    STACMetadataValidationError,
)
from app.services.eo.stac.models import (
    NormalizedImageryScene,
    NormalizedBand,
    RasterAssetReference,
)


def sanitize_stac_geometry(raw_geom: Optional[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[float], bool]:
    """
    Validates and deterministically repairs GeoJSON footprint geometry in EPSG:4326.
    Returns (sanitized_geojson, bbox, repaired_flag).
    """
    if not raw_geom or not isinstance(raw_geom, dict):
        raise STACGeometryError("STAC item is missing a valid geometry object")

    geom_type = raw_geom.get("type")
    if geom_type not in ["Polygon", "MultiPolygon"]:
        raise STACGeometryError(f"Unsupported STAC scene geometry type: {geom_type}. Expected Polygon/MultiPolygon.")

    try:
        shp = shape(raw_geom)
    except Exception as e:
        raise STACGeometryError(f"Failed to parse STAC geometry: {str(e)}") from e

    # Bounds check
    min_lng, min_lat, max_lng, max_lat = shp.bounds
    if not (-180.01 <= min_lng <= 180.01 and -180.01 <= max_lng <= 180.01):
        raise STACGeometryError(f"Longitude bounds out of range: [{min_lng}, {max_lng}]")
    if not (-90.01 <= min_lat <= 90.01 and -90.01 <= max_lat <= 90.01):
        raise STACGeometryError(f"Latitude bounds out of range: [{min_lat}, {max_lat}]")

    repaired = False
    if not shp.is_valid:
        shp = make_valid(shp)
        repaired = True
        if not shp.is_valid:
            raise STACGeometryError("Irreparable topological geometry in STAC item")

    # If make_valid produced GeometryCollection, extract the polygon components
    if shp.geom_type == "GeometryCollection":
        polys = [g for g in shp.geoms if g.geom_type in ["Polygon", "MultiPolygon"]]
        if not polys:
            raise STACGeometryError("Geometry repair resulted in non-polygon components")
        shp = polys[0]
        repaired = True

    bbox = [round(min_lng, 6), round(min_lat, 6), round(max_lng, 6), round(max_lat, 6)]
    return (mapping(shp), bbox, repaired)


def parse_cloud_coverage(props: Dict[str, Any]) -> Optional[float]:
    """
    Extracts cloud cover percentage (0.0 - 100.0) without inferring 0.0% when null/missing.
    """
    candidates = [
        props.get("eo:cloud_cover"),
        props.get("cloud_cover"),
        props.get("s2:cloud_cover"),
        props.get("cloudCover"),
    ]
    for val in candidates:
        if val is not None:
            try:
                num = float(val)
                return max(0.0, min(100.0, round(num, 2)))
            except (ValueError, TypeError):
                pass
    return None


def parse_acquisition_datetime(props: Dict[str, Any]) -> datetime:
    """
    Extracts ISO 8601 acquisition timestamp.
    """
    candidates = [
        props.get("datetime"),
        props.get("start_datetime"),
        props.get("acquisition_date"),
    ]
    for val in candidates:
        if val:
            try:
                # Handle standard Z or offset formats
                clean_str = val.replace("Z", "+00:00")
                return datetime.fromisoformat(clean_str)
            except Exception:
                pass
    raise STACMetadataValidationError("STAC item properties missing valid 'datetime' or 'start_datetime'")


def parse_stac_item(
    item_dict: Dict[str, Any],
    provider_name: str,
    default_dataset_id: Optional[str] = None,
) -> NormalizedImageryScene:
    """
    Parses and normalizes a raw STAC 1.0 item into ORBIT canonical NormalizedImageryScene.
    """
    if not isinstance(item_dict, dict) or item_dict.get("type") != "Feature":
        raise STACInvalidResponseError("Invalid STAC Item: expected GeoJSON Feature object")

    item_id = str(item_dict.get("id"))
    if not item_id:
        raise STACMetadataValidationError("STAC Item is missing 'id'")

    collection_id = str(item_dict.get("collection") or "default-collection")
    props = item_dict.get("properties", {})
    raw_assets = item_dict.get("assets", {})

    # 1. Parse Geometry and Bounding Box
    sanitized_geom, bbox, repaired = sanitize_stac_geometry(item_dict.get("geometry"))

    # 2. Parse Acquisition Timestamp
    acq_dt = parse_acquisition_datetime(props)
    year = acq_dt.year

    # 3. Detect Platform, Sensor & Modality
    platform_raw = str(props.get("platform") or props.get("constellation") or "Satellite").strip()
    sensor_raw = str(props.get("instruments", [props.get("instrument", "Sensor")])[0]).strip()

    # Determine Modality & Dataset ID mapping
    platform_lower = platform_raw.lower()
    item_id_lower = item_id.lower()
    collection_lower = collection_id.lower()

    if "sentinel-1" in platform_lower or "s1" in item_id_lower or "sentinel-1" in collection_lower:
        platform = "Sentinel-1A" if "s1a" in item_id_lower else "Sentinel-1B" if "s1b" in item_id_lower else "Sentinel-1"
        sensor = "C-SAR"
        modality = SensingModality.SAR
        dataset_id = "copernicus-s1-grd"
        processing_level = props.get("sar:product_type") or props.get("processing_level") or "GRD"
        spatial_res = float(props.get("sar:resolution_range") or props.get("gsd") or 10.0)
        license_name = "EU Copernicus Open Data Policy"
        attribution = f"© European Union, Copernicus Sentinel-1 data [{year}]"
        cloud_cover = None  # SAR penetrates clouds; cloud cover is undefined
    elif "sentinel-2" in platform_lower or "s2" in item_id_lower or "sentinel-2" in collection_lower:
        platform = "Sentinel-2A" if "s2a" in item_id_lower else "Sentinel-2B" if "s2b" in item_id_lower else "Sentinel-2"
        sensor = "MSI"
        modality = SensingModality.OPTICAL
        dataset_id = "copernicus-s2-l2a"
        processing_level = props.get("processing_level") or "Level-2A (Surface Reflectance)"
        spatial_res = float(props.get("gsd") or 10.0)
        license_name = "EU Copernicus Open Data Policy"
        attribution = f"© European Union, Copernicus Sentinel-2 data [{year}]"
        cloud_cover = parse_cloud_coverage(props)
    elif "landsat" in platform_lower or "landsat" in collection_lower or "lc08" in item_id_lower or "lc09" in item_id_lower:
        platform = platform_raw if "landsat" in platform_lower else "Landsat-8/9"
        sensor = sensor_raw if sensor_raw != "Sensor" else "OLI/TIRS"
        modality = SensingModality.OPTICAL
        dataset_id = "usgs-landsat-c2l2"
        processing_level = props.get("landsat:collection_category") or "Collection 2 Level-2"
        spatial_res = float(props.get("gsd") or 30.0)
        license_name = "Public Domain"
        attribution = f"USGS/NASA Landsat data [{year}]"
        cloud_cover = parse_cloud_coverage(props)
    else:
        platform = platform_raw
        sensor = sensor_raw
        modality = SensingModality.OPTICAL
        dataset_id = default_dataset_id or "open-eo-archive"
        processing_level = props.get("processing_level") or "Standard"
        spatial_res = float(props.get("gsd") or 10.0)
        license_name = props.get("license") or "Open Access"
        attribution = f"{provider_name} Satellite Observation [{year}]"
        cloud_cover = parse_cloud_coverage(props)

    # 4. Normalize Bands & Assets
    normalized_assets: Dict[str, RasterAssetReference] = {}
    normalized_bands: List[NormalizedBand] = []
    thumbnail_url: Optional[str] = None

    for asset_key, asset_val in raw_assets.items():
        if not isinstance(asset_val, dict):
            continue

        href = asset_val.get("href", "")
        roles = asset_val.get("roles", [])
        title = asset_val.get("title") or asset_key
        media_type = asset_val.get("type")
        gsd = float(asset_val.get("gsd")) if asset_val.get("gsd") else spatial_res

        # Check thumbnail
        if "thumbnail" in roles or asset_key.lower() in ["thumbnail", "preview", "rendered_preview"]:
            thumbnail_url = href

        # Extract spectral bands
        eo_bands = asset_val.get("eo:bands", [])
        band_ref = None
        if eo_bands and isinstance(eo_bands, list) and len(eo_bands) > 0:
            b_info = eo_bands[0]
            b_name = b_info.get("name") or asset_key
            common = b_info.get("common_name")
            cw = float(b_info.get("center_wavelength")) if b_info.get("center_wavelength") else None
            band_ref = NormalizedBand(
                name=b_name,
                common_name=common,
                center_wavelength_nm=cw * 1000.0 if cw and cw < 10.0 else cw,
            )
            normalized_bands.append(band_ref)
        elif modality == SensingModality.SAR and asset_key.upper() in ["VV", "VH", "HH", "HV"]:
            band_ref = NormalizedBand(
                name=asset_key.upper(),
                polarization=asset_key.upper(),
            )
            normalized_bands.append(band_ref)

        normalized_assets[asset_key] = RasterAssetReference(
            asset_key=asset_key,
            href=href,
            media_type=media_type,
            roles=roles,
            title=title,
            band=band_ref,
            gsd=gsd,
            nodata=float(asset_val.get("nodata")) if asset_val.get("nodata") is not None else None,
            file_size_bytes=int(asset_val.get("file:size")) if asset_val.get("file:size") else None,
            checksum=asset_val.get("file:checksum") or asset_val.get("checksum"),
            is_cloud_optimized="cloud-optimized" in (media_type or "") or href.endswith(".tif") or href.endswith(".tiff"),
            access_method="HTTP_RANGE",
        )

    return NormalizedImageryScene(
        provider=provider_name,
        dataset_id=dataset_id,
        collection_id=collection_id,
        item_id=item_id,
        platform=platform,
        sensor=sensor,
        modality=modality,
        acquisition_datetime=acq_dt,
        processing_datetime=None,
        geometry=sanitized_geom,
        bbox=bbox,
        cloud_cover=cloud_cover,
        spatial_resolution=spatial_res,
        processing_level=processing_level,
        bands=normalized_bands,
        assets=normalized_assets,
        thumbnail_url=thumbnail_url,
        stac_version=str(item_dict.get("stac_version") or "1.0.0"),
        license=license_name,
        attribution=attribution,
        provider_url=props.get("provider_url"),
        metadata_payload=props,
        source_checksum=None,
        epistemic_level=EpistemicLevel.OBSERVED,
        geometry_repaired=repaired,
    )
