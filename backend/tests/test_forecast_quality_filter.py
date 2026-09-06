from datetime import datetime, timezone
import pytest
from app.models.enums import EpistemicLevel
from app.services.forecasting.models import (
    ForecastMetric,
    HistoricalObservation,
)
from app.services.forecasting.quality_filter import QualityFilterPipeline


def test_filter_nan_and_inf_values():
    observations = [
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=0.65,
            acquisition_datetime=datetime(2020, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=float("nan"),
            acquisition_datetime=datetime(2021, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=float("inf"),
            acquisition_datetime=datetime(2022, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=0.58,
            acquisition_datetime=datetime(2023, 7, 1, tzinfo=timezone.utc),
        ),
    ]

    accepted, report = QualityFilterPipeline.filter_observations(observations)
    assert len(accepted) == 2
    assert report.rejected_count == 2
    assert "NON_FINITE_OR_NAN_VALUE" in report.rejection_reasons


def test_filter_duplicate_timestamps():
    observations = [
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=0.62,
            acquisition_datetime=datetime(2020, 7, 1, 12, 0, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=0.63,
            acquisition_datetime=datetime(2020, 7, 1, 12, 0, tzinfo=timezone.utc),
        ),
    ]

    accepted, report = QualityFilterPipeline.filter_observations(observations)
    assert len(accepted) == 1
    assert report.rejected_count == 1
    assert "DUPLICATE_TIMESTAMP" in report.rejection_reasons


def test_filter_excessive_cloud_cover_and_sar_null_tolerance():
    observations = [
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=0.70,
            cloud_cover=12.0,
            acquisition_datetime=datetime(2020, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=0.60,
            cloud_cover=65.0,  # > 30% threshold
            acquisition_datetime=datetime(2021, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=0.68,
            sensor="Sentinel-1 SAR",
            cloud_cover=None,  # Null-safe for SAR radar
            acquisition_datetime=datetime(2022, 7, 1, tzinfo=timezone.utc),
        ),
    ]

    accepted, report = QualityFilterPipeline.filter_observations(observations, max_cloud_cover=30.0)
    assert len(accepted) == 2
    assert report.rejected_count == 1
    assert "EXCESSIVE_CLOUD_COVER" in report.rejection_reasons


def test_reject_predicted_epistemic_level_leakage():
    # Hard requirement 8: Never use PREDICTED values as historical training observations
    observations = [
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=0.65,
            acquisition_datetime=datetime(2020, 7, 1, tzinfo=timezone.utc),
            epistemic_level=EpistemicLevel.CALCULATED,
        ),
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=0.72,
            acquisition_datetime=datetime(2028, 7, 1, tzinfo=timezone.utc),
            epistemic_level=EpistemicLevel.PREDICTED,
        ),
    ]

    accepted, report = QualityFilterPipeline.filter_observations(observations)
    assert len(accepted) == 1
    assert report.rejected_count == 1
    assert "PREDICTED_EPISTEMIC_LEVEL_LEAKAGE" in report.rejection_reasons
