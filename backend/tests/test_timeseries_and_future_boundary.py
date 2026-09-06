from datetime import datetime, timezone
import pytest
from app.models.enums import EpistemicLevel
from app.services.eo.timeseries.models import (
    TimePointMeasurement,
    FuturePredictionForecastContract,
)
from app.services.eo.timeseries.series_builder import build_temporal_series


def test_build_temporal_series_ordering_and_gaps():
    pts = [
        TimePointMeasurement(
            acquisition_datetime=datetime(2025, 6, 1, tzinfo=timezone.utc),
            metric_name="NDVI_MEAN",
            value=0.62,
            unit="index_value",
            source_scene_id="S2_20250601",
            platform="Sentinel-2B",
            sensor="MSI",
            cloud_cover=5.0,
        ),
        TimePointMeasurement(
            acquisition_datetime=datetime(2025, 1, 15, tzinfo=timezone.utc),
            metric_name="NDVI_MEAN",
            value=0.45,
            unit="index_value",
            source_scene_id="S2_20250115",
            platform="Sentinel-2A",
            sensor="MSI",
            cloud_cover=12.0,
        ),
        TimePointMeasurement(
            acquisition_datetime=datetime(2026, 1, 10, tzinfo=timezone.utc),
            metric_name="NDVI_MEAN",
            value=0.50,
            unit="index_value",
            source_scene_id="S2_20260110",
            platform="Sentinel-2B",
            sensor="MSI",
            cloud_cover=8.0,
        ),
    ]

    series = build_temporal_series(pts, aoi_id="aoi-001", aoi_name="Mato Grosso", gap_threshold_days=60)

    # 1. Must be sorted chronologically
    assert len(series.data_points) == 3
    assert series.data_points[0].acquisition_datetime == datetime(2025, 1, 15, tzinfo=timezone.utc)
    assert series.data_points[1].acquisition_datetime == datetime(2025, 6, 1, tzinfo=timezone.utc)
    assert series.data_points[2].acquisition_datetime == datetime(2026, 1, 10, tzinfo=timezone.utc)

    # 2. Observation gaps detected
    assert len(series.observation_gaps) >= 1
    assert series.observation_gaps[0].duration_days > 60

    # 3. Epistemic level
    assert series.epistemic_level == EpistemicLevel.CALCULATED


def test_future_prediction_forecast_contract_invariants():
    """
    Verifies that the contract for future predictions requires target_year > training_end_year,
    scenario, model version, and epistemic level PREDICTED.
    """
    pts = [
        TimePointMeasurement(
            acquisition_datetime=datetime(2024, 6, 1, tzinfo=timezone.utc),
            metric_name="NDVI_MEAN",
            value=0.55,
            unit="index_value",
            source_scene_id="S2_2024",
            platform="Sentinel-2A",
            sensor="MSI",
        )
    ]

    contract = FuturePredictionForecastContract(
        aoi_id="aoi-amazon-01",
        target_year=2035,
        scenario_name="SSP2-4.5_BUSINESS_AS_USUAL",
        metric_target="NDVI_MEAN",
        training_start_year=2000,
        training_end_year=2026,
        historical_baseline_points=pts,
        forecast_model_name="ARIMA_Seasonal_Vegetation",
        forecast_model_version="1.0.0",
        epistemic_level=EpistemicLevel.PREDICTED,
    )

    assert contract.target_year > contract.training_end_year
    assert contract.target_year == 2035
    assert contract.epistemic_level == EpistemicLevel.PREDICTED
    assert contract.scenario_name == "SSP2-4.5_BUSINESS_AS_USUAL"
