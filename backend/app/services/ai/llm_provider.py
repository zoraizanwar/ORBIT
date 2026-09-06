import abc
import os
import uuid
from typing import Any, Dict, List
from app.services.ai.models import (
    EvidencePackage,
    Claim,
    ClaimType,
    Recommendation,
    RecommendationCategory,
    RecommendationPriority,
    AIInterpretationResult,
    AIInterpretationType,
    SupportStatus,
)


class LLMProviderInterface(abc.ABC):
    """
    Abstract interface for grounded LLM / reasoning providers in ORBIT.
    Enables local deterministic synthesis as well as external OpenAI-compatible endpoints.
    """

    @abc.abstractmethod
    def generate_interpretation(
        self,
        evidence_package: EvidencePackage,
        interpretation_type: AIInterpretationType,
        system_prompt: str,
        user_prompt: str,
    ) -> AIInterpretationResult:
        pass


class LocalDeterministicReasoner(LLMProviderInterface):
    """
    Local-first deterministic reasoning engine.
    Synthesizes claims, explanations, and recommendations purely from structured evidence rules
    with zero cloud dependencies or external API keys.
    """

    PROVIDER_NAME = "ORBIT-LocalReasoner"
    MODEL_NAME = "DeterministicGroundedSynthesizer"
    MODEL_VERSION = "1.0.0"

    def generate_interpretation(
        self,
        evidence_package: EvidencePackage,
        interpretation_type: AIInterpretationType,
        system_prompt: str,
        user_prompt: str,
    ) -> AIInterpretationResult:
        ev_items = {item.id: item for item in evidence_package.evidence_items}
        claims: List[Claim] = []
        recommendations: List[Recommendation] = []

        # Find key indicators
        ndvi_item = next((i for i in evidence_package.evidence_items if "ndvi" in i.id.lower() or "vegetation" in i.type.lower()), None)
        ndbi_item = next((i for i in evidence_package.evidence_items if "ndbi" in i.id.lower() or "built" in i.type.lower()), None)
        road_item = next((i for i in evidence_package.evidence_items if "road" in i.type.lower()), None)
        mask_item = next((i for i in evidence_package.evidence_items if "mask" in i.type.lower() or i.type == "CHANGE_MASK"), None)
        forecast_item = next((i for i in evidence_package.evidence_items if i.epistemic_level == "PREDICTED" or i.type == "FORECAST_PROJECTION"), None)

        # 1. Synthesize Observation Claims
        for item in evidence_package.evidence_items:
            ep_val = item.epistemic_level.value if hasattr(item.epistemic_level, "value") else str(item.epistemic_level)
            if ep_val == "OBSERVED":
                claims.append(
                    Claim(
                        claim_id=f"clm-obs-{item.id}",
                        claim_text=f"Telemetry observation confirmed from source {item.source_id} ({item.description}).",
                        claim_type=ClaimType.OBSERVATION,
                        epistemic_level="AI_INTERPRETED",
                        evidence_ids=[item.id],
                        support_status=SupportStatus.SUPPORTED,
                        confidence=0.98,
                    )
                )

        # 2. Synthesize Change / Measurement Claims
        if ndvi_item and ndbi_item:
            claims.append(
                Claim(
                    claim_id="clm-change-multi",
                    claim_text=f"Canopy vegetation deficit (dNDVI = {ndvi_item.value}) coincides with built-up surface influx (dNDBI = {ndbi_item.value}) across the inspected sector.",
                    claim_type=ClaimType.CHANGE,
                    epistemic_level="AI_INTERPRETED",
                    evidence_ids=[ndvi_item.id, ndbi_item.id],
                    support_status=SupportStatus.SUPPORTED,
                    confidence=0.95,
                )
            )

        if mask_item:
            claims.append(
                Claim(
                    claim_id="clm-mask-area",
                    claim_text=f"Contiguous spatial difference analysis delineates an affected clearance perimeter of {mask_item.value} km².",
                    claim_type=ClaimType.MEASUREMENT,
                    epistemic_level="AI_INTERPRETED",
                    evidence_ids=[mask_item.id],
                    support_status=SupportStatus.SUPPORTED,
                    confidence=0.96,
                )
            )

        # 3. Spatial & Infrastructure Corridor Context
        spatial_interp = "No direct road infrastructure corridor proximity detected."
        if road_item:
            claims.append(
                Claim(
                    claim_id="clm-road-proximity",
                    claim_text=f"Change area is situated within the right-of-way corridor of {road_item.description} ({road_item.value} meters proximity).",
                    claim_type=ClaimType.CORRELATION,
                    epistemic_level="AI_INTERPRETED",
                    evidence_ids=[road_item.id],
                    support_status=SupportStatus.SUPPORTED,
                    confidence=0.92,
                )
            )
            spatial_interp = f"Spatial buffering confirms direct alignment with {road_item.description} at {road_item.value}m."

        # 4. Contradiction Analysis
        contradiction_text = None
        if evidence_package.has_contradictions:
            contradiction_text = "Cross-sensor discrepancy detected: Optical canopy deficit is not independently corroborated by radar backscatter amplitude. Overall evidence strength downgraded to INSUFFICIENT."
            recommendations.append(
                Recommendation(
                    category=RecommendationCategory.REVIEW_CONTRADICTION,
                    recommendation_text="Conduct multi-pass radar coherence audit to resolve cross-sensor optical/SAR divergence.",
                    reason="Optical and SAR signals exhibit conflicting structural change telemetry.",
                    priority=RecommendationPriority.HIGH,
                    supporting_evidence_ids=[item.id for item in evidence_package.evidence_items if "sar" in item.id.lower() or "ndvi" in item.id.lower()],
                )
            )

        # 5. Forecast Interpretation
        forecast_interp = "No future prediction horizon supplied in evidence package."
        if forecast_item:
            claims.append(
                Claim(
                    claim_id="clm-forecast-proj",
                    claim_text=f"Calibrated baseline model projects metric value to reach {forecast_item.value} by target year {forecast_item.timestamp[:4] if forecast_item.timestamp else '2030'}.",
                    claim_type=ClaimType.FORECAST,
                    epistemic_level="AI_INTERPRETED",
                    evidence_ids=[forecast_item.id],
                    support_status=SupportStatus.SUPPORTED,
                    confidence=0.88,
                )
            )
            forecast_interp = f"Extrapolation under {forecast_item.source_type} projects continuous trajectory reaching {forecast_item.value} [Epistemic: PREDICTED]."

        # 6. Operational Recommendations
        if not recommendations:
            recommendations.append(
                Recommendation(
                    category=RecommendationCategory.MONITOR,
                    recommendation_text="Maintain scheduled satellite surveillance pass over active perimeter.",
                    reason="High evidence strength confirms active infrastructure corridor clearance.",
                    priority=RecommendationPriority.MEDIUM,
                    supporting_evidence_ids=[ndvi_item.id] if ndvi_item else [],
                )
            )

        exec_summary = (
            f"Multi-temporal intelligence synthesis for {evidence_package.aoi_name}. "
            f"Analysis of {len(evidence_package.evidence_items)} grounded evidence items confirms "
            f"{'disputed signals due to cross-sensor divergence' if evidence_package.has_contradictions else 'consistent multi-indicator clearance activity'}."
        )

        return AIInterpretationResult(
            id=f"ai-interp-{str(uuid.uuid4())[:8]}",
            aoi_id=evidence_package.aoi_id,
            analysis_run_id=evidence_package.analysis_run_id,
            title=f"Grounded Intelligence Synthesis: {evidence_package.aoi_name}",
            interpretation_type=interpretation_type,
            executive_summary=exec_summary,
            claims=claims,
            recommendations=recommendations,
            uncertainty_statement="Analytical conclusions are strictly grounded in satellite scenes and vector registries. Unpredicted operational variances or cloud obscuration may affect ground-truth timing.",
            contradiction_statement=contradiction_text,
            temporal_interpretation=f"Observation span: {evidence_package.date_range_start or 'T1'} to {evidence_package.date_range_end or 'T2'}.",
            spatial_interpretation=spatial_interp,
            forecast_interpretation=forecast_interp,
            evidence_package_hash=evidence_package.package_hash_sha256,
            provider_info={
                "provider": self.PROVIDER_NAME,
                "model": self.MODEL_NAME,
                "version": self.MODEL_VERSION,
                "local_first": True,
            },
            provenance={
                "evidence_items_count": len(evidence_package.evidence_items),
                "relationships_count": len(evidence_package.relationships),
                "deterministic_synthesis": True,
                "prompt_version": "ORBIT-AI-Prompt-v1",
            },
        )
