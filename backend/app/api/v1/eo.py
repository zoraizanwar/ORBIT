import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.enums import EpistemicLevel, AnalysisStatus
from app.models.intelligence.measurement import Measurement
from app.models.analysis.analysis_run import AnalysisRun
from app.services.eo.stac.models import (
    STACSearchRequest,
    STACSearchResponse,
    NormalizedImageryScene,
)
from app.services.eo.stac.client import stac_client_manager
from app.services.eo.discovery.scene_discovery import (
    execute_scene_discovery,
    register_imagery_scene,
    get_registered_scene_by_id,
    list_scene_assets,
)
from app.services.eo.discovery.modality import (
    ModalitySuitabilityAssessment,
    assess_modality_suitability,
)
from app.services.eo.raster import (
    RasterReader,
    RasterMetadata,
    RasterProcessor,
    IndexCalculationRequest,
    IndexCalculationResult,
    compute_raster_statistics,
    RasterDistributionStatistics,
)
from app.services.eo.timeseries import (
    TimePointMeasurement,
    TemporalMeasurementSeries,
    build_temporal_series,
)
from app.services.eo.stac.real_discovery import (
    DeterministicSceneRanker,
    RankedImageryScene,
    SceneRankingCriteria,
)
from app.services.eo.acquisition.secure_downloader import (
    SecureAssetAcquisitionService,
    AssetAcquisitionRequest,
    AcquiredAssetRecord,
)
from app.services.eo.raster.real_raster_validator import (
    RealRasterValidator,
    RasterValidationReport,
)
from app.services.eo.real_pipeline import RealDataPipelineOrchestrator
from app.services.eo.case_study_data import (
    SINOP_AOI_METADATA,
    SINOP_S2_BASELINE_2021,
    SINOP_S2_CURRENT_2024,
    generate_sinop_case_study_rasters,
    get_sinop_normalized_scenes,
)

router = APIRouter(prefix="/eo", tags=["Earth Observation & Raster Intelligence"])


# =============================================================================
# 1. STAC Discovery & Providers
# =============================================================================

@router.get(
    "/providers",
    summary="List STAC Providers",
    description="Returns metadata for all configured Earth Observation STAC providers.",
)
async def list_providers() -> List[Dict[str, Any]]:
    return stac_client_manager.list_providers()


@router.get(
    "/collections",
    summary="List STAC Collections",
    description="Returns list of supported satellite collections across open providers.",
)
async def list_collections() -> List[Dict[str, Any]]:
    return [
        {
            "id": "sentinel-2-l2a",
            "title": "Sentinel-2 MSI Level-2A (Surface Reflectance)",
            "provider": "Copernicus / AWS Open Data",
            "modality": "OPTICAL_MULTISPECTRAL",
            "spatial_resolution_meters": 10.0,
            "license": "EU Copernicus Open Data Policy",
            "attribution": "© European Union, Copernicus Sentinel-2 data",
        },
        {
            "id": "sentinel-1-grd",
            "title": "Sentinel-1 C-SAR Ground Range Detected (GRD)",
            "provider": "Copernicus / CDSE",
            "modality": "SAR_MICROWAVE",
            "spatial_resolution_meters": 10.0,
            "license": "EU Copernicus Open Data Policy",
            "attribution": "© European Union, Copernicus Sentinel-1 data",
        },
        {
            "id": "landsat-c2-l2",
            "title": "Landsat 8/9 Collection 2 Level-2",
            "provider": "USGS / NASA",
            "modality": "OPTICAL_MULTISPECTRAL",
            "spatial_resolution_meters": 30.0,
            "license": "Public Domain",
            "attribution": "USGS/NASA Landsat data",
        },
    ]


@router.post(
    "/search",
    response_model=STACSearchResponse,
    summary="Search Satellite Imagery via STAC",
    description="Queries open STAC API catalogs for optical multispectral and SAR satellite scenes.",
)
async def search_satellite_scenes(
    request: STACSearchRequest,
) -> STACSearchResponse:
    try:
        return await execute_scene_discovery(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"STAC provider discovery failed: {str(e)}",
        ) from e


@router.post(
    "/modality-assessment",
    response_model=ModalitySuitabilityAssessment,
    summary="Assess Modality Suitability",
    description="Calculates initial suitability metrics (cloud cover, SAR availability) for candidate scenes.",
)
async def assess_modality(
    scenes: List[NormalizedImageryScene],
    target_modality_preference: Optional[str] = Query(None),
) -> ModalitySuitabilityAssessment:
    return assess_modality_suitability(scenes, target_modality_preference)


@router.post(
    "/scenes/register",
    summary="Register Discovered Scene into Local Database",
    description="Idempotently registers a normalized STAC scene and its assets into eo.imagery_scenes and eo.imagery_assets.",
)
async def register_scene(
    scene: NormalizedImageryScene,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        db_scene = await register_imagery_scene(session, scene)
        return {
            "status": "REGISTERED",
            "scene_id": str(db_scene.id),
            "provider_scene_id": db_scene.provider_scene_id,
            "platform": db_scene.platform,
            "epistemic_level": "OBSERVED",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register imagery scene: {str(e)}",
        ) from e


@router.get(
    "/scenes/{scene_id}",
    summary="Get Registered Scene Detail",
    description="Fetches registered scene metadata and GeoJSON footprint by UUID.",
)
async def get_scene(
    scene_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    scene = await get_registered_scene_by_id(session, scene_id)
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imagery scene with ID {scene_id} was not found",
        )
    return scene


@router.get(
    "/scenes/{scene_id}/assets",
    summary="List Scene Assets",
    description="Retrieves all asset references and COG metadata for a scene.",
)
async def get_scene_assets(
    scene_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    return await list_scene_assets(session, scene_id)


# =============================================================================
# 2. Raster Inspection & Spectral Processing
# =============================================================================

class RasterInspectRequest(BaseModel):
    source_uri: str = Field(..., description="Local file path or HTTP/HTTPS COG URL")


@router.post(
    "/raster/inspect",
    response_model=RasterMetadata,
    summary="Inspect Raster Header & Metadata",
    description="Reads Cloud-Optimized GeoTIFF header and returns dimensions, CRS, bounds, and transform without reading pixel payload.",
)
async def inspect_raster(request: RasterInspectRequest) -> RasterMetadata:
    try:
        return RasterReader.inspect_metadata(request.source_uri)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to inspect raster: {str(e)}",
        ) from e


@router.post(
    "/indices/ndvi",
    response_model=IndexCalculationResult,
    summary="Calculate NDVI over Scene & AOI",
    description="Computes Normalized Difference Vegetation Index: (NIR - RED) / (NIR + RED) [Epistemic: CALCULATED].",
)
async def calculate_ndvi_endpoint(request: IndexCalculationRequest) -> IndexCalculationResult:
    try:
        req = request.model_copy(update={"index_type": "NDVI"})
        return RasterProcessor.process_index(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"NDVI processing failed: {str(e)}",
        ) from e


@router.post(
    "/indices/ndwi",
    response_model=IndexCalculationResult,
    summary="Calculate NDWI over Scene & AOI",
    description="Computes Normalized Difference Water Index: (GREEN - NIR) / (GREEN + NIR) [Epistemic: CALCULATED].",
)
async def calculate_ndwi_endpoint(request: IndexCalculationRequest) -> IndexCalculationResult:
    try:
        req = request.model_copy(update={"index_type": "NDWI"})
        return RasterProcessor.process_index(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"NDWI processing failed: {str(e)}",
        ) from e


@router.post(
    "/indices/ndbi",
    response_model=IndexCalculationResult,
    summary="Calculate NDBI over Scene & AOI",
    description="Computes Normalized Difference Built-up Index: (SWIR - NIR) / (SWIR + NIR) [Epistemic: CALCULATED].",
)
async def calculate_ndbi_endpoint(request: IndexCalculationRequest) -> IndexCalculationResult:
    try:
        req = request.model_copy(update={"index_type": "NDBI"})
        return RasterProcessor.process_index(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"NDBI processing failed: {str(e)}",
        ) from e


# =============================================================================
# 3. Time Series & Measurements
# =============================================================================

class TimeSeriesRequest(BaseModel):
    aoi_id: Optional[str] = None
    aoi_name: Optional[str] = None
    measurements: List[TimePointMeasurement]


@router.post(
    "/timeseries",
    response_model=TemporalMeasurementSeries,
    summary="Assemble Temporal Measurement Series",
    description="Assembles, chronologically orders, and evaluates temporal observation continuity for an AOI.",
)
async def assemble_timeseries(request: TimeSeriesRequest) -> TemporalMeasurementSeries:
    return build_temporal_series(
        measurements=request.measurements,
        aoi_id=request.aoi_id,
        aoi_name=request.aoi_name,
    )


class CreateMeasurementPayload(BaseModel):
    analysis_run_id: uuid.UUID
    measurement_type: str
    value: float
    unit: str
    uncertainty: Optional[float] = None
    methodology: str
    source: str
    epistemic_level: EpistemicLevel = EpistemicLevel.CALCULATED


@router.post(
    "/measurements",
    summary="Persist Deterministic Measurement",
    description="Stores a scientifically traceable deterministic measurement in intelligence.measurements.",
)
async def save_measurement(
    payload: CreateMeasurementPayload,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        m = Measurement(
            analysis_run_id=payload.analysis_run_id,
            measurement_type=payload.measurement_type,
            value=payload.value,
            unit=payload.unit,
            uncertainty=payload.uncertainty,
            epistemic_level=payload.epistemic_level,
            methodology=payload.methodology,
            source=payload.source,
        )
        session.add(m)
        await session.commit()
        await session.refresh(m)
        return {
            "status": "SAVED",
            "measurement_id": str(m.id),
            "measurement_type": m.measurement_type,
            "value": m.value,
            "unit": m.unit,
            "epistemic_level": m.epistemic_level.value,
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist measurement: {str(e)}",
        ) from e


@router.get(
    "/measurements/{measurement_id}",
    summary="Get Measurement by ID",
    description="Retrieves measurement record from intelligence.measurements.",
)
async def get_measurement(
    measurement_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    res = await session.execute(select(Measurement).where(Measurement.id == measurement_id))
    m = res.scalar_one_or_none()
    if not m:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Measurement {measurement_id} not found",
        )
    return {
        "id": str(m.id),
        "analysis_run_id": str(m.analysis_run_id),
        "measurement_type": m.measurement_type,
        "value": m.value,
        "unit": m.unit,
        "uncertainty": m.uncertainty,
        "epistemic_level": m.epistemic_level.value,
        "methodology": m.methodology,
        "source": m.source,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


@router.get(
    "/analysis/{analysis_id}",
    summary="Get Analysis Run Status & Measurements",
    description="Retrieves analysis run execution status and associated deterministic measurements.",
)
async def get_analysis_run(
    analysis_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    res = await session.execute(select(AnalysisRun).where(AnalysisRun.id == analysis_id))
    run = res.scalar_one_or_none()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis run {analysis_id} not found",
        )
    return {
        "id": str(run.id),
        "project_id": str(run.project_id),
        "area_of_interest_id": str(run.area_of_interest_id),
        "status": run.status.value,
        "analysis_type": run.analysis_type,
        "start_date": run.start_date.isoformat(),
        "end_date": run.end_date.isoformat(),
        "parameters": run.parameters,
        "pipeline_version": run.pipeline_version,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "error_message": run.error_message,
        "created_at": run.created_at.isoformat() if run.created_at else None,
    }


@router.get(
    "/health",
    summary="Check STAC & Raster Engine Health",
    description="Returns health status of configured STAC provider endpoints and raster processing engine.",
)
async def stac_health_check() -> Dict[str, Any]:
    providers = stac_client_manager.list_providers()
    health_results = {}
    for p_info in providers:
        p = stac_client_manager.get_provider(p_info["key"])
        if p:
            is_healthy = await p.health_check()
            health_results[p_info["key"]] = "HEALTHY" if is_healthy else "UNREACHABLE"
    return {
        "status": "OPERATIONAL",
        "providers": health_results,
        "raster_engine": "READY",
    }


# =============================================================================
# 4. Phase 15: Operational Real-World Data & Pipeline Endpoints
# =============================================================================

class RankedSearchRequest(STACSearchRequest):
    target_datetime: Optional[datetime] = None
    criteria: Optional[SceneRankingCriteria] = None


class RankedSearchResponse(BaseModel):
    query: STACSearchRequest
    total_matched: int
    ranked_scenes: List[RankedImageryScene]
    providers_contacted: List[str]
    attribution_summary: List[str]


@router.post(
    "/discovery/search",
    response_model=RankedSearchResponse,
    summary="Ranked STAC Satellite Scene Discovery",
    description="Performs deterministic multi-criteria ranking across discovered STAC satellite scenes.",
)
async def search_and_rank_scenes(
    request: RankedSearchRequest,
) -> RankedSearchResponse:
    try:
        search_resp = await execute_scene_discovery(request)
        ranked = DeterministicSceneRanker.rank_scenes(
            scenes=search_resp.scenes,
            target_datetime=request.target_datetime,
            aoi_bbox=request.bbox,
            criteria=request.criteria,
        )
        return RankedSearchResponse(
            query=search_resp.query,
            total_matched=search_resp.total_matched,
            ranked_scenes=ranked,
            providers_contacted=search_resp.providers_contacted,
            attribution_summary=search_resp.attribution_summary,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"STAC ranked search failed: {str(e)}",
        ) from e


@router.post(
    "/assets/acquire",
    response_model=AcquiredAssetRecord,
    summary="Securely Acquire & Cache Remote Asset",
    description="Downloads and securely stores an Earth Observation raster asset into local cache with SSRF protection, size caps, and SHA-256 digest computation.",
)
async def acquire_asset_endpoint(
    request: AssetAcquisitionRequest,
) -> AcquiredAssetRecord:
    try:
        return await SecureAssetAcquisitionService.acquire_asset(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Asset acquisition failed: {str(e)}",
        ) from e


@router.post(
    "/assets/validate",
    response_model=RasterValidationReport,
    summary="Validate Real Raster Integrity & Bounds",
    description="Pre-analytical validation of GeoTIFF/COG header, CRS, transform, resolution, dimension limits, and checksum.",
)
async def validate_raster_endpoint(
    source_uri: str = Query(..., description="Local file URI or absolute path"),
    expected_sha256: Optional[str] = Query(None),
) -> RasterValidationReport:
    try:
        return RealRasterValidator.validate_raster(source_uri, expected_sha256)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Raster validation failed: {str(e)}",
        ) from e


class RealPipelineRunRequest(BaseModel):
    aoi_id: str
    aoi_name: str
    aoi_geometry: Dict[str, Any]
    t1_scene_id: str
    t1_band_paths: Dict[str, str]
    t1_datetime: datetime
    t2_scene_id: str
    t2_band_paths: Dict[str, str]
    t2_datetime: datetime
    platform: str = "Sentinel-2"
    sensor: str = "MSI"
    nearby_road_distance_m: Optional[float] = 85.0
    is_test_fixture: bool = False


@router.post(
    "/real-analysis/run",
    summary="Execute Full End-to-End Operational Pipeline",
    description="Executes all 8 tiers on real/calibrated Earth Observation datasets with strict epistemic segregation.",
)
async def run_real_analysis_pipeline(
    request: RealPipelineRunRequest,
) -> Dict[str, Any]:
    try:
        return await RealDataPipelineOrchestrator.run_operational_pipeline(
            aoi_id=request.aoi_id,
            aoi_name=request.aoi_name,
            aoi_geometry=request.aoi_geometry,
            t1_scene_id=request.t1_scene_id,
            t1_band_paths=request.t1_band_paths,
            t1_datetime=request.t1_datetime,
            t2_scene_id=request.t2_scene_id,
            t2_band_paths=request.t2_band_paths,
            t2_datetime=request.t2_datetime,
            platform=request.platform,
            sensor=request.sensor,
            nearby_road_distance_m=request.nearby_road_distance_m,
            is_test_fixture=request.is_test_fixture,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Operational pipeline execution failed: {str(e)}",
        ) from e


@router.get(
    "/case-study/sinop",
    summary="Get Sinop Case Study Metadata & Scenes",
    description="Returns authentic operational metadata, Sentinel-2 L2A scene references, and baseline information for the Sinop, Mato Grosso deforestation case study.",
)
async def get_sinop_case_study() -> Dict[str, Any]:
    return {
        "aoi": SINOP_AOI_METADATA,
        "baseline_2021": SINOP_S2_BASELINE_2021,
        "current_2024": SINOP_S2_CURRENT_2024,
        "is_test_fixture": False,
        "epistemic_level": "OBSERVED",
    }

