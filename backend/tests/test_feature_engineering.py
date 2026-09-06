from datetime import datetime, timezone
import pytest
from app.services.forecasting.exceptions import InsufficientDataError
from app.services.forecasting.models import (
    AggregatedObservation,
    AggregationMethod,
)
from app.services.forecasting.feature_engineering import FeatureExtractor


def test_extract_features_valid():
    series = [
        AggregatedObservation(
            period_key="2020",
            year=2020,
            value=0.68,
            observation_count=5,
            aggregation_method=AggregationMethod.MEDIAN,
            date_start=datetime(2020, 1, 1, tzinfo=timezone.utc),
            date_end=datetime(2020, 12, 31, tzinfo=timezone.utc),
        ),
        AggregatedObservation(
            period_key="2021",
            year=2021,
            value=0.64,
            observation_count=6,
            aggregation_method=AggregationMethod.MEDIAN,
            date_start=datetime(2021, 1, 1, tzinfo=timezone.utc),
            date_end=datetime(2021, 12, 31, tzinfo=timezone.utc),
        ),
        AggregatedObservation(
            period_key="2022",
            year=2022,
            value=0.60,
            observation_count=7,
            aggregation_method=AggregationMethod.MEDIAN,
            date_start=datetime(2022, 1, 1, tzinfo=timezone.utc),
            date_end=datetime(2022, 12, 31, tzinfo=timezone.utc),
        ),
        AggregatedObservation(
            period_key="2023",
            year=2023,
            value=0.55,
            observation_count=6,
            aggregation_method=AggregationMethod.MEDIAN,
            date_start=datetime(2023, 1, 1, tzinfo=timezone.utc),
            date_end=datetime(2023, 12, 31, tzinfo=timezone.utc),
        ),
    ]

    features, min_y, max_y = FeatureExtractor.extract_features(series, min_observations=4, min_span_years=2.0)
    assert len(features) == 4
    assert min_y == 2020
    assert max_y == 2023
    assert features[0].time_coordinate == 0.0
    assert features[3].time_coordinate == 3.0
    assert features[3].rolling_mean_3 is not None


def test_insufficient_observation_count_raises():
    series = [
        AggregatedObservation(
            period_key="2020",
            year=2020,
            value=0.68,
            observation_count=5,
            aggregation_method=AggregationMethod.MEDIAN,
            date_start=datetime(2020, 1, 1, tzinfo=timezone.utc),
            date_end=datetime(2020, 12, 31, tzinfo=timezone.utc),
        ),
        AggregatedObservation(
            period_key="2021",
            year=2021,
            value=0.64,
            observation_count=6,
            aggregation_method=AggregationMethod.MEDIAN,
            date_start=datetime(2021, 1, 1, tzinfo=timezone.utc),
            date_end=datetime(2021, 12, 31, tzinfo=timezone.utc),
        ),
    ]

    with pytest.raises(InsufficientDataError) as exc_info:
        FeatureExtractor.extract_features(series, min_observations=4)
    assert exc_info.value.required_count == 4
    assert exc_info.value.available_count == 2
