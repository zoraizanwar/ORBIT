import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.services.eo.operational.models import (
    OperationalAOICreateRequest,
    OperationalAOIResponse,
    OperationalSceneSearchRequest,
    OperationalSceneRankRequest,
    ObservationPairSelectRequest,
    ObservationPairSelectResponse,
    OperationalJobCreateRequest,
    OperationalJobStatusResponse,
    JobStage,
    JobStatus,
)
from app.services.eo.operational.aoi_service import OperationalAOIService
from app.services.eo.operational.discovery_service import STACDiscoveryService
from app.services.eo.operational.ranking_service import SceneSelectionService
from app.services.eo.operational.pair_service import ObservationPairService
from app.services.eo.acquisition.secure_downloader import (
    SecureAssetAcquisitionService,
    AssetAcquisitionRequest,
)
from app.services.eo.raster.real_raster_validator import RealRasterValidator
from app.services.eo.real_pipeline import RealDataPipelineOrchestrator
from app.services.eo.stac.models import NormalizedImageryScene

logger = logging.getLogger("orbit.operational")
router = APIRouter(prefix="/operational", tags=["Operational Workstation"])

# In-memory storage for active operational jobs and results
_JOBS: Dict[str, Dict[str, Any]] = {}
_RESULTS: Dict[str, Dict[str, Any]] = {}
_ACQUIRED_ASSETS: Dict[str, Dict[str, Any]] = {}


@router.post("/aoi", response_model=OperationalAOIResponse, status_code=status.HTTP_201_CREATED)
async def create_operational_aoi(payload: OperationalAOICreateRequest):
    """
    Validates and creates an Operational Area of Interest (AOI) session.
    Enforces WGS84 (EPSG:4326), valid geometry bounds, and computes geodesic area.
    """
    try:
        return OperationalAOIService.validate_and_create_aoi(
            name=payload.name,
            geometry=payload.geometry,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to create operational AOI: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="AOI session creation failed.")


@router.get("/aoi/{aoi_id}", response_model=OperationalAOIResponse)
async def get_operational_aoi(aoi_id: str):
    """Retrieves an active Operational AOI session by ID."""
    aoi = OperationalAOIService.get_aoi(aoi_id)
    if not aoi:
        raise HTTPException(status_code=404, detail=f"AOI session '{aoi_id}' not found.")
    return aoi


@router.post("/scenes/search")
async def search_operational_scenes(payload: OperationalSceneSearchRequest):
    """
    Searches configured live STAC providers for imagery overlapping the target AOI.
    """
    try:
        bbox_override = None
        if payload.aoi_id:
            aoi = OperationalAOIService.get_aoi(payload.aoi_id)
            if aoi:
                bbox_override = aoi.bbox

        resp = await STACDiscoveryService.search_scenes(payload, bbox_override=bbox_override)
        return resp.model_dump()
    except Exception as e:
        logger.error(f"STAC scene search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Operational STAC search failed.")


@router.post("/scenes/rank")
async def rank_operational_scenes(payload: OperationalSceneRankRequest):
    """
    Deterministically ranks candidate STAC scenes against target AOI bbox, temporal proximity,
    cloud cover, and spatial resolution using Phase 15 ranker.
    """
    try:
        # Convert candidate dicts to NormalizedImageryScene models
        scenes: List[NormalizedImageryScene] = []
        for s_dict in payload.candidate_scenes:
            try:
                scenes.append(NormalizedImageryScene(**s_dict))
            except Exception:
                pass

        if not scenes:
            raise ValueError("No valid candidate scene metadata provided.")

        ranked = SceneSelectionService.rank_candidate_scenes(
            candidate_scenes=scenes,
            target_aoi_bbox=payload.target_aoi_bbox,
            target_datetime=payload.target_datetime,
            criteria=payload.ranking_criteria,
        )
        return {"ranked_scenes": [r.model_dump() for r in ranked], "total": len(ranked)}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Scene ranking failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Deterministic scene ranking failed.")


@router.post("/pair/select", response_model=ObservationPairSelectResponse)
async def select_observation_pair(payload: ObservationPairSelectRequest):
    """
    Validates and registers a multi-temporal observation pair (T1 baseline and T2 comparison).
    Enforces strict temporal ordering (T1 < T2) and required spectral band availability.
    """
    try:
        return ObservationPairService.validate_and_select_pair(payload)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Observation pair validation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Observation pair validation failed.")


@router.post("/assets/acquire")
async def acquire_operational_asset(payload: AssetAcquisitionRequest):
    """
    Acquires and caches a remote raster asset securely with SSRF checks, size caps, and SHA-256 verification.
    """
    try:
        record = await SecureAssetAcquisitionService.acquire_asset(payload)
        record_dict = record.model_dump()
        _ACQUIRED_ASSETS[record.sha256_checksum] = record_dict
        return record_dict
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Asset acquisition failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Secure asset acquisition failed.")


@router.get("/assets/{asset_id}")
async def get_operational_asset_metadata(asset_id: str):
    """
    Retrieves acquisition metadata and header validation for a cached raster asset.
    """
    record = _ACQUIRED_ASSETS.get(asset_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Acquired asset '{asset_id}' not found.")
    return record


@router.post("/jobs", response_model=OperationalJobStatusResponse, status_code=status.HTTP_201_CREATED)
async def create_operational_job(payload: OperationalJobCreateRequest):
    """
    Initializes an operational multi-temporal analysis job.
    """
    job_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    job_data = {
        "job_id": job_id,
        "aoi_id": payload.aoi_id,
        "aoi_name": payload.aoi_name,
        "aoi_geometry": payload.aoi_geometry,
        "t1_scene_id": payload.t1_scene_id,
        "t1_band_paths": payload.t1_band_paths,
        "t1_datetime": payload.t1_datetime.isoformat(),
        "t2_scene_id": payload.t2_scene_id,
        "t2_band_paths": payload.t2_band_paths,
        "t2_datetime": payload.t2_datetime.isoformat(),
        "platform": payload.platform,
        "sensor": payload.sensor,
        "nearby_road_distance_m": payload.nearby_road_distance_m,
        "is_test_fixture": payload.is_test_fixture,
        "status": JobStatus.PENDING,
        "current_stage": JobStage.INITIALIZED,
        "started_at": now_iso,
        "completed_at": None,
        "duration_ms": None,
        "error_metadata": None,
    }
    _JOBS[job_id] = job_data

    return OperationalJobStatusResponse(
        job_id=job_id,
        aoi_id=payload.aoi_id,
        status=JobStatus.PENDING,
        current_stage=JobStage.INITIALIZED,
        started_at=now_iso,
        is_test_fixture=payload.is_test_fixture,
    )


@router.get("/jobs/{job_id}", response_model=OperationalJobStatusResponse)
async def get_operational_job_status(job_id: str):
    """Retrieves current lifecycle status of an operational analysis job."""
    job = _JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    return OperationalJobStatusResponse(
        job_id=job["job_id"],
        aoi_id=job["aoi_id"],
        status=job["status"],
        current_stage=job["current_stage"],
        started_at=job["started_at"],
        completed_at=job.get("completed_at"),
        duration_ms=job.get("duration_ms"),
        error_metadata=job.get("error_metadata"),
        is_test_fixture=job.get("is_test_fixture", False),
    )


@router.post("/jobs/{job_id}/execute")
async def execute_operational_job(job_id: str):
    """
    Executes the 8-tier live analytical pipeline for the given job.
    """
    job = _JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    job["status"] = JobStatus.RUNNING
    job["current_stage"] = JobStage.RASTER_VALIDATION

    try:
        t1_dt = datetime.fromisoformat(job["t1_datetime"])
        t2_dt = datetime.fromisoformat(job["t2_datetime"])

        result = await RealDataPipelineOrchestrator.run_operational_pipeline(
            aoi_id=job["aoi_id"],
            aoi_name=job["aoi_name"],
            aoi_geometry=job["aoi_geometry"],
            t1_scene_id=job["t1_scene_id"],
            t1_band_paths=job["t1_band_paths"],
            t1_datetime=t1_dt,
            t2_scene_id=job["t2_scene_id"],
            t2_band_paths=job["t2_band_paths"],
            t2_datetime=t2_dt,
            platform=job["platform"],
            sensor=job["sensor"],
            nearby_road_distance_m=job.get("nearby_road_distance_m"),
            is_test_fixture=job.get("is_test_fixture", False),
        )

        job["status"] = JobStatus.COMPLETED
        job["current_stage"] = JobStage.COMPLETED
        job["completed_at"] = datetime.now(timezone.utc).isoformat()
        job["duration_ms"] = result.get("duration_ms", 120.0)

        # Store serialized result
        _RESULTS[job_id] = result
        return {"status": "SUCCESS", "job_id": job_id, "summary": result.get("summary")}
    except Exception as e:
        logger.error(f"Job execution failed for {job_id}: {e}", exc_info=True)
        job["status"] = JobStatus.FAILED
        job["current_stage"] = JobStage.FAILED
        job["error_metadata"] = {"error": str(e)}
        raise HTTPException(status_code=500, detail=f"Operational pipeline execution failed: {str(e)}")


@router.get("/jobs/{job_id}/results")
async def get_operational_job_results(job_id: str):
    """
    Returns the grounded analytical outputs, difference metrics, rules, and AI synthesis for a completed job.
    """
    res = _RESULTS.get(job_id)
    if not res:
        job = _JOBS.get(job_id)
        if job and job["status"] == JobStatus.RUNNING:
            raise HTTPException(status_code=202, detail="Job is currently executing.")
        raise HTTPException(status_code=404, detail=f"Results for job '{job_id}' not found.")
    return res


@router.get("/jobs/{job_id}/provenance")
async def get_operational_job_provenance(job_id: str):
    """
    Returns the complete cryptographic provenance chain, SHA-256 digests, and licensing attributions.
    """
    res = _RESULTS.get(job_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Provenance records for job '{job_id}' not found.")

    return {
        "job_id": job_id,
        "provenance_records": res.get("provenance_records", []),
        "evidence_package_hash": res.get("evidence_package", {}).package_hash_sha256 if hasattr(res.get("evidence_package"), "package_hash_sha256") else res.get("evidence_package_hash"),
        "report_provenance_hash": res.get("report", {}).provenance_hash_sha256 if hasattr(res.get("report"), "provenance_hash_sha256") else res.get("report_provenance_hash"),
        "is_test_fixture": res.get("is_test_fixture", False),
    }
