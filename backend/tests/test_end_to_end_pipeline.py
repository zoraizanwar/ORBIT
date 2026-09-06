"""
ORBIT End-to-End Pipeline Integration Test

Tests the complete intelligence pipeline from synthetic raster inputs
to cryptographically signed intelligence report.

All data used here is explicitly labeled as TEST FIXTURE / SIMULATED.
None of it is real satellite telemetry.
"""

from app.services.pipeline_orchestrator import EndToEndPipelineOrchestrator
from app.services.forecasting.models import ForecastStatus


def test_full_end_to_end_intelligence_pipeline():
    """Verifies that all 8 pipeline stages run successfully and carry provenance end-to-end."""
    result = EndToEndPipelineOrchestrator.run_full_pipeline(
        aoi_id="aoi-sinop-e2e-test",
        aoi_name="Sinop E2E Verification [TEST FIXTURE - SIMULATED]",
    )

    assert result["status"] == "SUCCESS"
    assert result["is_test_fixture"] is True

    # ── Stage 1 & 2: Lifecycle tracking + NDVI stats ──────────────────────────
    lifecycle = result["lifecycle"]
    assert lifecycle["status"] == "COMPLETED"
    assert lifecycle["duration_ms"] > 0
    assert "metrics" in lifecycle
    assert lifecycle["metrics"]["is_test_fixture"] is True

    stats_t1 = result["stats_t1"]
    stats_t2 = result["stats_t2"]
    assert stats_t1.mean > stats_t2.mean, "NDVI should decline between T1 and T2"

    # ── Stage 3: Temporal comparison (CALCULATED) ─────────────────────────────
    comp = result["comparison"]
    assert comp.epistemic_level.value == "CALCULATED"
    assert comp.absolute_delta < 0.0, "NDVI decline should be negative"
    assert comp.is_significant is True

    # ── Stage 4: Intelligence rule evaluation (CALCULATED / DETECTED) ────────
    intel_event = result["intelligence_event"]
    # DeterministicRuleEngine returns IntelligenceObjectResult with CALCULATED epistemic level
    # (rule-based deterministic inference is classified as CALCULATED in ORBIT Phase 11)
    assert intel_event.epistemic_level.value in ["CALCULATED", "DETECTED"]
    assert intel_event.evidence_strength is not None
    assert intel_event.intelligence_type is not None

    # ── Stage 5: Forecast (PREDICTED) ─────────────────────────────────────────
    forecast = result["forecast"]
    assert forecast.status.value in ["SUCCESS", "COMPLETED"]
    assert len(forecast.predictions) == 4
    for pt in forecast.predictions:
        assert pt.epistemic_level.value == "PREDICTED"
    assert forecast.predictions[-1].target_year == 2030

    # ── Stage 6: Evidence package & SHA-256 cryptographic digest ──────────────
    pkg = result["evidence_package"]
    assert len(pkg.package_hash_sha256) == 64
    assert len(pkg.evidence_items) >= 5
    # All scene evidence must remain OBSERVED — never upgraded
    for item in pkg.evidence_items:
        if item.type == "SCENE":
            assert item.epistemic_level.value == "OBSERVED"
        if item.type == "FORECAST_PROJECTION":
            assert item.epistemic_level.value == "PREDICTED"

    # ── Stage 7: AI interpretation (AI_INTERPRETED) ────────────────────────────
    ai_interp = result["ai_interpretation"]
    assert ai_interp.epistemic_level == "AI_INTERPRETED"
    assert len(ai_interp.claims) >= 3
    assert len(ai_interp.recommendations) >= 1
    assert "provenance_hash_sha256" in ai_interp.provenance

    # Test fixture label must never appear as a real scene claim
    for claim in ai_interp.claims:
        # AI must not report a CALCULATED value as OBSERVED
        assert claim.epistemic_level != "OBSERVED", (
            f"AI claim '{claim.claim_text[:60]}' illegally upgraded to OBSERVED"
        )

    # ── Stage 8: Signed intelligence report ───────────────────────────────────
    report = result["report"]
    assert report.report_format.value == "MARKDOWN"
    assert len(report.provenance_hash_sha256) == 64
    report_text = report.content_text
    assert "# ORBIT GEOSPATIAL INTELLIGENCE REPORT" in report_text
    assert "## 1. Executive Summary" in report_text
    assert "## 9. Grounded Evidence Inventory" in report_text

    # ── Provenance: Each run produces a unique hash (analysis_run_id varies) ──
    # The hash encodes evidence item IDs, types, values, AOI, and run ID.
    # Two different runs will have different hashes by design (different run IDs).
    # We verify the hash length and format, not exact equality across runs.
    assert len(pkg.package_hash_sha256) == 64, "SHA-256 must be 64 hex characters"
    assert all(c in "0123456789abcdef" for c in pkg.package_hash_sha256), "Hash must be lowercase hex"
