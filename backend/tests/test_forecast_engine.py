from datetime import datetime, timezone
import pytest
from app.models.enums import EpistemicLevel
from app.services.forecasting.exceptions import InvalidHorizonError, InsufficientDataError
from app.services.forecasting.models import (
    ForecastMetric,
    ForecastScenarioType,
    HistoricalObservation,
    RunForecastPayload,
)
from app.services.forecasting.forecast_engine import ForecastEngine


def test_forecast_engine_end_to_end_projection():
    observations = [
        HistoricalObservation(
            aoi_id="aoi-sinop",
            metric=ForecastMetric.NDVI,
            value=0.72,
            acquisition_datetime=datetime(2020, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-sinop",
            metric=ForecastMetric.NDVI,
            value=0.68,
            acquisition_datetime=datetime(2021, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-sinop",
            metric=ForecastMetric.NDVI,
            value=0.63,
            acquisition_datetime=datetime(2022, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-sinop",
            metric=ForecastMetric.NDVI,
            value=0.59,
            acquisition_datetime=datetime(2023, 7, 1, tzinfo=timezone.utc),
        ),
    ]

    payload = RunForecastPayload(
        aoi_id="aoi-sinop",
        metric=ForecastMetric.NDVI,
        observations=observations,
        forecast_start_year=2024,
        forecast_end_year=2028,
        scenario=ForecastScenarioType.BASELINE_TREND,
    )

    result = ForecastEngine.run_forecast(payload)

    assert result.status == "COMPLETED"
    assert result.training_start_year == 2020
    assert result.training_end_year == 2023
    assert len(result.predictions) == 5  # 2024, 2025, 2026, 2027, 2028

    # All predictions strictly PREDICTED epistemic level
    for p in result.predictions:
        assert p.epistemic_level == EpistemicLevel.PREDICTED
        assert p.target_year >= 2024
        assert p.lower_bound is not None
        assert p.upper_bound is not None
        assert p.lower_bound <= p.predicted_value <= p.upper_bound

    # Provenance hash verified
    assert "provenance_hash_sha256" in result.provenance
    assert len(result.provenance["provenance_hash_sha256"]) == 64


def test_forecast_engine_rejects_past_or_current_start_year():
    observations = [
        HistoricalObservation(
            aoi_id="aoi-sinop",
            metric=ForecastMetric.NDVI,
            value=0.72,
            acquisition_datetime=datetime(2020, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-sinop",
            metric=ForecastMetric.NDVI,
            value=0.68,
            acquisition_datetime=datetime(2021, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-sinop",
            metric=ForecastMetric.NDVI,
            value=0.63,
            acquisition_datetime=datetime(2022, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-sinop",
            metric=ForecastMetric.NDVI,
            value=0.59,
            acquisition_datetime=datetime(2023, 7, 1, tzinfo=timezone.utc),
        ),
    ]

    payload = RunForecastPayload(
        aoi_id="aoi-sinop",
        metric=ForecastMetric.NDVI,
        observations=observations,
        forecast_start_year=2022,  # Past relative to 2023 training end
        forecast_end_year=2028,
    )

    with pytest.raises(InvalidHorizonError):
        ForecastEngine.run_forecast(payload)


def test_forecast_engine_rejects_horizon_beyond_2050():
    observations = [
        HistoricalObservation(
            aoi_id="aoi-sinop",
            metric=ForecastMetric.NDVI,
            value=0.72,
            acquisition_datetime=datetime(2020, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-sinop",
            metric=ForecastMetric.NDVI,
            value=0.68,
            acquisition_datetime=datetime(2021, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-sinop",
            metric=ForecastMetric.NDVI,
            value=0.63,
            acquisition_datetime=datetime(2022, 7, 1, tzinfo=timezone.utc),
        ),
        HistoricalObservation(
            aoi_id="aoi-sinop",
            metric=ForecastMetric.NDVI,
            value=0.59,
            acquisition_datetime=datetime(2023, 7, 1, tzinfo=timezone.utc),
        ),
    ]

    payload = RunForecastPayload(
        aoi_id="aoi-sinop",
        metric=ForecastMetric.NDVI,
        observations=observations,
        forecast_start_year=2024,
        forecast_end_year=2055,  # Beyond 2050 boundary
    )

    with pytest.raises(InvalidHorizonError):
        ForecastEngine.run_forecast(payload)


def test_alembic_migration_0007_script_validity():
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    rev = script.get_revision("0007_forecasting_foundation")
    assert rev is not None
    assert rev.down_revision == "0006_advanced_geo_intel"
