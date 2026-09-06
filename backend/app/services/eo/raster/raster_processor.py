from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import numpy as np
from pydantic import BaseModel, Field

from app.models.enums import EpistemicLevel
from app.services.eo.raster.band_resolver import (
    CanonicalBand,
    resolve_asset_key_for_band,
)
from app.services.eo.raster.raster_exceptions import (
    BandNotFoundError,
    InvalidAOIError,
    RasterError,
)
from app.services.eo.raster.raster_metadata import RasterMetadata, RasterWindowBounds
from app.services.eo.raster.raster_reader import RasterReader
from app.services.eo.raster.raster_statistics import (
    compute_raster_statistics,
    RasterDistributionStatistics,
)
from app.services.eo.raster.raster_window import calculate_aoi_raster_window
from app.services.eo.raster.spectral_indices import SpectralIndexEngine
from app.services.eo.raster.vegetation_intelligence import (
    analyze_vegetation_canopy,
    VegetationIntelligenceSummary,
)
from app.services.eo.raster.water_intelligence import (
    analyze_water_coverage,
    WaterIntelligenceSummary,
)
from app.services.eo.raster.urban_intelligence import (
    analyze_built_up_coverage,
    UrbanIntelligenceSummary,
)


class IndexCalculationRequest(BaseModel):
    scene_id: str
    platform: str = "Sentinel-2B"
    sensor: str = "MSI"
    index_type: str = Field(..., description="NDVI, NDWI, NDBI, or SAVI")
    aoi_geometry: Dict[str, Any] = Field(..., description="GeoJSON Polygon/MultiPolygon in EPSG:4326")
    asset_urls: Dict[str, str] = Field(..., description="Mapping of asset keys to file paths or HTTP COG URLs")
    custom_thresholds: Optional[Dict[str, float]] = None


class IndexCalculationResult(BaseModel):
    index_name: str
    formula: str
    scene_id: str
    platform: str
    sensor: str
    acquisition_datetime: Optional[str] = None
    aoi_bounds_wgs84: List[float]
    window_dimensions: List[int]
    statistics: RasterDistributionStatistics
    vegetation_summary: Optional[VegetationIntelligenceSummary] = None
    water_summary: Optional[WaterIntelligenceSummary] = None
    urban_summary: Optional[UrbanIntelligenceSummary] = None
    provenance: Dict[str, Any]
    epistemic_level: EpistemicLevel = EpistemicLevel.CALCULATED
    calculated_at: str


class RasterProcessor:
    """
    High-level orchestrator for reading, windowing, calculating spectral indices, and deriving spatial statistics.
    """

    @classmethod
    def process_index(
        cls,
        request: IndexCalculationRequest,
        acquisition_datetime: Optional[datetime] = None,
    ) -> IndexCalculationResult:
        idx_upper = request.index_type.upper()
        available_keys = list(request.asset_urls.keys())

        # 1. Resolve Required Bands
        if idx_upper == "NDVI":
            nir_key = resolve_asset_key_for_band(CanonicalBand.NIR, available_keys, request.platform)
            red_key = resolve_asset_key_for_band(CanonicalBand.RED, available_keys, request.platform)
            bands_needed = {"nir": nir_key, "red": red_key}
            formula = "NDVI = (NIR - RED) / (NIR + RED)"
        elif idx_upper == "NDWI":
            green_key = resolve_asset_key_for_band(CanonicalBand.GREEN, available_keys, request.platform)
            nir_key = resolve_asset_key_for_band(CanonicalBand.NIR, available_keys, request.platform)
            bands_needed = {"green": green_key, "nir": nir_key}
            formula = "NDWI = (GREEN - NIR) / (GREEN + NIR) [McFeeters 1996]"
        elif idx_upper == "NDBI":
            swir_key = resolve_asset_key_for_band(CanonicalBand.SWIR_1, available_keys, request.platform)
            nir_key = resolve_asset_key_for_band(CanonicalBand.NIR, available_keys, request.platform)
            bands_needed = {"swir": swir_key, "nir": nir_key}
            formula = "NDBI = (SWIR - NIR) / (SWIR + NIR) [Zha et al. 2003]"
        elif idx_upper == "SAVI":
            nir_key = resolve_asset_key_for_band(CanonicalBand.NIR, available_keys, request.platform)
            red_key = resolve_asset_key_for_band(CanonicalBand.RED, available_keys, request.platform)
            bands_needed = {"nir": nir_key, "red": red_key}
            formula = "SAVI = ((NIR - RED) / (NIR + RED + 0.5)) * 1.5 [Huete 1988]"
        else:
            raise RasterError(f"Unsupported spectral index: {request.index_type}")

        # 2. Inspect First Band Metadata for Window Extraction
        primary_key = list(bands_needed.values())[0]
        primary_uri = request.asset_urls[primary_key]
        meta = RasterReader.inspect_metadata(primary_uri)

        # 3. Calculate AOI Window
        import rasterio
        trans_obj = rasterio.Affine(*meta.transform)
        window, win_trans, win_bounds = calculate_aoi_raster_window(
            aoi_geometry=request.aoi_geometry,
            raster_crs_str=meta.crs,
            raster_transform=trans_obj,
            raster_width=meta.width,
            raster_height=meta.height,
        )

        # Extract Center Latitude for WGS84 Geodesic Scaling
        center_lat = (win_bounds.bounds_wgs84[1] + win_bounds.bounds_wgs84[3]) / 2.0 if win_bounds.bounds_wgs84 else None

        # 4. Read Required Band Windows
        read_arrays: Dict[str, np.ndarray] = {}
        read_nodatas: Dict[str, Optional[float]] = {}

        for role, key in bands_needed.items():
            uri = request.asset_urls[key]
            arr, nodata_val, _ = RasterReader.read_band(uri, band_index=1, window=window)
            read_arrays[role] = arr
            read_nodatas[role] = nodata_val

        # 5. Compute Spectral Index Array
        if idx_upper == "NDVI":
            index_arr = SpectralIndexEngine.calculate_ndvi(
                nir_band=read_arrays["nir"],
                red_band=read_arrays["red"],
                nodata_nir=read_nodatas["nir"],
                nodata_red=read_nodatas["red"],
            )
            veg_summary = analyze_vegetation_canopy(
                ndvi_array=index_arr,
                pixel_res_x=meta.resolution_x,
                pixel_res_y=meta.resolution_y,
                crs_str=meta.crs,
                center_latitude=center_lat,
            )
            water_summary = None
            urban_summary = None
        elif idx_upper == "NDWI":
            index_arr = SpectralIndexEngine.calculate_ndwi(
                green_band=read_arrays["green"],
                nir_band=read_arrays["nir"],
                nodata_green=read_nodatas["green"],
                nodata_nir=read_nodatas["nir"],
            )
            veg_summary = None
            water_summary = analyze_water_coverage(
                ndwi_array=index_arr,
                pixel_res_x=meta.resolution_x,
                pixel_res_y=meta.resolution_y,
                crs_str=meta.crs,
                center_latitude=center_lat,
            )
            urban_summary = None
        elif idx_upper == "NDBI":
            index_arr = SpectralIndexEngine.calculate_ndbi(
                swir_band=read_arrays["swir"],
                nir_band=read_arrays["nir"],
                nodata_swir=read_nodatas["swir"],
                nodata_nir=read_nodatas["nir"],
            )
            veg_summary = None
            water_summary = None
            urban_summary = analyze_built_up_coverage(
                ndbi_array=index_arr,
                pixel_res_x=meta.resolution_x,
                pixel_res_y=meta.resolution_y,
                crs_str=meta.crs,
                center_latitude=center_lat,
            )
        else:  # SAVI
            index_arr = SpectralIndexEngine.calculate_savi(
                nir_band=read_arrays["nir"],
                red_band=read_arrays["red"],
                nodata_nir=read_nodatas["nir"],
                nodata_red=read_nodatas["red"],
            )
            veg_summary = None
            water_summary = None
            urban_summary = None

        # 6. Compute Spatial Distribution Statistics
        stats = compute_raster_statistics(
            data=index_arr,
            pixel_resolution_x_m=meta.resolution_x,
            pixel_resolution_y_m=meta.resolution_y,
            crs_str=meta.crs,
            center_latitude=center_lat,
        )

        now_utc = datetime.now(timezone.utc).isoformat()

        # 7. Build Provenance Record
        provenance = {
            "scene_id": request.scene_id,
            "platform": request.platform,
            "sensor": request.sensor,
            "index_type": idx_upper,
            "formula": formula,
            "bands_used": bands_needed,
            "crs": meta.crs,
            "pixel_resolution_meters": [meta.resolution_x, meta.resolution_y],
            "window_bounds_wgs84": win_bounds.bounds_wgs84,
            "area_calculation_method": stats.area_calculation_method,
            "epistemic_level": "CALCULATED",
            "software": "ORBIT Raster Processing Engine v1.0",
            "calculated_at": now_utc,
        }

        return IndexCalculationResult(
            index_name=idx_upper,
            formula=formula,
            scene_id=request.scene_id,
            platform=request.platform,
            sensor=request.sensor,
            acquisition_datetime=acquisition_datetime.isoformat() if acquisition_datetime else None,
            aoi_bounds_wgs84=win_bounds.bounds_wgs84 or [],
            window_dimensions=[win_bounds.width, win_bounds.height],
            statistics=stats,
            vegetation_summary=veg_summary,
            water_summary=water_summary,
            urban_summary=urban_summary,
            provenance=provenance,
            epistemic_level=EpistemicLevel.CALCULATED,
            calculated_at=now_utc,
        )
