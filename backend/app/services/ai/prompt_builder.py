import re
from typing import Dict, Any
from app.services.ai.models import EvidencePackage, AIInterpretationType


class PromptBuilder:
    """
    Sanitized, Grounded Prompt Builder.
    Constructs deterministic system and user prompts constraining LLM synthesis
    strictly to supplied EvidencePackage items.
    """

    SYSTEM_PROMPT = """You are the ORBIT Earth Intelligence Grounded Reasoner.
Your task is to synthesize and explain geospatial telemetry strictly from the provided Evidence Package.

HARD INVARIANTS:
1. Grounded Invariant: Never invent, extrapolate, or mention any numbers, dates, coordinates, or sensors not in the evidence.
2. Epistemic Separation: Distinguish OBSERVED (raw telemetry), CALCULATED (spectral indices/masks), DETECTED (events), PREDICTED (future forecasts), and AI_INTERPRETED (your explanatory synthesis).
3. Contradiction Invariant: If evidence contains a CONTRADICTS edge, explicitly highlight the conflicting signals and declare evidence strength limited.
4. Citation Invariant: Every claim must cite the exact evidence IDs [e.g. ev-ndvi-delta] supporting it.
5. Insufficient Data: If evidence is missing, state 'Insufficient evidence available.'

Output format must strictly conform to JSON structured interpretation."""

    @classmethod
    def sanitize_input(cls, text: str) -> str:
        """Strips injection characters and dangerous tokens."""
        if not text:
            return ""
        # Remove system control sequences and delimiter hacking
        cleaned = re.sub(r"[<>{}\[\]\x00-\x1F\x7F]", "", text)
        return cleaned.strip()[:500]

    @classmethod
    def build_prompt(
        cls,
        evidence_package: EvidencePackage,
        interpretation_type: AIInterpretationType,
        user_query: str = "",
    ) -> Dict[str, Any]:
        evidence_summary_lines = []
        for item in evidence_package.evidence_items:
            val_str = f" Value={item.value} {item.unit or ''}" if item.value is not None else ""
            ts_str = f" Timestamp={item.timestamp}" if item.timestamp else ""
            evidence_summary_lines.append(
                f"- [ID: {item.id}] Type={item.type} Epistemic={item.epistemic_level}{val_str}{ts_str} Source={item.source_id} Description: {item.description}"
            )

        relationship_lines = []
        for rel in evidence_package.relationships:
            desc = f" ({rel.description})" if rel.description else ""
            relationship_lines.append(
                f"- {rel.source_id} --[{rel.relationship_type}]--> {rel.target_id}{desc}"
            )

        user_content = f"""EVIDENCE PACKAGE FOR AREA OF INTEREST: {evidence_package.aoi_name} (ID: {evidence_package.aoi_id})
Package Hash: {evidence_package.package_hash_sha256}
Contradictions Present: {evidence_package.has_contradictions} (Count: {evidence_package.contradiction_count})

EVIDENCE ITEMS:
{chr(10).join(evidence_summary_lines)}

EVIDENCE RELATIONSHIPS:
{chr(10).join(relationship_lines) if relationship_lines else "None explicitly registered"}

TASK: Generate a {interpretation_type.value} grounded synthesis.
User Query / Focus: {cls.sanitize_input(user_query) if user_query else "Comprehensive synthesis of detected dynamics."}
"""

        return {
            "system_prompt": cls.SYSTEM_PROMPT,
            "user_prompt": user_content,
            "package_hash": evidence_package.package_hash_sha256,
        }
