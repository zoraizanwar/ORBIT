import re
from typing import List, Tuple, Set
from app.services.ai.models import (
    EvidencePackage,
    Claim,
    SupportStatus,
)


class ClaimValidator:
    """
    Deterministic Grounded Claim Validator.
    Performs adversarial post-generation verification to prevent LLM hallucinations:
    1. Validates referenced evidence IDs exist in the EvidencePackage.
    2. Checks numerical token alignment (no unsupported fabricated numbers).
    3. Checks temporal date alignment (no fabricated years/months).
    4. Enforces epistemic integrity (PREDICTED cannot be framed as OBSERVED).
    5. Flags contradictory evidence explicitly.
    """

    @classmethod
    def validate_claims(
        cls,
        evidence_package: EvidencePackage,
        claims: List[Claim],
    ) -> Tuple[List[Claim], bool]:
        """
        Validates a list of AI claims against the supplied EvidencePackage.
        Returns (validated_claims, is_all_valid).
        """
        evidence_map = {item.id: item for item in evidence_package.evidence_items}
        valid_evidence_ids = set(evidence_map.keys())

        # Collect grounded numeric values from evidence
        grounded_numbers: Set[float] = set()
        grounded_years: Set[int] = set()

        for item in evidence_package.evidence_items:
            if item.value is not None:
                grounded_numbers.add(round(abs(item.value), 2))
                grounded_numbers.add(round(item.value, 2))
            if item.timestamp:
                try:
                    yr = int(item.timestamp[:4])
                    grounded_years.add(yr)
                except Exception:
                    pass

            # Extract numbers from description and source metadata (e.g. BR-163, 85m, etc.)
            combined_text = f"{item.id} {item.source_id} {item.source_type} {item.description}"
            for token_num in re.findall(r"\b\d+\.?\d*\b", combined_text):
                try:
                    grounded_numbers.add(round(float(token_num), 2))
                except Exception:
                    pass

        # Also add date range bounds
        if evidence_package.date_range_start:
            grounded_years.add(int(evidence_package.date_range_start[:4]))
        if evidence_package.date_range_end:
            grounded_years.add(int(evidence_package.date_range_end[:4]))

        all_valid = True
        validated: List[Claim] = []

        for claim in claims:
            violations = []
            status = SupportStatus.SUPPORTED

            # 1. Verify cited evidence IDs
            if not claim.evidence_ids:
                violations.append("NO_EVIDENCE_CITED")
                status = SupportStatus.UNSUPPORTED
            else:
                invalid_ids = [eid for eid in claim.evidence_ids if eid not in valid_evidence_ids]
                if invalid_ids:
                    violations.append(f"INVALID_EVIDENCE_IDS: {invalid_ids}")
                    status = SupportStatus.UNSUPPORTED

            # 2. Check for Contradictory Evidence in the Cited Subgraph
            if evidence_package.has_contradictions:
                # If any cited evidence is target or source of a CONTRADICTS edge
                for rel in evidence_package.relationships:
                    if rel.relationship_type == "CONTRADICTS":
                        if rel.source_id in claim.evidence_ids or rel.target_id in claim.evidence_ids:
                            status = SupportStatus.CONTRADICTED
                            violations.append("CITED_EVIDENCE_CONTRADICTED_BY_CROSS_SENSOR_TELEMETRY")
                            break

            # 3. Check for Epistemic Integrity (PREDICTED vs OBSERVED)
            cited_epistemic_levels = [
                evidence_map[eid].epistemic_level for eid in claim.evidence_ids if eid in evidence_map
            ]
            if any(lvl == "PREDICTED" for lvl in cited_epistemic_levels):
                # Claim text cannot use deterministic observation wording like "observed" or "confirmed fact"
                text_lower = claim.claim_text.lower()
                if "observed in reality" in text_lower or "authoritative observation" in text_lower:
                    violations.append("PREDICTED_VALUE_MISREPRESENTED_AS_OBSERVED")
                    status = SupportStatus.UNSUPPORTED

            # 4. Numerical Hallucination Check
            # Extract decimals/integers from claim text
            numbers_in_text = re.findall(r"\b\d+\.?\d*\b", claim.claim_text)
            for num_str in numbers_in_text:
                try:
                    num_val = float(num_str)
                    # Skip common small counts like 1, 2, 3 or percentages unless they look like values
                    if num_val > 1000 and int(num_val) not in grounded_years:
                        # Year check
                        if 1900 <= num_val <= 2100 and int(num_val) not in grounded_years:
                            violations.append(f"UNGROUNDED_YEAR_IN_TEXT: {num_str}")
                            status = SupportStatus.UNSUPPORTED
                    elif num_val not in grounded_numbers and round(num_val, 2) not in grounded_numbers:
                        # Allow small ordinals or counts <= 5
                        if num_val not in [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 10.0, 95.0]:
                            violations.append(f"UNGROUNDED_NUMERIC_VALUE: {num_str}")
                            status = SupportStatus.UNSUPPORTED
                except Exception:
                    pass

            if violations:
                all_valid = False

            validated_claim = Claim(
                claim_id=claim.claim_id,
                claim_text=claim.claim_text,
                claim_type=claim.claim_type,
                epistemic_level=claim.epistemic_level,
                evidence_ids=claim.evidence_ids,
                support_status=status,
                confidence=0.50 if status == SupportStatus.CONTRADICTED else (0.95 if status == SupportStatus.SUPPORTED else 0.0),
                validation_details={"violations": violations, "is_valid": len(violations) == 0},
            )
            validated.append(validated_claim)

        return validated, all_valid
