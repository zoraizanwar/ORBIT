import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.intelligence.ai_synthesis import (
    AIInterpretation,
    AIClaim,
    AIRecommendation,
    AIReport,
)
from app.services.ai import (
    EvidencePackage,
    AIInterpretationResult,
    InterpretRequestPayload,
    ValidateClaimsPayload,
    ReportRequestPayload,
    ReportResult,
    EvidenceRetriever,
    ClaimValidator,
    GroundedReasoner,
    ReportGenerator,
    InsufficientEvidenceError,
    ClaimValidationError,
    HallucinationError,
    AIIntelligenceError,
)

router = APIRouter(prefix="/ai", tags=["Grounded AI Intelligence & Reporting"])


class PackageRequestPayload(BaseModel):
    aoi_id: str
    aoi_name: Optional[str] = "Selected Area of Interest"
    include_contradiction: bool = False


class DecisionSupportPayload(BaseModel):
    aoi_id: str
    evidence_package: Optional[EvidencePackage] = None


@router.post(
    "/evidence/package",
    response_model=EvidencePackage,
    summary="Assemble Deterministic Evidence Package",
    description="Retrieves and packages raw observations, calculated indices, change events, and forecasts into a SHA-256 digested package.",
)
async def assemble_evidence_package(
    payload: PackageRequestPayload,
) -> EvidencePackage:
    try:
        return EvidenceRetriever.get_seed_evidence_package(
            aoi_id=payload.aoi_id,
            aoi_name=payload.aoi_name or payload.aoi_id,
            include_contradiction=payload.include_contradiction,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assemble evidence package: {str(e)}",
        ) from e


@router.post(
    "/interpret",
    response_model=AIInterpretationResult,
    summary="Generate Grounded AI Intelligence Synthesis",
    description="Executes deterministic or local LLM reasoning constrained strictly to grounded evidence with adversarial post-generation validation.",
)
async def generate_interpretation(
    payload: InterpretRequestPayload,
    session: AsyncSession = Depends(get_db),
) -> AIInterpretationResult:
    try:
        aoi_uuid = uuid.UUID(payload.aoi_id) if len(payload.aoi_id) == 36 else None

        result = GroundedReasoner.interpret(payload)

        # Persist to database if valid UUID
        if aoi_uuid:
            interp_db = AIInterpretation(
                id=uuid.UUID(result.id) if len(result.id) == 36 else uuid.uuid4(),
                area_of_interest_id=aoi_uuid,
                interpretation_type=result.interpretation_type.value,
                title=result.title,
                executive_summary=result.executive_summary,
                epistemic_level=result.epistemic_level,
                evidence_package_hash=result.evidence_package_hash,
                provider_name=result.provider_info.get("provider", "ORBIT-LocalReasoner"),
                model_name=result.provider_info.get("model", "DeterministicGroundedSynthesizer"),
                model_version=result.provider_info.get("version", "1.0.0"),
                uncertainty_statement=result.uncertainty_statement,
                contradiction_statement=result.contradiction_statement,
                temporal_interpretation=result.temporal_interpretation,
                spatial_interpretation=result.spatial_interpretation,
                forecast_interpretation=result.forecast_interpretation,
                provenance=result.provenance,
                created_at=datetime.now(timezone.utc),
            )
            session.add(interp_db)

            for clm in result.claims:
                claim_db = AIClaim(
                    id=uuid.uuid4(),
                    ai_interpretation_id=interp_db.id,
                    claim_text=clm.claim_text,
                    claim_type=clm.claim_type.value,
                    epistemic_level=clm.epistemic_level,
                    evidence_ids=clm.evidence_ids,
                    support_status=clm.support_status.value,
                    confidence=clm.confidence,
                    validation_details=clm.validation_details,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(claim_db)

            for rec in result.recommendations:
                rec_db = AIRecommendation(
                    id=uuid.uuid4(),
                    ai_interpretation_id=interp_db.id,
                    category=rec.category.value,
                    recommendation_text=rec.recommendation_text,
                    reason=rec.reason,
                    priority=rec.priority.value,
                    supporting_evidence_ids=rec.supporting_evidence_ids,
                    uncertainty_note=rec.uncertainty_note,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(rec_db)

            await session.commit()

        return result
    except InsufficientEvidenceError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "status": "INSUFFICIENT_EVIDENCE",
                "reason": str(e),
                "required_types": e.required_types,
                "available_types": e.available_types,
            },
        ) from e
    except (ClaimValidationError, HallucinationError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "status": "HALLUCINATION_OR_GROUNDING_VIOLATION",
                "reason": str(e),
            },
        ) from e
    except AIIntelligenceError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI interpretation failed: {str(e)}",
        ) from e


@router.post(
    "/claims/validate",
    summary="Validate AI Claims Against Grounded Evidence",
    description="Deterministic adversary validating referenced evidence IDs, numerical fidelity, and contradiction alignment.",
)
async def validate_claims_endpoint(
    payload: ValidateClaimsPayload,
) -> Dict[str, Any]:
    validated, is_all_valid = ClaimValidator.validate_claims(
        evidence_package=payload.evidence_package,
        claims=payload.claims,
    )
    return {
        "is_all_valid": is_all_valid,
        "claims_count": len(validated),
        "validated_claims": [c.model_dump() for c in validated],
    }


@router.post(
    "/reports/generate",
    response_model=ReportResult,
    summary="Generate Grounded Intelligence Report",
    description="Produces comprehensive, signed Markdown, JSON, or PDF intelligence reports.",
)
async def generate_report_endpoint(
    payload: ReportRequestPayload,
    session: AsyncSession = Depends(get_db),
) -> ReportResult:
    try:
        aoi_uuid = uuid.UUID(payload.aoi_id) if len(payload.aoi_id) == 36 else None

        result = ReportGenerator.generate_report(payload)

        if aoi_uuid:
            report_db = AIReport(
                id=uuid.UUID(result.report_id) if len(result.report_id) == 36 else uuid.uuid4(),
                area_of_interest_id=aoi_uuid,
                title=result.title,
                report_type=result.report_type,
                report_format=result.report_format.value,
                content=result.content_text,
                provenance_hash_sha256=result.provenance_hash_sha256,
                created_at=datetime.now(timezone.utc),
            )
            session.add(report_db)
            await session.commit()

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}",
        ) from e


@router.post(
    "/decision-support",
    summary="Generate Operational Decision Support Recommendations",
    description="Derives prioritized operational actions deterministically from grounded evidence strength and contradiction state.",
)
async def generate_decision_support(
    payload: DecisionSupportPayload,
) -> Dict[str, Any]:
    pkg = payload.evidence_package or EvidenceRetriever.get_seed_evidence_package(aoi_id=payload.aoi_id)
    interp = GroundedReasoner.interpret(
        InterpretRequestPayload(aoi_id=payload.aoi_id),
        evidence_package=pkg,
    )
    return {
        "aoi_id": payload.aoi_id,
        "evidence_package_hash": pkg.package_hash_sha256,
        "has_contradictions": pkg.has_contradictions,
        "recommendations": [rec.model_dump() for rec in interp.recommendations],
    }


@router.get(
    "/interpretations/{interpretation_id}",
    summary="Get AI Interpretation By ID",
    description="Retrieves a saved grounded interpretation record.",
)
async def get_interpretation_by_id(
    interpretation_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    res = await session.execute(
        select(AIInterpretation).where(AIInterpretation.id == interpretation_id)
    )
    interp = res.scalar_one_or_none()
    if not interp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI Interpretation {interpretation_id} not found",
        )

    claims_res = await session.execute(
        select(AIClaim).where(AIClaim.ai_interpretation_id == interpretation_id)
    )
    claims = claims_res.scalars().all()

    rec_res = await session.execute(
        select(AIRecommendation).where(AIRecommendation.ai_interpretation_id == interpretation_id)
    )
    recs = rec_res.scalars().all()

    return {
        "id": str(interp.id),
        "aoi_id": str(interp.area_of_interest_id),
        "title": interp.title,
        "interpretation_type": interp.interpretation_type,
        "executive_summary": interp.executive_summary,
        "epistemic_level": interp.epistemic_level,
        "evidence_package_hash": interp.evidence_package_hash,
        "uncertainty_statement": interp.uncertainty_statement,
        "contradiction_statement": interp.contradiction_statement,
        "temporal_interpretation": interp.temporal_interpretation,
        "spatial_interpretation": interp.spatial_interpretation,
        "forecast_interpretation": interp.forecast_interpretation,
        "claims": [
            {
                "claim_id": str(c.id),
                "claim_text": c.claim_text,
                "claim_type": c.claim_type,
                "epistemic_level": c.epistemic_level,
                "evidence_ids": c.evidence_ids,
                "support_status": c.support_status,
                "confidence": c.confidence,
            }
            for c in claims
        ],
        "recommendations": [
            {
                "recommendation_id": str(r.id),
                "category": r.category,
                "recommendation_text": r.recommendation_text,
                "reason": r.reason,
                "priority": r.priority,
                "supporting_evidence_ids": r.supporting_evidence_ids,
            }
            for r in recs
        ],
        "provenance": interp.provenance,
        "created_at": interp.created_at.isoformat() if interp.created_at else None,
    }


@router.get(
    "/interpretations/{interpretation_id}/provenance",
    summary="Get Interpretation Provenance",
    description="Retrieves complete calculation trace and cryptographic lineage for an AI interpretation.",
)
async def get_interpretation_provenance(
    interpretation_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    res = await session.execute(
        select(AIInterpretation).where(AIInterpretation.id == interpretation_id)
    )
    interp = res.scalar_one_or_none()
    if not interp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI Interpretation {interpretation_id} not found",
        )

    return {
        "interpretation_id": str(interp.id),
        "evidence_package_hash": interp.evidence_package_hash,
        "provider_name": interp.provider_name,
        "model_name": interp.model_name,
        "model_version": interp.model_version,
        "prompt_version": interp.prompt_version,
        "epistemic_level": interp.epistemic_level,
        "provenance_trace": interp.provenance,
    }
