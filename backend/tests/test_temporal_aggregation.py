from datetime import datetime, timezone
import pytest
from app.services.forecasting.models import (
    ForecastMetric,
    HistoricalObservation,
    TemporalResolution,
    AggregationMethod,
)
from app.services.forecasting.temporal_aggregation import TemporalAggregator


def test_annual_median_aggregation():
    observations = [
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=0.60,
            acquisition_datetime=datetime(2020, 6, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=0.70,
            acquisition_datetime=datetime(2020, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=0.65,
            acquisition_datetime=datetime(2020, 8, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDVI,
            value=0.55,
            acquisition_datetime=datetime(2021, 7, 1, tzinfo=timezone.utc),
        ),
    ]

    agg = TemporalAggregator.aggregate_series(
        observations=observations,
        resolution=TemporalResolution.ANNUAL,
        method=AggregationMethod.MEDIAN,
    )

    assert len(agg) == 2
    # 2020 median of [0.60, 0.65, 0.70] is 0.65
    assert agg[0].year == 2020
    assert agg[0].value == 0.65
    assert agg[0].observation_count == 3

    # 2021
    assert agg[1].year == 2021
    assert agg[1].value == 0.55
    assert agg[1].observation_count == 1


def test_quarterly_mean_aggregation():
    observations = [
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDWI,
            value=0.20,
            acquisition_datetime=datetime(2022, 1, 15, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDWI,
            value=0.30,
            acquisition_datetime=datetime(2022, 2, 20, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-1",
            metric=ForecastMetric.NDWI,
            value=0.10,
            acquisition_datetime=datetime(2022, 5, 10, tzinfo=timezone.utc),
        ),
    ]

    agg = TemporalAggregator.aggregate_series(
        observations=observations,
        resolution=TemporalResolution.QUARTERLY,
        method=AggregationMethod.MEAN,
    )

    assert len(agg) == 2
    assert agg[0].period_key == "2022-Q1"
    assert agg[0].value == 0.25
    assert agg[1].period_key == "2022-Q2"
    assert agg[1].value == 0.10
