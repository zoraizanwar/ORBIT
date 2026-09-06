import hashlib
import json
from typing import Optional
from app.services.ai.exceptions import InsufficientEvidenceError
from app.services.ai.models import (
    EvidencePackage,
    AIInterpretationResult,
    InterpretRequestPayload,
)
from app.services.ai.evidence_retriever import EvidenceRetriever
from app.services.ai.prompt_builder import PromptBuilder
from app.services.ai.llm_provider import LocalDeterministicReasoner
from app.services.ai.claim_validator import ClaimValidator


class GroundedReasoner:
    """
    Unified ORBIT AI Intelligence Synthesis & Grounding Engine.
    Coordinates evidence retrieval, prompt security, LLM synthesis, adversarial claim validation,
    and cryptographic provenance sealing.
    """

    @classmethod
    def interpret(
        cls,
        payload: InterpretRequestPayload,
        evidence_package: Optional[EvidencePackage] = None,
    ) -> AIInterpretationResult:
        # 1. Retrieve or assemble evidence package
        pkg = evidence_package or EvidenceRetriever.get_seed_evidence_package(
            aoi_id=payload.aoi_id,
        )

        if not pkg.evidence_items:
            raise InsufficientEvidenceError(
                f"No grounded evidence found for Area of Interest {payload.aoi_id}.",
                required_types=["SCENE", "INDEX_MEASUREMENT"],
                available_types=[],
            )

        # 2. Build sanitized prompt
        prompts = PromptBuilder.build_prompt(
            evidence_package=pkg,
            interpretation_type=payload.interpretation_type,
            user_query=payload.user_prompt or "",
        )

        # 3. Generate structured synthesis via LocalDeterministicReasoner
        provider = LocalDeterministicReasoner()
        raw_result = provider.generate_interpretation(
            evidence_package=pkg,
            interpretation_type=payload.interpretation_type,
            system_prompt=prompts["system_prompt"],
            user_prompt=prompts["user_prompt"],
        )

        # 4. Strict Adversarial Claim Validation
        validated_claims, _ = ClaimValidator.validate_claims(
            evidence_package=pkg,
            claims=raw_result.claims,
        )
        raw_result.claims = validated_claims

        # 5. Attach cryptographic provenance digest
        prov_dict = {
            "interpretation_id": raw_result.id,
            "aoi_id": raw_result.aoi_id,
            "evidence_package_hash": pkg.package_hash_sha256,
            "claims_count": len(validated_claims),
            "contradictions_present": pkg.has_contradictions,
            "provider": raw_result.provider_info.get("provider"),
            "model": raw_result.provider_info.get("model"),
            "epistemic_level": "AI_INTERPRETED",
            "deterministic_pipeline": True,
            "hallucination_validation_passed": True,
        }
        prov_str = json.dumps(prov_dict, sort_keys=True)
        raw_result.provenance["provenance_hash_sha256"] = hashlib.sha256(prov_str.encode("utf-8")).hexdigest()

        return raw_result
