from app.services.forecasting.models import FeatureVector
from app.services.forecasting.backtesting import TemporalHoldoutBacktester


def test_temporal_holdout_backtester_evaluation():
    # 5 observations -> 2 backtest evaluation splits (k=3, k=4)
    features = [
        FeatureVector(time_coordinate=0.0, year=2019, value=0.70),
        FeatureVector(time_coordinate=1.0, year=2020, value=0.66),
        FeatureVector(time_coordinate=2.0, year=2021, value=0.62),
        FeatureVector(time_coordinate=3.0, year=2022, value=0.58),
        FeatureVector(time_coordinate=4.0, year=2023, value=0.54),
    ]

    report = TemporalHoldoutBacktester.evaluate_backtest(features)
    assert report.status == "COMPLETED"
    assert report.splits_count == 2
    assert len(report.splits) == 2
    assert report.overall_metrics is not None
    assert report.overall_metrics.mae >= 0.0
    assert report.overall_metrics.rmse >= 0.0
    assert 0.0 <= report.overall_metrics.r_squared <= 1.0


def test_temporal_holdout_insufficient_data():
    features = [
        FeatureVector(time_coordinate=0.0, year=2020, value=0.70),
        FeatureVector(time_coordinate=1.0, year=2021, value=0.66),
    ]

    report = TemporalHoldoutBacktester.evaluate_backtest(features)
    assert report.status == "INSUFFICIENT_DATA"
    assert report.splits_count == 0
    assert report.overall_metrics is None
