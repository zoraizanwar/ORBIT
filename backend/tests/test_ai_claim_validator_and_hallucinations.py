from app.services.ai.models import (
    Claim,
    ClaimType,
    SupportStatus,
)
from app.services.ai.evidence_retriever import EvidenceRetriever
from app.services.ai.claim_validator import ClaimValidator


def test_claim_validator_accepts_grounded_claims():
    pkg = EvidenceRetriever.get_seed_evidence_package(aoi_id="aoi-sinop")

    claims = [
        Claim(
            claim_id="c1",
            claim_text="Canopy vegetation deficit of -0.24 was calculated from telemetry.",
            claim_type=ClaimType.CHANGE,
            evidence_ids=["ev-ndvi-delta"],
            epistemic_level="AI_INTERPRETED",
        ),
        Claim(
            claim_id="c2",
            claim_text="The affected area spans 6.85 km2 situated within 85.0 meters of Highway BR-163.",
            claim_type=ClaimType.MEASUREMENT,
            evidence_ids=["ev-change-mask", "ev-road-corridor"],
            epistemic_level="AI_INTERPRETED",
        ),
    ]

    validated, is_all_valid = ClaimValidator.validate_claims(pkg, claims)
    assert is_all_valid is True
    assert len(validated) == 2
    assert validated[0].support_status == SupportStatus.SUPPORTED
    assert validated[1].support_status == SupportStatus.SUPPORTED


def test_claim_validator_rejects_missing_or_invalid_evidence_ids():
    pkg = EvidenceRetriever.get_seed_evidence_package(aoi_id="aoi-sinop")

    claims = [
        Claim(
            claim_id="c-no-id",
            claim_text="Vegetation is declining rapidly.",
            claim_type=ClaimType.CHANGE,
            evidence_ids=[],  # No evidence cited
            epistemic_level="AI_INTERPRETED",
        ),
        Claim(
            claim_id="c-fake-id",
            claim_text="Vegetation is declining rapidly.",
            claim_type=ClaimType.CHANGE,
            evidence_ids=["non-existent-evidence-id-999"],  # Fake evidence cited
            epistemic_level="AI_INTERPRETED",
        ),
    ]

    validated, is_all_valid = ClaimValidator.validate_claims(pkg, claims)
    assert is_all_valid is False
    assert validated[0].support_status == SupportStatus.UNSUPPORTED
    assert validated[1].support_status == SupportStatus.UNSUPPORTED


def test_claim_validator_rejects_numerical_hallucination():
    pkg = EvidenceRetriever.get_seed_evidence_package(aoi_id="aoi-sinop")

    # Evidence has -0.24 and +0.18. Claim invents -0.89!
    claims = [
        Claim(
            claim_id="c-hallucinated-num",
            claim_text="NDVI experienced a catastrophic collapse of -0.89 across the perimeter.",
            claim_type=ClaimType.CHANGE,
            evidence_ids=["ev-ndvi-delta"],
            epistemic_level="AI_INTERPRETED",
        )
    ]

    validated, is_all_valid = ClaimValidator.validate_claims(pkg, claims)
    assert is_all_valid is False
    assert validated[0].support_status == SupportStatus.UNSUPPORTED
    assert any("UNGROUNDED_NUMERIC_VALUE" in v for v in validated[0].validation_details["violations"])


def test_claim_validator_rejects_date_hallucination():
    pkg = EvidenceRetriever.get_seed_evidence_package(aoi_id="aoi-sinop")

    # Evidence timeline is 2023–2026, with forecast 2030. Claim invents year 2048!
    claims = [
        Claim(
            claim_id="c-hallucinated-date",
            claim_text="Historical clear-cutting began in 2048 according to telemetry.",
            claim_type=ClaimType.CHANGE,
            evidence_ids=["ev-ndvi-delta"],
            epistemic_level="AI_INTERPRETED",
        )
    ]

    validated, is_all_valid = ClaimValidator.validate_claims(pkg, claims)
    assert is_all_valid is False
    assert validated[0].support_status == SupportStatus.UNSUPPORTED


def test_claim_validator_detects_contradiction_and_flags():
    pkg = EvidenceRetriever.get_seed_evidence_package(
        aoi_id="aoi-sinop",
        include_contradiction=True,
    )

    claims = [
        Claim(
            claim_id="c-contradicted",
            claim_text="Canopy loss is unequivocally confirmed by optical telemetry.",
            claim_type=ClaimType.CHANGE,
            evidence_ids=["ev-ndvi-delta"],
            epistemic_level="AI_INTERPRETED",
        )
    ]

    validated, _ = ClaimValidator.validate_claims(pkg, claims)
    assert validated[0].support_status == SupportStatus.CONTRADICTED
    assert validated[0].confidence == 0.50
