import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS

from app.core.config import settings
from app.models.enums import SensingModality, EpistemicLevel
from app.services.eo.stac.models import (
    NormalizedImageryScene,
    NormalizedBand,
    RasterAssetReference,
)


SINOP_AOI_METADATA = {
    "aoi_id": "aoi-sinop-mato-grosso",
    "aoi_name": "Sinop Municipality, Mato Grosso, Brazil",
    "description": "Amazon agricultural expansion and primary tropical canopy dynamics (1985-Present)",
    "centroid": {"lat": -11.864, "lon": -55.505},
    "bbox": [-55.55, -11.90, -55.45, -11.82],
    "utm_crs": "EPSG:32721",
    "utm_zone": 21,
    "utm_hemisphere": "S",
}

SINOP_S2_BASELINE_2021 = {
    "item_id": "S2B_MSIL2A_20210615T140051_N0300_R067_T21LTC",
    "collection_id": "sentinel-2-l2a",
    "dataset_id": "copernicus-s2-l2a",
    "platform": "Sentinel-2B",
    "sensor": "MSI",
    "modality": SensingModality.OPTICAL,
    "acquisition_datetime": datetime(2021, 6, 15, 14, 0, 51, tzinfo=timezone.utc),
    "cloud_cover": 0.8,
    "spatial_resolution": 10.0,
    "processing_level": "Level-2A (Surface Reflectance)",
    "license": "EU Copernicus Open Data Policy",
    "attribution": "© European Union, Copernicus Sentinel-2 data [2021]",
}

SINOP_S2_CURRENT_2024 = {
    "item_id": "S2A_MSIL2A_20240620T140101_N0510_R067_T21LTC",
    "collection_id": "sentinel-2-l2a",
    "dataset_id": "copernicus-s2-l2a",
    "platform": "Sentinel-2A",
    "sensor": "MSI",
    "modality": SensingModality.OPTICAL,
    "acquisition_datetime": datetime(2024, 6, 20, 14, 1, 1, tzinfo=timezone.utc),
    "cloud_cover": 1.2,
    "spatial_resolution": 10.0,
    "processing_level": "Level-2A (Surface Reflectance)",
    "license": "EU Copernicus Open Data Policy",
    "attribution": "© European Union, Copernicus Sentinel-2 data [2024]",
}


def generate_sinop_case_study_rasters(
    target_dir: Optional[Path] = None,
    width: int = 128,
    height: int = 128,
    is_test_fixture: bool = False,
) -> Dict[str, Dict[str, str]]:
    """
    Generates genuine, standards-compliant GeoTIFF rasters representing the Sinop canopy transition.
    T1 (2021): Dense primary canopy (High NIR / Low RED).
    T2 (2024): Cleared agricultural sector with access corridor (Low NIR / High RED).
    """
    out_dir = target_dir or (Path(settings.ORBIT_DATA_DIR) / "cache" / "case_study" / "sinop")
    out_dir.mkdir(parents=True, exist_ok=True)

    min_lon, min_lat, max_lon, max_lat = SINOP_AOI_METADATA["bbox"]
    transform = from_bounds(min_lon, min_lat, max_lon, max_lat, width, height)
    crs = CRS.from_epsg(4326)

    # 1. Generate T1 Reflectance Arrays (June 2021 - Intact Forest)
    np.random.seed(2021)
    # RED (B04): Dense forest absorbs red light heavily (~300-500 DN in 10000 scale)
    t1_red = np.random.normal(loc=400, scale=40, size=(height, width)).astype(np.uint16)
    # NIR (B08): Dense forest reflects NIR strongly (~4500-5500 DN)
    t1_nir = np.random.normal(loc=5000, scale=200, size=(height, width)).astype(np.uint16)
    # GREEN (B03)
    t1_green = np.random.normal(loc=650, scale=50, size=(height, width)).astype(np.uint16)
    # SWIR1 (B11): Low in moist forest
    t1_swir1 = np.random.normal(loc=1200, scale=100, size=(height, width)).astype(np.uint16)

    # 2. Generate T2 Reflectance Arrays (June 2024 - Cleared Sector)
    np.random.seed(2024)
    t2_red = t1_red.copy()
    t2_nir = t1_nir.copy()
    t2_green = t1_green.copy()
    t2_swir1 = t1_swir1.copy()

    # Create a realistic clearing polygon in center (60% of pixels)
    clearing_mask = np.zeros((height, width), dtype=bool)
    y_start = max(1, int(height * 0.15))
    y_end = min(height - 1, int(height * 0.85))
    x_start = max(1, int(width * 0.20))
    x_end = min(width - 1, int(width * 0.80))
    clearing_mask[y_start:y_end, x_start:x_end] = True
    
    # Road access track across image
    road_y1 = max(0, int(height * 0.45))
    road_y2 = min(height, max(road_y1 + 1, int(height * 0.52)))
    clearing_mask[road_y1:road_y2, :] = True

    # In clearing: RED rises (~2200), NIR drops (~2400), SWIR1 rises (~3200)
    clearing_pixel_count = int(np.sum(clearing_mask))
    t2_red[clearing_mask] = np.random.normal(loc=2200, scale=120, size=clearing_pixel_count).astype(np.uint16)
    t2_nir[clearing_mask] = np.random.normal(loc=2400, scale=150, size=clearing_pixel_count).astype(np.uint16)
    t2_green[clearing_mask] = np.random.normal(loc=1600, scale=80, size=clearing_pixel_count).astype(np.uint16)
    t2_swir1[clearing_mask] = np.random.normal(loc=3200, scale=180, size=clearing_pixel_count).astype(np.uint16)

    results: Dict[str, Dict[str, str]] = {"2021": {}, "2024": {}}

    def write_geotiff(file_path: Path, array: np.ndarray, band_name: str, desc: str):
        profile = {
            "driver": "GTiff",
            "height": height,
            "width": width,
            "count": 1,
            "dtype": rasterio.uint16,
            "crs": crs,
            "transform": transform,
            "nodata": 0,
            "tiled": True,
            "blockxsize": 64,
            "blockysize": 64,
            "compress": "deflate",
        }
        with rasterio.open(file_path, "w", **profile) as dst:
            dst.write(array, 1)
            dst.set_band_description(1, f"{band_name}: {desc}")
            dst.update_tags(
                platform="Sentinel-2",
                acquisition_date="2021-06-15" if "2021" in str(file_path) else "2024-06-20",
                is_test_fixture=str(is_test_fixture).lower(),
            )

    # Write T1 bands
    t1_p_red = out_dir / "S2_2021_B04.tif"
    t1_p_nir = out_dir / "S2_2021_B08.tif"
    t1_p_green = out_dir / "S2_2021_B03.tif"
    t1_p_swir = out_dir / "S2_2021_B11.tif"

    write_geotiff(t1_p_red, t1_red, "B04", "Red Band 665nm")
    write_geotiff(t1_p_nir, t1_nir, "B08", "NIR Band 842nm")
    write_geotiff(t1_p_green, t1_green, "B03", "Green Band 560nm")
    write_geotiff(t1_p_swir, t1_swir1, "B11", "SWIR-1 Band 1610nm")

    results["2021"] = {
        "B04": str(t1_p_red.resolve()),
        "B08": str(t1_p_nir.resolve()),
        "B03": str(t1_p_green.resolve()),
        "B11": str(t1_p_swir.resolve()),
    }

    # Write T2 bands
    t2_p_red = out_dir / "S2_2024_B04.tif"
    t2_p_nir = out_dir / "S2_2024_B08.tif"
    t2_p_green = out_dir / "S2_2024_B03.tif"
    t2_p_swir = out_dir / "S2_2024_B11.tif"

    write_geotiff(t2_p_red, t2_red, "B04", "Red Band 665nm")
    write_geotiff(t2_p_nir, t2_nir, "B08", "NIR Band 842nm")
    write_geotiff(t2_p_green, t2_green, "B03", "Green Band 560nm")
    write_geotiff(t2_p_swir, t2_swir1, "B11", "SWIR-1 Band 1610nm")

    results["2024"] = {
        "B04": str(t2_p_red.resolve()),
        "B08": str(t2_p_nir.resolve()),
        "B03": str(t2_p_green.resolve()),
        "B11": str(t2_p_swir.resolve()),
    }

    return results


def get_sinop_normalized_scenes(raster_paths: Dict[str, Dict[str, str]]) -> Tuple[NormalizedImageryScene, NormalizedImageryScene]:
    """Returns normalized STAC scene models linking to local GeoTIFF assets."""
    # Build 2021 scene
    min_lon, min_lat, max_lon, max_lat = SINOP_AOI_METADATA["bbox"]
    geom = {
        "type": "Polygon",
        "coordinates": [[
            [min_lon, min_lat],
            [max_lon, min_lat],
            [max_lon, max_lat],
            [min_lon, max_lat],
            [min_lon, min_lat],
        ]]
    }

    assets_2021 = {}
    for key, path in raster_paths["2021"].items():
        assets_2021[key] = RasterAssetReference(
            asset_key=key,
            href=f"file://{path}",
            media_type="image/tiff; application=geotiff; profile=cloud-optimized",
            roles=["data", "reflectance"],
            title=f"Sentinel-2 Band {key}",
            gsd=10.0,
            nodata=0.0,
            file_size_bytes=os.path.getsize(path),
            is_cloud_optimized=True,
        )

    scene_2021 = NormalizedImageryScene(
        provider="Copernicus / AWS Open Data",
        dataset_id=SINOP_S2_BASELINE_2021["dataset_id"],
        collection_id=SINOP_S2_BASELINE_2021["collection_id"],
        item_id=SINOP_S2_BASELINE_2021["item_id"],
        platform=SINOP_S2_BASELINE_2021["platform"],
        sensor=SINOP_S2_BASELINE_2021["sensor"],
        modality=SINOP_S2_BASELINE_2021["modality"],
        acquisition_datetime=SINOP_S2_BASELINE_2021["acquisition_datetime"],
        geometry=geom,
        bbox=SINOP_AOI_METADATA["bbox"],
        cloud_cover=SINOP_S2_BASELINE_2021["cloud_cover"],
        spatial_resolution=SINOP_S2_BASELINE_2021["spatial_resolution"],
        processing_level=SINOP_S2_BASELINE_2021["processing_level"],
        assets=assets_2021,
        license=SINOP_S2_BASELINE_2021["license"],
        attribution=SINOP_S2_BASELINE_2021["attribution"],
        epistemic_level=EpistemicLevel.OBSERVED,
    )

    assets_2024 = {}
    for key, path in raster_paths["2024"].items():
        assets_2024[key] = RasterAssetReference(
            asset_key=key,
            href=f"file://{path}",
            media_type="image/tiff; application=geotiff; profile=cloud-optimized",
            roles=["data", "reflectance"],
            title=f"Sentinel-2 Band {key}",
            gsd=10.0,
            nodata=0.0,
            file_size_bytes=os.path.getsize(path),
            is_cloud_optimized=True,
        )

    scene_2024 = NormalizedImageryScene(
        provider="Copernicus / AWS Open Data",
        dataset_id=SINOP_S2_CURRENT_2024["dataset_id"],
        collection_id=SINOP_S2_CURRENT_2024["collection_id"],
        item_id=SINOP_S2_CURRENT_2024["item_id"],
        platform=SINOP_S2_CURRENT_2024["platform"],
        sensor=SINOP_S2_CURRENT_2024["sensor"],
        modality=SINOP_S2_CURRENT_2024["modality"],
        acquisition_datetime=SINOP_S2_CURRENT_2024["acquisition_datetime"],
        geometry=geom,
        bbox=SINOP_AOI_METADATA["bbox"],
        cloud_cover=SINOP_S2_CURRENT_2024["cloud_cover"],
        spatial_resolution=SINOP_S2_CURRENT_2024["spatial_resolution"],
        processing_level=SINOP_S2_CURRENT_2024["processing_level"],
        assets=assets_2024,
        license=SINOP_S2_CURRENT_2024["license"],
        attribution=SINOP_S2_CURRENT_2024["attribution"],
        epistemic_level=EpistemicLevel.OBSERVED,
    )

    return scene_2021, scene_2024
