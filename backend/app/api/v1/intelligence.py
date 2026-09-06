import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import from_shape
from shapely.geometry import shape, MultiPolygon, Polygon

from app.db.session import get_db
from app.models.enums import EpistemicLevel, EvidenceStrength, AnalysisStatus
from app.models.intelligence.intelligence_event import IntelligenceEvent
from app.models.intelligence.evidence_record import EvidenceRecord
from app.models.intelligence.evidence_relationship import EvidenceRelationship
from app.models.analysis.analysis_run import AnalysisRun
from app.services.intelligence import (
    IntelligenceEngine,
    RuleEvaluationInput,
    IntelligenceObjectResult,
    EvidenceGraphTraverser,
)

router = APIRouter(prefix="/intelligence", tags=["Advanced Geospatial Intelligence & Evidence"])


class AnalyzePayload(BaseModel):
    project_id: Optional[uuid.UUID] = None
    area_of_interest_id: Optional[uuid.UUID] = None
    aoi_geometry: Dict[str, Any]
    target_start_date: datetime
    target_end_date: datetime
    ndvi_delta: Optional[float] = None
    ndwi_delta: Optional[float] = None
    ndbi_delta: Optional[float] = None
    affected_area_km2: float = 0.0
    primary_sensor: str = "Sentinel-2"
    secondary_sensor: Optional[str] = None
    secondary_sensor_signal_delta: Optional[float] = None
    road_features: Optional[List[Dict[str, Any]]] = None


@router.post(
    "/analyze",
    response_model=IntelligenceObjectResult,
    summary="Execute Deterministic Intelligence Analysis",
    description="Correlates multi-spectral indices, spatial infrastructure context, and sensor telemetry to produce structured intelligence and evidence graphs [Epistemic: CALCULATED/DETECTED].",
)
async def analyze_intelligence(
    payload: AnalyzePayload,
    session: AsyncSession = Depends(get_db),
) -> IntelligenceObjectResult:
    try:
        # 1. Create or resolve AnalysisRun if IDs provided
        run_id_val = str(uuid.uuid4())
        if payload.project_id and payload.area_of_interest_id:
            run = AnalysisRun(
                id=uuid.UUID(run_id_val),
                project_id=payload.project_id,
                area_of_interest_id=payload.area_of_interest_id,
                status=AnalysisStatus.COMPLETED,
                analysis_type="MULTI_INDICATOR_INTELLIGENCE",
                start_date=payload.target_start_date,
                end_date=payload.target_end_date,
                parameters={
                    "ndvi_delta": payload.ndvi_delta,
                    "ndwi_delta": payload.ndwi_delta,
                    "ndbi_delta": payload.ndbi_delta,
                    "primary_sensor": payload.primary_sensor,
                },
                pipeline_version="1.0.0",
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
            )
            session.add(run)
            await session.commit()

        # 2. Execute Deterministic Intelligence Engine
        rule_input = RuleEvaluationInput(
            aoi_id=str(payload.area_of_interest_id) if payload.area_of_interest_id else None,
            aoi_geometry=payload.aoi_geometry,
            target_start_date=payload.target_start_date,
            target_end_date=payload.target_end_date,
            ndvi_delta=payload.ndvi_delta,
            ndwi_delta=payload.ndwi_delta,
            ndbi_delta=payload.ndbi_delta,
            affected_area_km2=payload.affected_area_km2,
            primary_sensor=payload.primary_sensor,
            secondary_sensor=payload.secondary_sensor,
            secondary_sensor_signal_delta=payload.secondary_sensor_signal_delta,
        )

        result = IntelligenceEngine.execute_intelligence_analysis(
            payload=rule_input,
            road_features=payload.road_features,
            analysis_run_id=run_id_val,
        )

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Intelligence analysis evaluation failed: {str(e)}",
        ) from e


@router.get(
    "/events",
    summary="Query Intelligence Events",
    description="Queries intelligence events with filtering and pagination.",
)
async def list_intelligence_events(
    intelligence_type: Optional[str] = Query(None),
    evidence_strength: Optional[EvidenceStrength] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    query = select(IntelligenceEvent)
    conditions = []
    if intelligence_type:
        conditions.append(IntelligenceEvent.intelligence_type == intelligence_type)
    if evidence_strength:
        conditions.append(IntelligenceEvent.evidence_strength == evidence_strength)
    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(desc(IntelligenceEvent.created_at)).offset(offset).limit(limit)
    res = await session.execute(query)
    events = res.scalars().all()

    return {
        "total": len(events),
        "offset": offset,
        "limit": limit,
        "items": [
            {
                "id": str(evt.id),
                "analysis_run_id": str(evt.analysis_run_id),
                "intelligence_type": evt.intelligence_type,
                "title": evt.title,
                "affected_area_km2": evt.affected_area,
                "start_date": evt.start_date.isoformat(),
                "end_date": evt.end_date.isoformat(),
                "evidence_strength": evt.evidence_strength.value,
                "epistemic_level": evt.epistemic_level.value,
                "confidence": evt.confidence,
                "rule_id": evt.rule_id,
                "status": evt.status,
                "created_at": evt.created_at.isoformat() if evt.created_at else None,
            }
            for evt in events
        ],
    }


@router.get(
    "/{intelligence_id}",
    summary="Get Intelligence Event",
    description="Retrieves a specific intelligence object by UUID.",
)
async def get_intelligence_event(
    intelligence_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    res = await session.execute(select(IntelligenceEvent).where(IntelligenceEvent.id == intelligence_id))
    evt = res.scalar_one_or_none()
    if not evt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intelligence object {intelligence_id} not found",
        )
    return {
        "id": str(evt.id),
        "analysis_run_id": str(evt.analysis_run_id),
        "area_of_interest_id": str(evt.area_of_interest_id) if evt.area_of_interest_id else None,
        "intelligence_type": evt.intelligence_type,
        "title": evt.title,
        "affected_area_km2": evt.affected_area,
        "start_date": evt.start_date.isoformat(),
        "end_date": evt.end_date.isoformat(),
        "evidence_strength": evt.evidence_strength.value,
        "epistemic_level": evt.epistemic_level.value,
        "confidence": evt.confidence,
        "rule_id": evt.rule_id,
        "rule_version": evt.rule_version,
        "algorithm_version": evt.algorithm_version,
        "quality_metadata": evt.quality_metadata,
        "provenance": evt.provenance,
        "status": evt.status,
        "created_at": evt.created_at.isoformat() if evt.created_at else None,
    }


@router.get(
    "/{intelligence_id}/evidence",
    summary="Get Intelligence Supporting Evidence",
    description="Retrieves all evidence records linked to this intelligence object.",
)
async def get_intelligence_evidence(
    intelligence_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    res = await session.execute(
        select(EvidenceRecord).where(EvidenceRecord.intelligence_event_id == intelligence_id)
    )
    records = res.scalars().all()
    return {
        "intelligence_id": str(intelligence_id),
        "evidence_count": len(records),
        "evidence_records": [
            {
                "id": str(rec.id),
                "source_type": rec.source_type,
                "source_id": rec.source_id,
                "claim_type": rec.claim_type,
                "claim_reference": rec.claim_reference,
                "input_checksum": rec.input_checksum,
                "evidence_strength": rec.evidence_strength.value,
                "epistemic_level": rec.epistemic_level.value,
                "algorithm": rec.algorithm,
                "parameters": rec.parameters,
                "created_at": rec.created_at.isoformat() if rec.created_at else None,
            }
            for rec in records
        ],
    }


@router.get(
    "/{intelligence_id}/provenance",
    summary="Get Intelligence Provenance Trace",
    description="Retrieves full deterministic lineage and calculation trace for the intelligence object.",
)
async def get_intelligence_provenance(
    intelligence_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    res = await session.execute(select(IntelligenceEvent).where(IntelligenceEvent.id == intelligence_id))
    evt = res.scalar_one_or_none()
    if not evt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intelligence object {intelligence_id} not found",
        )
    return {
        "intelligence_id": str(evt.id),
        "rule_id": evt.rule_id,
        "rule_version": evt.rule_version,
        "algorithm_version": evt.algorithm_version,
        "epistemic_level": evt.epistemic_level.value,
        "evidence_strength": evt.evidence_strength.value,
        "confidence": evt.confidence,
        "quality_metadata": evt.quality_metadata,
        "provenance_trace": evt.provenance,
        "evaluated_at": evt.created_at.isoformat() if evt.created_at else None,
    }


@router.get(
    "/{intelligence_id}/relationships",
    summary="Get Evidence Graph Relationships",
    description="Retrieves all graph relationship edges for an intelligence object.",
)
async def get_intelligence_relationships(
    intelligence_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    res = await session.execute(
        select(EvidenceRelationship).where(EvidenceRelationship.target_entity_id == str(intelligence_id))
    )
    rels = res.scalars().all()
    return {
        "intelligence_id": str(intelligence_id),
        "relationships_count": len(rels),
        "relationships": [
            {
                "id": str(rel.id),
                "source_evidence_id": str(rel.source_evidence_id),
                "target_entity_type": rel.target_entity_type,
                "target_entity_id": rel.target_entity_id,
                "relationship_type": rel.relationship_type,
                "weight": rel.weight,
                "metadata_payload": rel.metadata_payload,
                "created_at": rel.created_at.isoformat() if rel.created_at else None,
            }
            for rel in rels
        ],
    }


class EvidenceQueryPayload(BaseModel):
    source_type: Optional[str] = None
    claim_type: Optional[str] = None
    evidence_strength: Optional[EvidenceStrength] = None
    epistemic_level: Optional[EpistemicLevel] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


@router.post(
    "/evidence/query",
    summary="Query Evidence Records",
    description="Queries evidence records with multifaceted filters and pagination.",
)
async def query_evidence_records(
    payload: EvidenceQueryPayload,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    query = select(EvidenceRecord)
    conditions = []
    if payload.source_type:
        conditions.append(EvidenceRecord.source_type == payload.source_type)
    if payload.claim_type:
        conditions.append(EvidenceRecord.claim_type == payload.claim_type)
    if payload.evidence_strength:
        conditions.append(EvidenceRecord.evidence_strength == payload.evidence_strength)
    if payload.epistemic_level:
        conditions.append(EvidenceRecord.epistemic_level == payload.epistemic_level)
    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(desc(EvidenceRecord.created_at)).offset(payload.offset).limit(payload.limit)
    res = await session.execute(query)
    records = res.scalars().all()

    return {
        "total": len(records),
        "offset": payload.offset,
        "limit": payload.limit,
        "items": [
            {
                "id": str(rec.id),
                "analysis_run_id": str(rec.analysis_run_id),
                "intelligence_event_id": str(rec.intelligence_event_id) if rec.intelligence_event_id else None,
                "source_type": rec.source_type,
                "source_id": rec.source_id,
                "claim_type": rec.claim_type,
                "claim_reference": rec.claim_reference,
                "evidence_strength": rec.evidence_strength.value,
                "epistemic_level": rec.epistemic_level.value,
                "created_at": rec.created_at.isoformat() if rec.created_at else None,
            }
            for rec in records
        ],
    }
