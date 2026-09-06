from datetime import datetime, timezone
import pytest
from app.models.enums import EpistemicLevel
from app.services.eo.change.exceptions import (
    IncompatibleMeasurementsError,
    IncompatibleSensorsError,
    IncompatibleUnitsError,
    TemporalOrderError,
)
from app.services.eo.change.models import TemporalObservationPair
from app.services.eo.change.temporal_comparator import TemporalComparator
from app.services.eo.change.thresholds import (
    ChangeMetric,
    ChangeClass,
    ChangeThresholdConfig,
)
from app.services.eo.timeseries.models import TimePointMeasurement


def test_temporal_comparison_valid_pair():
    m1 = TimePointMeasurement(
        acquisition_datetime=datetime(2024, 6, 1, tzinfo=timezone.utc),
        metric_name="NDVI_MEAN",
        value=0.42,
        unit="index_value",
        source_scene_id="S2A_20240601",
        platform="Sentinel-2A",
        sensor="MSI",
        cloud_cover=4.0,
    )
    m2 = TimePointMeasurement(
        acquisition_datetime=datetime(2026, 6, 1, tzinfo=timezone.utc),
        metric_name="NDVI_MEAN",
        value=0.61,
        unit="index_value",
        source_scene_id="S2B_20260601",
        platform="Sentinel-2B",
        sensor="MSI",
        cloud_cover=6.0,
    )

    pair = TemporalObservationPair(
        aoi_id="aoi-001",
        aoi_name="Test AOI",
        measurement_t1=m1,
        measurement_t2=m2,
    )

    res = TemporalComparator.compare_observations(pair)

    assert res.metric == ChangeMetric.NDVI
    assert res.absolute_delta == 0.19
    assert res.relative_change == pytest.approx(0.4524, rel=1e-3)
    assert res.percentage_change == pytest.approx(45.24, rel=1e-2)
    assert res.classification == ChangeClass.SIGNIFICANT_INCREASE
    assert res.is_significant is True
    assert res.interval_days == 730
    assert res.epistemic_level == EpistemicLevel.CALCULATED


def test_temporal_ordering_violation_raises_error():
    m1 = TimePointMeasurement(
        acquisition_datetime=datetime(2026, 1, 1, tzinfo=timezone.utc),
        metric_name="NDVI_MEAN",
        value=0.50,
        unit="index_value",
        source_scene_id="S2_01",
        platform="Sentinel-2A",
        sensor="MSI",
    )
    m2 = TimePointMeasurement(
        acquisition_datetime=datetime(2024, 1, 1, tzinfo=timezone.utc),
        metric_name="NDVI_MEAN",
        value=0.60,
        unit="index_value",
        source_scene_id="S2_02",
        platform="Sentinel-2B",
        sensor="MSI",
    )

    pair = TemporalObservationPair(measurement_t1=m1, measurement_t2=m2)
    with pytest.raises(TemporalOrderError):
        TemporalComparator.compare_observations(pair)


def test_mismatched_metrics_rejection():
    m1 = TimePointMeasurement(
        acquisition_datetime=datetime(2024, 1, 1, tzinfo=timezone.utc),
        metric_name="NDVI_MEAN",
        value=0.50,
        unit="index_value",
        source_scene_id="S2_01",
        platform="Sentinel-2A",
        sensor="MSI",
    )
    m2 = TimePointMeasurement(
        acquisition_datetime=datetime(2025, 1, 1, tzinfo=timezone.utc),
        metric_name="NDWI_MEAN",
        value=0.20,
        unit="index_value",
        source_scene_id="S2_02",
        platform="Sentinel-2B",
        sensor="MSI",
    )

    pair = TemporalObservationPair(measurement_t1=m1, measurement_t2=m2)
    with pytest.raises(IncompatibleMeasurementsError):
        TemporalComparator.compare_observations(pair)


def test_mismatched_units_rejection():
    m1 = TimePointMeasurement(
        acquisition_datetime=datetime(2024, 1, 1, tzinfo=timezone.utc),
        metric_name="VEGETATED_AREA",
        value=150.0,
        unit="km2",
        source_scene_id="S2_01",
        platform="Sentinel-2A",
        sensor="MSI",
    )
    m2 = TimePointMeasurement(
        acquisition_datetime=datetime(2025, 1, 1, tzinfo=timezone.utc),
        metric_name="VEGETATED_AREA",
        value=15000.0,
        unit="hectares",
        source_scene_id="S2_02",
        platform="Sentinel-2B",
        sensor="MSI",
    )

    pair = TemporalObservationPair(measurement_t1=m1, measurement_t2=m2)
    with pytest.raises(IncompatibleUnitsError):
        TemporalComparator.compare_observations(pair)


def test_sar_optical_cross_comparison_rejection():
    m1 = TimePointMeasurement(
        acquisition_datetime=datetime(2024, 1, 1, tzinfo=timezone.utc),
        metric_name="NDVI_MEAN",
        value=0.50,
        unit="index_value",
        source_scene_id="S2_01",
        platform="Sentinel-2A",
        sensor="MSI",
    )
    m2 = TimePointMeasurement(
        acquisition_datetime=datetime(2025, 1, 1, tzinfo=timezone.utc),
        metric_name="NDVI_MEAN",
        value=0.50,
        unit="index_value",
        source_scene_id="S1_01",
        platform="Sentinel-1A",
        sensor="C-SAR",
    )

    pair = TemporalObservationPair(measurement_t1=m1, measurement_t2=m2)
    with pytest.raises(IncompatibleSensorsError):
        TemporalComparator.compare_observations(pair)


def test_zero_denominator_safe_percentage_handling():
    m1 = TimePointMeasurement(
        acquisition_datetime=datetime(2024, 1, 1, tzinfo=timezone.utc),
        metric_name="NDVI_MEAN",
        value=0.0,
        unit="index_value",
        source_scene_id="S2_01",
        platform="Sentinel-2A",
        sensor="MSI",
    )
    m2 = TimePointMeasurement(
        acquisition_datetime=datetime(2025, 1, 1, tzinfo=timezone.utc),
        metric_name="NDVI_MEAN",
        value=0.35,
        unit="index_value",
        source_scene_id="S2_02",
        platform="Sentinel-2B",
        sensor="MSI",
    )

    pair = TemporalObservationPair(measurement_t1=m1, measurement_t2=m2)
    res = TemporalComparator.compare_observations(pair)

    assert res.absolute_delta == 0.35
    assert res.relative_change is None
    assert res.percentage_change is None
    assert res.classification == ChangeClass.SIGNIFICANT_INCREASE


def test_equal_timestamps_rejected():
    ts = datetime(2025, 5, 1, 12, 0, tzinfo=timezone.utc)
    m1 = TimePointMeasurement(
        acquisition_datetime=ts,
        metric_name="NDVI_MEAN",
        value=0.50,
        unit="index_value",
        source_scene_id="S2A_01",
        platform="Sentinel-2A",
        sensor="MSI",
    )
    m2 = TimePointMeasurement(
        acquisition_datetime=ts,
        metric_name="NDVI_MEAN",
        value=0.55,
        unit="index_value",
        source_scene_id="S2B_01",
        platform="Sentinel-2B",
        sensor="MSI",
    )
    pair = TemporalObservationPair(measurement_t1=m1, measurement_t2=m2)
    with pytest.raises(TemporalOrderError):
        TemporalComparator.compare_observations(pair)


def test_threshold_exact_boundaries():
    # Test boundary transitions:
    # default thresholds: sig_inc: 0.15, inc: 0.05, dec: -0.05, sig_dec: -0.15
    ts1 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    ts2 = datetime(2025, 1, 1, tzinfo=timezone.utc)

    # 1. Delta exactly +0.05 -> INCREASE
    m1 = TimePointMeasurement(acquisition_datetime=ts1, metric_name="NDVI", value=0.50, unit="index_value", source_scene_id="S1", platform="Sentinel-2A", sensor="MSI")
    m2 = TimePointMeasurement(acquisition_datetime=ts2, metric_name="NDVI", value=0.55, unit="index_value", source_scene_id="S2", platform="Sentinel-2B", sensor="MSI")
    res = TemporalComparator.compare_observations(TemporalObservationPair(measurement_t1=m1, measurement_t2=m2))
    assert res.classification == ChangeClass.INCREASE

    # 2. Delta exactly +0.15 -> SIGNIFICANT_INCREASE
    m3 = TimePointMeasurement(acquisition_datetime=ts2, metric_name="NDVI", value=0.65, unit="index_value", source_scene_id="S3", platform="Sentinel-2B", sensor="MSI")
    res = TemporalComparator.compare_observations(TemporalObservationPair(measurement_t1=m1, measurement_t2=m3))
    assert res.classification == ChangeClass.SIGNIFICANT_INCREASE

    # 3. Delta exactly -0.05 -> DECREASE
    m4 = TimePointMeasurement(acquisition_datetime=ts2, metric_name="NDVI", value=0.45, unit="index_value", source_scene_id="S4", platform="Sentinel-2B", sensor="MSI")
    res = TemporalComparator.compare_observations(TemporalObservationPair(measurement_t1=m1, measurement_t2=m4))
    assert res.classification == ChangeClass.DECREASE

    # 4. Delta exactly -0.15 -> SIGNIFICANT_DECREASE
    m5 = TimePointMeasurement(acquisition_datetime=ts2, metric_name="NDVI", value=0.35, unit="index_value", source_scene_id="S5", platform="Sentinel-2B", sensor="MSI")
    res = TemporalComparator.compare_observations(TemporalObservationPair(measurement_t1=m1, measurement_t2=m5))
    assert res.classification == ChangeClass.SIGNIFICANT_DECREASE

    # 5. Delta 0.0 -> NO_CHANGE
    m6 = TimePointMeasurement(acquisition_datetime=ts2, metric_name="NDVI", value=0.50, unit="index_value", source_scene_id="S6", platform="Sentinel-2B", sensor="MSI")
    res = TemporalComparator.compare_observations(TemporalObservationPair(measurement_t1=m1, measurement_t2=m6))
    assert res.classification == ChangeClass.NO_CHANGE

