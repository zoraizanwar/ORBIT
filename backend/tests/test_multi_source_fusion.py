import pytest
from datetime import datetime, timezone
from app.services.eo.fusion.models import (
    ObservationSource,
    ObservationMeasurement,
    AlignmentStatus,
    FusionRelationship,
    TemporalSeriesState,
)
from app.services.eo.fusion.alignment_service import (
    ObservationAlignmentService,
    TemporalWindowService,
    SpatialResolutionService,
)
from app.services.eo.fusion.multi_temporal_analyzer import MultiTemporalChangeAnalyzer
from app.services.eo.fusion.contradiction_engine import CrossSensorContradictionEngine
from app.services.eo.fusion.evidence_scorer import EvidenceFusionScorer
from app.services.eo.fusion.fusion_orchestrator import MultiSourceFusionOrchestrator
from app.models.enums import SensingModality


@pytest.fixture
def sample_optical_source_t1():
    return ObservationSource(
        id="obs-opt-2021",
        scene_id="S2B_MSIL2A_20210615T140051",
        catalog="Element84-AWS",
        collection="sentinel-2-l2a",
        platform="Sentinel-2B",
        sensor="MSI",
        modality=SensingModality.OPTICAL,
        acquisition_datetime=datetime(2021, 6, 15, 14, 0, 0, tzinfo=timezone.utc),
        geometry={"type": "Polygon", "coordinates": [[[-55.6, -11.9], [-55.4, -11.9], [-55.4, -11.8], [-55.6, -11.8], [-55.6, -11.9]]]},
        bbox=[-55.6, -11.9, -55.4, -11.8],
        gsd_meters=10.0,
        crs="EPSG:4326",
        cloud_cover=1.2,
        is_test_fixture=True,
    )


@pytest.fixture
def sample_optical_source_t2():
    return ObservationSource(
        id="obs-opt-2024",
        scene_id="S2A_MSIL2A_20240620T140101",
        catalog="Element84-AWS",
        collection="sentinel-2-l2a",
        platform="Sentinel-2A",
        sensor="MSI",
        modality=SensingModality.OPTICAL,
        acquisition_datetime=datetime(2024, 6, 20, 14, 1, 1, tzinfo=timezone.utc),
        geometry={"type": "Polygon", "coordinates": [[[-55.6, -11.9], [-55.4, -11.9], [-55.4, -11.8], [-55.6, -11.8], [-55.6, -11.9]]]},
        bbox=[-55.6, -11.9, -55.4, -11.8],
        gsd_meters=10.0,
        crs="EPSG:4326",
        cloud_cover=0.8,
        is_test_fixture=True,
    )


def test_temporal_window_service_calculations():
    t1 = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2024, 6, 8, 12, 0, 0, tzinfo=timezone.utc)
    t3 = datetime(2024, 7, 15, 12, 0, 0, tzinfo=timezone.utc)

    assert TemporalWindowService.calculate_offset_days(t1, t2) == 7.0
    assert TemporalWindowService.is_within_window(t1, t2, window_days=7.0) is True
    assert TemporalWindowService.is_within_window(t1, t2, window_days=6.9) is False
    assert TemporalWindowService.is_within_window(t1, t3, window_days=14.0) is False


def test_spatial_resolution_service():
    status, ratio, need_resample, _ = SpatialResolutionService.evaluate_resolution_compatibility(10.0, 10.0)
    assert status == "IDENTICAL"
    assert ratio == 1.0
    assert need_resample is False

    status, ratio, need_resample, method = SpatialResolutionService.evaluate_resolution_compatibility(10.0, 20.0)
    assert status == "COMPATIBLE"
    assert ratio == 2.0
    assert need_resample is True
    assert method == "BILINEAR_AREA_WEIGHTED"

    status, ratio, _, _ = SpatialResolutionService.evaluate_resolution_compatibility(10.0, 60.0)
    assert status == "MISMATCH"
    assert ratio == 6.0


def test_observation_alignment_service(sample_optical_source_t1, sample_optical_source_t2):
    # Same bbox, large temporal offset (3 years)
    report = ObservationAlignmentService.align_observations(
        source=sample_optical_source_t1,
        target=sample_optical_source_t2,
        temporal_window_days=1500.0,
    )
    assert report.status == AlignmentStatus.ALIGNED
    assert report.spatial_overlap_percentage == 100.0
    assert report.resolution_ratio == 1.0

    # Strict 14 days window should flag incompatible
    report_strict = ObservationAlignmentService.align_observations(
        source=sample_optical_source_t1,
        target=sample_optical_source_t2,
        temporal_window_days=14.0,
    )
    assert report_strict.status == AlignmentStatus.INCOMPATIBLE
    assert len(report_strict.reasons) > 0


def test_multi_temporal_change_analyzer_insufficient_data():
    meas_0 = []
    res_0 = MultiTemporalChangeAnalyzer.analyze_series("NDVI", meas_0)
    assert res_0.overall_state == TemporalSeriesState.INSUFFICIENT_DATA
    assert res_0.valid_observation_count == 0

    meas_1 = [
        ObservationMeasurement(
            observation_id="obs-1",
            metric="NDVI",
            value=0.82,
            timestamp=datetime(2021, 6, 15, tzinfo=timezone.utc),
        )
    ]
    res_1 = MultiTemporalChangeAnalyzer.analyze_series("NDVI", meas_1)
    assert res_1.overall_state == TemporalSeriesState.INSUFFICIENT_DATA


def test_multi_temporal_change_analyzer_persistence_and_recovery():
    # 1. Persistent Decrease (T1: 0.85 -> T2: 0.65 -> T3: 0.42)
    persistent_meas = [
        ObservationMeasurement(observation_id="obs-1", metric="NDVI", value=0.85, timestamp=datetime(2021, 6, 15, tzinfo=timezone.utc)),
        ObservationMeasurement(observation_id="obs-2", metric="NDVI", value=0.65, timestamp=datetime(2022, 6, 15, tzinfo=timezone.utc)),
        ObservationMeasurement(observation_id="obs-3", metric="NDVI", value=0.42, timestamp=datetime(2023, 6, 15, tzinfo=timezone.utc)),
    ]
    res_p = MultiTemporalChangeAnalyzer.analyze_series("NDVI", persistent_meas)
    assert res_p.overall_state == TemporalSeriesState.PERSISTENT_CHANGE
    assert res_p.net_absolute_delta == -0.43
    assert res_p.recovery_detected is False

    # 2. Recovery (T1: 0.85 -> T2: 0.40 -> T3: 0.78)
    recovery_meas = [
        ObservationMeasurement(observation_id="obs-1", metric="NDVI", value=0.85, timestamp=datetime(2021, 6, 15, tzinfo=timezone.utc)),
        ObservationMeasurement(observation_id="obs-2", metric="NDVI", value=0.40, timestamp=datetime(2022, 6, 15, tzinfo=timezone.utc)),
        ObservationMeasurement(observation_id="obs-3", metric="NDVI", value=0.78, timestamp=datetime(2023, 6, 15, tzinfo=timezone.utc)),
    ]
    res_r = MultiTemporalChangeAnalyzer.analyze_series("NDVI", recovery_meas)
    assert res_r.overall_state == TemporalSeriesState.RECOVERY
    assert res_r.recovery_detected is True


def test_cross_sensor_contradiction_engine():
    # 1. Contradiction: Optical decline vs SAR stable
    findings_1 = CrossSensorContradictionEngine.evaluate_cross_sensor_evidence(
        optical_measurements={"NDVI_DELTA": -0.38},
        sar_measurements={"VV_DELTA": 0.1, "VV_CURRENT": -8.5},
    )
    assert len(findings_1) == 1
    assert findings_1[0].relationship == FusionRelationship.CONTRADICTED
    assert "contradicted" in findings_1[0].explanation.lower()

    # 2. Corroboration: Optical decline + SAR roughness drop
    findings_2 = CrossSensorContradictionEngine.evaluate_cross_sensor_evidence(
        optical_measurements={"NDVI_DELTA": -0.38},
        sar_measurements={"VV_DELTA": -2.8, "VV_CURRENT": -14.5},
    )
    assert len(findings_2) == 1
    assert findings_2[0].relationship == FusionRelationship.CORROBORATED


def test_evidence_fusion_scorer():
    score_clean = EvidenceFusionScorer.calculate_evidence_score(
        valid_observation_count=4,
        mean_valid_pixel_pct=98.0,
        mean_cloud_cover_pct=2.0,
        mean_spatial_overlap_pct=95.0,
    )
    assert 0.70 <= score_clean.evidence_strength_score <= 1.0

    score_penalized = EvidenceFusionScorer.calculate_evidence_score(
        valid_observation_count=2,
        mean_valid_pixel_pct=70.0,
        mean_cloud_cover_pct=30.0,
        findings=[
            CrossSensorContradictionEngine.evaluate_cross_sensor_evidence(
                optical_measurements={"NDVI_DELTA": -0.40},
                sar_measurements={"VV_DELTA": 0.0},
            )[0]
        ],
    )
    assert score_penalized.evidence_strength_score < score_clean.evidence_strength_score
    assert score_penalized.contradiction_penalty > 0.0
