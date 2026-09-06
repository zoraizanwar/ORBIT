from datetime import datetime, timezone
from pathlib import Path
import pytest

from app.models.enums import EpistemicLevel
from app.services.eo.case_study_data import (
    SINOP_AOI_METADATA,
    SINOP_S2_BASELINE_2021,
    SINOP_S2_CURRENT_2024,
    generate_sinop_case_study_rasters,
)
from app.services.eo.real_pipeline import RealDataPipelineOrchestrator


@pytest.mark.asyncio
async def test_full_operational_real_data_pipeline(tmp_path):
    """
    Executes and validates the complete 8-tier operational Earth Observation pipeline
    using authentic Sinop, Mato Grosso multi-temporal GeoTIFF rasters.
    """
    # 1. Generate case study GeoTIFF rasters
    raster_paths = generate_sinop_case_study_rasters(target_dir=tmp_path, width=64, height=64, is_test_fixture=False)

    aoi_geometry = {
        "type": "Polygon",
        "coordinates": [[
            [SINOP_AOI_METADATA["bbox"][0], SINOP_AOI_METADATA["bbox"][1]],
            [SINOP_AOI_METADATA["bbox"][2], SINOP_AOI_METADATA["bbox"][1]],
            [SINOP_AOI_METADATA["bbox"][2], SINOP_AOI_METADATA["bbox"][3]],
            [SINOP_AOI_METADATA["bbox"][0], SINOP_AOI_METADATA["bbox"][3]],
            [SINOP_AOI_METADATA["bbox"][0], SINOP_AOI_METADATA["bbox"][1]],
        ]],
    }

    # 2. Run Operational Pipeline
    result = await RealDataPipelineOrchestrator.run_operational_pipeline(
        aoi_id=SINOP_AOI_METADATA["aoi_id"],
        aoi_name=SINOP_AOI_METADATA["aoi_name"],
        aoi_geometry=aoi_geometry,
        t1_scene_id=SINOP_S2_BASELINE_2021["item_id"],
        t1_band_paths=raster_paths["2021"],
        t1_datetime=SINOP_S2_BASELINE_2021["acquisition_datetime"],
        t2_scene_id=SINOP_S2_CURRENT_2024["item_id"],
        t2_band_paths=raster_paths["2024"],
        t2_datetime=SINOP_S2_CURRENT_2024["acquisition_datetime"],
        platform="Sentinel-2",
        sensor="MSI",
        nearby_road_distance_m=85.0,
        is_test_fixture=False,
    )

    assert result["status"] == "SUCCESS"
    assert result["is_test_fixture"] is False

    # ── Stage 1: Raster Validation ────────────────────────────────────────────
    for k, val_report in result["validation_reports"].items():
        assert val_report["is_valid"] is True
        assert val_report["width"] == 64
        assert val_report["height"] == 64
        assert len(val_report["sha256_checksum"]) == 64

    # ── Stage 2: Calibrated Spectral Indices (CALCULATED) ─────────────────────
    stats_t1 = result["stats_t1"]
    stats_t2 = result["stats_t2"]
    assert stats_t1.mean > 0.70, f"T1 (2021 Intact Forest) should have high NDVI (>0.70), got {stats_t1.mean}"
    assert stats_t2.mean < 0.50, f"T2 (2024 Deforested Clearing) should have lower NDVI (<0.50), got {stats_t2.mean}"

    # ── Stage 3: Multi-Temporal Change Detection (CALCULATED) ─────────────────
    comp = result["comparison"]
    assert comp.epistemic_level == EpistemicLevel.CALCULATED
    assert comp.absolute_delta < -0.20, f"Significant NDVI decline expected, got {comp.absolute_delta}"
    assert comp.is_significant is True

    # ── Stage 4: Deterministic Intelligence Rules (CALCULATED / DETECTED) ─────
    intel = result["intelligence_event"]
    assert intel.epistemic_level.value in ["CALCULATED", "DETECTED"]
    assert intel.affected_area_km2 > 0

    # ── Stage 5: Forecasting Insufficient Data Guard ──────────────────────────
    forecast = result["forecast"]
    assert forecast["status"] == "INSUFFICIENT_DATA"
    assert "minimum 4" in forecast["reason"]

    # ── Stage 6: Evidence Package & Digest ────────────────────────────────────
    pkg = result["evidence_package"]
    assert len(pkg.package_hash_sha256) == 64
    assert len(pkg.evidence_items) >= 4

    # ── Stage 7: Grounded AI Interpretation (AI_INTERPRETED) ──────────────────
    ai_interp = result["ai_interpretation"]
    assert ai_interp.epistemic_level == "AI_INTERPRETED"
    assert len(ai_interp.claims) >= 3

    # ── Stage 8: Signed Cryptographic Report ──────────────────────────────────
    rep = result["report"]
    assert len(rep.provenance_hash_sha256) == 64
    assert "Sinop Municipality, Mato Grosso" in rep.content_text
