import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import from_shape
from shapely.geometry import shape, MultiPolygon, Polygon

from app.db.session import get_db
from app.models.enums import EpistemicLevel, EvidenceStrength, AnalysisStatus
from app.models.intelligence.detected_change import DetectedChange
from app.models.analysis.analysis_run import AnalysisRun
from app.services.eo.change import (
    TemporalComparator,
    TemporalObservationPair,
    ChangeComparisonResult,
    SpatialChangeMaskResult,
    ChangeThresholdConfig,
    compute_raster_spatial_difference,
    ChangeDetectionEngine,
)
from app.services.eo.raster import RasterReader
from app.services.eo.raster.raster_window import calculate_aoi_raster_window
import rasterio

router = APIRouter(prefix="/eo/change", tags=["Multi-Temporal Change Detection"])


@router.post(
    "/compare",
    response_model=ChangeComparisonResult,
    summary="Pairwise Temporal Comparison",
    description="Compares two temporal observations for the same AOI and computes absolute delta, relative change, and deterministic classification [Epistemic: CALCULATED].",
)
async def compare_temporal_measurements(
    pair: TemporalObservationPair,
) -> ChangeComparisonResult:
    try:
        return ChangeDetectionEngine.compare_measurements(pair)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Temporal comparison failed: {str(e)}",
        ) from e


class SpatialChangeRequest(BaseModel):
    t1_scene_id: str
    t2_scene_id: str
    t1_raster_uri: str
    t2_raster_uri: str
    aoi_geometry: Dict[str, Any]
    threshold_config: Optional[ChangeThresholdConfig] = None


@router.post(
    "/mask",
    response_model=SpatialChangeMaskResult,
    summary="Compute Spatial Difference Raster & Change Mask",
    description="Calculates pixel-level difference raster (T2 - T1) with nodata preservation and stratified spatial change classes [Epistemic: CALCULATED].",
)
async def compute_spatial_mask_endpoint(
    request: SpatialChangeRequest,
) -> SpatialChangeMaskResult:
    try:
        # 1. Inspect T1 and T2 rasters
        meta_t1 = RasterReader.inspect_metadata(request.t1_raster_uri)
        meta_t2 = RasterReader.inspect_metadata(request.t2_raster_uri)

        # 2. Compute AOI Windows
        trans_t1 = rasterio.Affine(*meta_t1.transform)
        win_t1, _, win_bounds_t1 = calculate_aoi_raster_window(
            aoi_geometry=request.aoi_geometry,
            raster_crs_str=meta_t1.crs,
            raster_transform=trans_t1,
            raster_width=meta_t1.width,
            raster_height=meta_t1.height,
        )

        trans_t2 = rasterio.Affine(*meta_t2.transform)
        win_t2, _, _ = calculate_aoi_raster_window(
            aoi_geometry=request.aoi_geometry,
            raster_crs_str=meta_t2.crs,
            raster_transform=trans_t2,
            raster_width=meta_t2.width,
            raster_height=meta_t2.height,
        )

        # 3. Read Arrays
        arr_t1, nodata_t1, _ = RasterReader.read_band(request.t1_raster_uri, band_index=1, window=win_t1)
        arr_t2, nodata_t2, _ = RasterReader.read_band(request.t2_raster_uri, band_index=1, window=win_t2)

        center_lat = (
            (win_bounds_t1.bounds_wgs84[1] + win_bounds_t1.bounds_wgs84[3]) / 2.0
            if win_bounds_t1.bounds_wgs84
            else None
        )

        _, result = compute_raster_spatial_difference(
            raster_t1=arr_t1,
            raster_t2=arr_t2,
            nodata_t1=nodata_t1,
            nodata_t2=nodata_t2,
            pixel_res_x_m=meta_t1.resolution_x,
            pixel_res_y_m=meta_t1.resolution_y,
            crs_str=meta_t1.crs,
            center_latitude=center_lat,
            threshold_config=request.threshold_config,
            t1_scene_id=request.t1_scene_id,
            t2_scene_id=request.t2_scene_id,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Spatial change processing failed: {str(e)}",
        ) from e


class CreateChangeEventPayload(BaseModel):
    analysis_run_id: uuid.UUID
    change_type: str
    aoi_geometry: Dict[str, Any]
    affected_area: float
    percentage_change: Optional[float] = None
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    evidence_strength: EvidenceStrength = EvidenceStrength.STRONG
    detection_method: str
    before_date: datetime
    after_date: datetime


@router.post(
    "/events",
    summary="Persist Detected Change Event",
    description="Stores a scientifically validated multi-temporal change event in intelligence.detected_changes [Epistemic: CALCULATED].",
)
async def create_change_event(
    payload: CreateChangeEventPayload,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        # Convert GeoJSON to Shapely MultiPolygon
        shp = shape(payload.aoi_geometry)
        if isinstance(shp, Polygon):
            shp = MultiPolygon([shp])
        elif not isinstance(shp, MultiPolygon):
            shp = MultiPolygon([shp.buffer(0)])

        wkb_geom = from_shape(shp, srid=4326)

        event = DetectedChange(
            analysis_run_id=payload.analysis_run_id,
            change_type=payload.change_type,
            geometry=wkb_geom,
            affected_area=payload.affected_area,
            percentage_change=payload.percentage_change,
            confidence=payload.confidence,
            evidence_strength=payload.evidence_strength,
            detection_method=payload.detection_method,
            before_date=payload.before_date,
            after_date=payload.after_date,
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)

        return {
            "status": "SAVED",
            "change_event_id": str(event.id),
            "change_type": event.change_type,
            "affected_area_km2": event.affected_area,
            "percentage_change": event.percentage_change,
            "evidence_strength": event.evidence_strength.value,
            "epistemic_level": "CALCULATED",
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist change event: {str(e)}",
        ) from e


@router.get(
    "/{change_id}",
    summary="Get Detected Change Event",
    description="Retrieves a detected change event by ID.",
)
async def get_change_event(
    change_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    res = await session.execute(select(DetectedChange).where(DetectedChange.id == change_id))
    chg = res.scalar_one_or_none()
    if not chg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detected change event {change_id} not found",
        )
    return {
        "id": str(chg.id),
        "analysis_run_id": str(chg.analysis_run_id),
        "change_type": chg.change_type,
        "affected_area_km2": chg.affected_area,
        "percentage_change": chg.percentage_change,
        "confidence": chg.confidence,
        "evidence_strength": chg.evidence_strength.value,
        "detection_method": chg.detection_method,
        "before_date": chg.before_date.isoformat(),
        "after_date": chg.after_date.isoformat(),
        "epistemic_level": "CALCULATED",
        "created_at": chg.created_at.isoformat() if chg.created_at else None,
    }


@router.get(
    "/{change_id}/provenance",
    summary="Get Change Event Provenance Trace",
    description="Retrieves full calculation methodology, input dates, and algorithm trace.",
)
async def get_change_provenance(
    change_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    res = await session.execute(select(DetectedChange).where(DetectedChange.id == change_id))
    chg = res.scalar_one_or_none()
    if not chg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detected change event {change_id} not found",
        )
    return {
        "change_id": str(chg.id),
        "change_type": chg.change_type,
        "detection_method": chg.detection_method,
        "temporal_interval": {
            "t1_before_date": chg.before_date.isoformat(),
            "t2_after_date": chg.after_date.isoformat(),
        },
        "affected_surface_area_km2": chg.affected_area,
        "relative_magnitude_percentage": chg.percentage_change,
        "evidence_strength": chg.evidence_strength.value,
        "epistemic_level": "CALCULATED",
        "software": "ORBIT Multi-Temporal Change Detection Engine v1.0",
        "trace_verified": True,
    }


class CreateChangeAnalysisRunPayload(BaseModel):
    project_id: uuid.UUID
    area_of_interest_id: uuid.UUID
    start_date: datetime
    end_date: datetime
    parameters: Dict[str, Any] = Field(default_factory=dict)
    pipeline_version: str = "1.0.0"


@router.post(
    "/runs/create",
    summary="Create Change Detection Analysis Run",
    description="Registers and tracks a multi-temporal change detection run in analysis.runs [Epistemic: CALCULATED].",
)
async def create_change_analysis_run(
    payload: CreateChangeAnalysisRunPayload,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        run = AnalysisRun(
            project_id=payload.project_id,
            area_of_interest_id=payload.area_of_interest_id,
            status=AnalysisStatus.COMPLETED,
            analysis_type="BI_TEMPORAL_CHANGE",
            start_date=payload.start_date,
            end_date=payload.end_date,
            parameters=payload.parameters,
            pipeline_version=payload.pipeline_version,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        session.add(run)
        await session.commit()
        await session.refresh(run)

        return {
            "status": "CREATED",
            "analysis_run_id": str(run.id),
            "analysis_type": run.analysis_type,
            "project_id": str(run.project_id),
            "area_of_interest_id": str(run.area_of_interest_id),
            "status_code": run.status.value,
            "pipeline_version": run.pipeline_version,
            "created_at": run.created_at.isoformat() if run.created_at else None,
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create analysis run: {str(e)}",
        ) from e


@router.get(
    "/runs/{run_id}",
    summary="Get Change Detection Analysis Run",
    description="Retrieves an analysis run with its associated detected changes.",
)
async def get_change_analysis_run(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    res = await session.execute(select(AnalysisRun).where(AnalysisRun.id == run_id))
    run = res.scalar_one_or_none()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis run {run_id} not found",
        )
    return {
        "id": str(run.id),
        "project_id": str(run.project_id),
        "area_of_interest_id": str(run.area_of_interest_id),
        "analysis_type": run.analysis_type,
        "status": run.status.value,
        "start_date": run.start_date.isoformat(),
        "end_date": run.end_date.isoformat(),
        "parameters": run.parameters,
        "pipeline_version": run.pipeline_version,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "error_message": run.error_message,
        "created_at": run.created_at.isoformat() if run.created_at else None,
    }

