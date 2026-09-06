from datetime import datetime, timezone
import pytest
from app.models.enums import EpistemicLevel, EvidenceStrength
from app.services.intelligence.models import (
    IntelligenceType,
    RuleEvaluationInput,
    SpatialContextResult,
    TemporalContextResult,
)
from app.services.intelligence.rule_engine import DeterministicRuleEngine


def test_rule_multi_indicator_urban_expansion():
    payload = RuleEvaluationInput(
        aoi_id="aoi-001",
        aoi_geometry={
            "type": "Polygon",
            "coordinates": [[[-54.7, -11.5], [-54.6, -11.5], [-54.6, -11.4], [-54.7, -11.4], [-54.7, -11.5]]],
        },
        target_start_date=datetime(2023, 7, 15, tzinfo=timezone.utc),
        target_end_date=datetime(2026, 7, 18, tzinfo=timezone.utc),
        ndvi_delta=-0.22,
        ndbi_delta=0.18,
        affected_area_km2=6.85,
    )
    spatial_ctx = SpatialContextResult(
        nearby_roads_count=0,
        intersects_road_corridor=False,
    )
    temporal_ctx = TemporalContextResult(
        start_date=payload.target_start_date,
        end_date=payload.target_end_date,
        interval_days=1099,
        temporal_alignment="AUTHORITATIVE_INTERVAL",
    )

    res = DeterministicRuleEngine.evaluate_rules(
        payload=payload,
        spatial_context=spatial_ctx,
        temporal_context=temporal_ctx,
        analysis_run_id="run-001",
    )

    assert res.intelligence_type == IntelligenceType.URBAN_EXPANSION
    assert res.rule_id == "RULE_MULTI_URBAN_EXPANSION_v1"
    assert res.evidence_strength == EvidenceStrength.STRONG
    assert res.epistemic_level == EpistemicLevel.CALCULATED
    assert len(res.evidence_graph.nodes) >= 3  # Root + NDVI + NDBI
    assert res.evidence_graph.has_contradictions is False


def test_rule_road_corridor_clearing():
    payload = RuleEvaluationInput(
        aoi_id="aoi-001",
        aoi_geometry={
            "type": "Polygon",
            "coordinates": [[[-54.7, -11.5], [-54.6, -11.5], [-54.6, -11.4], [-54.7, -11.4], [-54.7, -11.5]]],
        },
        target_start_date=datetime(2023, 7, 15, tzinfo=timezone.utc),
        target_end_date=datetime(2026, 7, 18, tzinfo=timezone.utc),
        ndvi_delta=-0.18,
        ndbi_delta=0.02,  # No NDBI rise
        affected_area_km2=2.15,
    )
    spatial_ctx = SpatialContextResult(
        nearby_roads_count=1,
        closest_road_name="Highway BR-163",
        closest_road_class="primary",
        distance_to_closest_road_m=120.0,
        intersects_road_corridor=True,
    )
    temporal_ctx = TemporalContextResult(
        start_date=payload.target_start_date,
        end_date=payload.target_end_date,
        interval_days=1099,
        temporal_alignment="AUTHORITATIVE_INTERVAL",
    )

    res = DeterministicRuleEngine.evaluate_rules(
        payload=payload,
        spatial_context=spatial_ctx,
        temporal_context=temporal_ctx,
        analysis_run_id="run-001",
    )

    assert res.intelligence_type == IntelligenceType.INFRASTRUCTURE_CHANGE
    assert res.rule_id == "RULE_INFRASTRUCTURE_CORRIDOR_v1"
    assert res.spatial_context.intersects_road_corridor is True


def test_rule_water_recession():
    payload = RuleEvaluationInput(
        aoi_geometry={"type": "Polygon", "coordinates": [[[-54.7, -11.5], [-54.6, -11.5], [-54.6, -11.4], [-54.7, -11.4], [-54.7, -11.5]]]},
        target_start_date=datetime(2023, 7, 15, tzinfo=timezone.utc),
        target_end_date=datetime(2026, 7, 18, tzinfo=timezone.utc),
        ndwi_delta=-0.25,
        affected_area_km2=8.40,
    )
    spatial_ctx = SpatialContextResult()
    temporal_ctx = TemporalContextResult(
        start_date=payload.target_start_date,
        end_date=payload.target_end_date,
        interval_days=1099,
        temporal_alignment="AUTHORITATIVE_INTERVAL",
    )

    res = DeterministicRuleEngine.evaluate_rules(
        payload=payload,
        spatial_context=spatial_ctx,
        temporal_context=temporal_ctx,
        analysis_run_id="run-001",
    )

    assert res.intelligence_type == IntelligenceType.WATER_CHANGE
    assert "Recession" in res.title


def test_contradictory_evidence_detection():
    # Optical shows significant vegetation loss (-0.25), but SAR backscatter indicates growth (+0.12)
    payload = RuleEvaluationInput(
        aoi_geometry={"type": "Polygon", "coordinates": [[[-54.7, -11.5], [-54.6, -11.5], [-54.6, -11.4], [-54.7, -11.4], [-54.7, -11.5]]]},
        target_start_date=datetime(2023, 7, 15, tzinfo=timezone.utc),
        target_end_date=datetime(2026, 7, 18, tzinfo=timezone.utc),
        ndvi_delta=-0.25,
        primary_sensor="Sentinel-2",
        secondary_sensor="Sentinel-1 SAR C-Band",
        secondary_sensor_signal_delta=0.12,
        affected_area_km2=5.0,
    )
    spatial_ctx = SpatialContextResult()
    temporal_ctx = TemporalContextResult(
        start_date=payload.target_start_date,
        end_date=payload.target_end_date,
        interval_days=1099,
        temporal_alignment="AUTHORITATIVE_INTERVAL",
    )

    res = DeterministicRuleEngine.evaluate_rules(
        payload=payload,
        spatial_context=spatial_ctx,
        temporal_context=temporal_ctx,
        analysis_run_id="run-001",
    )

    assert res.status == "CONTRADICTED"
    assert res.evidence_graph.has_contradictions is True
    assert res.evidence_strength == EvidenceStrength.INSUFFICIENT
    assert res.evidence_graph.contradiction_count == 1
