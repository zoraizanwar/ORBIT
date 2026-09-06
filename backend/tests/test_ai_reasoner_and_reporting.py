from app.services.ai.models import (
    InterpretRequestPayload,
    ReportRequestPayload,
    ReportFormat,
    AIInterpretationType,
)
from app.services.ai.grounded_reasoner import GroundedReasoner
from app.services.ai.report_generator import ReportGenerator


def test_grounded_reasoner_synthesis():
    payload = InterpretRequestPayload(
        aoi_id="aoi-sinop-mato-grosso",
        interpretation_type=AIInterpretationType.URBAN_EXPANSION_SYNTHESIS,
        user_prompt="Analyze canopy deficit and urban growth dynamics",
    )

    result = GroundedReasoner.interpret(payload)

    assert result.aoi_id == "aoi-sinop-mato-grosso"
    assert result.epistemic_level == "AI_INTERPRETED"
    assert len(result.claims) >= 3
    assert len(result.recommendations) >= 1
    assert result.evidence_package_hash is not None
    assert "provenance_hash_sha256" in result.provenance

    # Verify claim grounding
    for claim in result.claims:
        assert claim.epistemic_level == "AI_INTERPRETED"
        assert len(claim.evidence_ids) > 0


def test_report_generator_markdown_output():
    report_payload = ReportRequestPayload(
        aoi_id="aoi-sinop-mato-grosso",
        title="Sinop Geospatial Intelligence & Grounding Assessment",
        report_format=ReportFormat.MARKDOWN,
    )

    report = ReportGenerator.generate_report(report_payload)

    assert report.aoi_id == "aoi-sinop-mato-grosso"
    assert report.report_format == ReportFormat.MARKDOWN
    assert len(report.provenance_hash_sha256) == 64
    assert "# ORBIT GEOSPATIAL INTELLIGENCE REPORT" in report.content_text
    assert "## 1. Executive Summary" in report.content_text
    assert "## 2. Epistemic Hierarchy" in report.content_text
    assert "## 3. Grounded Evidence Claims" in report.content_text
    assert "## 7. Decision Support" in report.content_text
    assert "## 9. Grounded Evidence Inventory" in report.content_text
