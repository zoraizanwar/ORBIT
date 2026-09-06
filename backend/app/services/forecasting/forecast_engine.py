import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.models.enums import EpistemicLevel, EvidenceStrength
from app.services.forecasting.exceptions import (
    ForecastingError,
    InvalidHorizonError,
    InsufficientDataError,
    ScenarioError,
)
from app.services.forecasting.models import (
    ForecastMetric,
    TemporalResolution,
    AggregationMethod,
    ForecastScenarioType,
    ForecastStatus,
    HistoricalObservation,
    AggregatedObservation,
    ForecastPredictionPoint,
    ForecastRunResult,
    PrepareSeriesPayload,
    RunForecastPayload,
)
from app.services.forecasting.quality_filter import QualityFilterPipeline
from app.services.forecasting.temporal_aggregation import TemporalAggregator
from app.services.forecasting.feature_engineering import FeatureExtractor
from app.services.forecasting.forecast_models import MODEL_REGISTRY
from app.services.forecasting.backtesting import TemporalHoldoutBacktester


class ForecastEngine:
    """
    Unified ORBIT Future Forecasting & Prediction Engine.
    Executes end-to-end data preparation, quality filtering, temporal aggregation,
    feature engineering, model fitting, horizon projection, and cryptographic provenance tracing.
    """

    @classmethod
    def prepare_series(
        cls,
        payload: PrepareSeriesPayload,
    ) -> Dict[str, Any]:
        """
        Runs quality filtering and temporal aggregation on raw observations.
        """
        filtered_obs, quality_report = QualityFilterPipeline.filter_observations(
            observations=payload.observations,
            max_cloud_cover=payload.max_cloud_cover,
            min_valid_pixel_pct=payload.min_valid_pixel_pct,
        )

        aggregated = TemporalAggregator.aggregate_series(
            observations=filtered_obs,
            resolution=payload.temporal_resolution,
            method=payload.aggregation_method,
        )

        return {
            "aoi_id": payload.aoi_id,
            "metric": payload.metric,
            "quality_report": quality_report.model_dump(),
            "aggregated_series": [agg.model_dump() for agg in aggregated],
            "aggregated_count": len(aggregated),
        }

    @classmethod
    def run_forecast(
        cls,
        payload: RunForecastPayload,
        run_id: Optional[str] = None,
    ) -> ForecastRunResult:
        """
        Executes future forecast projection based on historical observations.
        """
        forecast_run_id = run_id or f"fc-run-{str(uuid.uuid4())[:8]}"

        # 1. Model Registry Security Check (Requirement 33)
        if payload.model_name not in MODEL_REGISTRY:
            raise ForecastingError(
                f"Model '{payload.model_name}' is not an authorized forecasting model in MODEL_REGISTRY."
            )

        # 2. Quality Filtering
        filtered_obs, quality_report = QualityFilterPipeline.filter_observations(
            observations=payload.observations,
        )

        # 3. Temporal Aggregation
        aggregated = TemporalAggregator.aggregate_series(
            observations=filtered_obs,
            resolution=payload.temporal_resolution,
            method=payload.aggregation_method,
        )

        # 4. Feature Extraction & Minimum Observation Check
        features, min_year, max_year = FeatureExtractor.extract_features(
            series=aggregated,
            min_observations=payload.min_observations,
            min_span_years=payload.min_span_years,
        )

        # 5. Future Horizon Validation (Requirements 14 & 38)
        if payload.forecast_start_year <= max_year:
            raise InvalidHorizonError(
                f"Forecast start year ({payload.forecast_start_year}) must be strictly later than the last historical training year ({max_year})."
            )

        if payload.forecast_end_year < payload.forecast_start_year:
            raise InvalidHorizonError(
                f"Forecast end year ({payload.forecast_end_year}) cannot precede forecast start year ({payload.forecast_start_year})."
            )

        if payload.forecast_end_year > 2050:
            raise InvalidHorizonError(
                f"Forecast horizon cannot extend beyond 2050 (requested {payload.forecast_end_year})."
            )

        # 6. Fit Baseline Model
        model_cls = MODEL_REGISTRY[payload.model_name]
        model = model_cls()
        model.fit(features)

        # 7. Generate Future Projections
        predictions: List[ForecastPredictionPoint] = []
        base_year = min_year

        for yr in range(payload.forecast_start_year, payload.forecast_end_year + 1):
            t_coord = float(yr - base_year)
            y_pred, lower, upper = model.predict(
                target_t=t_coord,
                confidence_level=payload.confidence_level,
            )

            # Scenario adjustments if applicable
            if payload.scenario == ForecastScenarioType.CONSERVATION_POLICY and payload.metric == ForecastMetric.NDVI:
                # Simulated conservation scenario adjustment (+0.02 boost bounded)
                y_pred = min(1.0, y_pred + 0.02)
                lower = lower + 0.02 if lower is not None else None
                upper = min(1.0, upper + 0.02) if upper is not None else None

            predictions.append(
                ForecastPredictionPoint(
                    target_year=yr,
                    target_date=f"{yr}-07-01T00:00:00Z",
                    predicted_value=round(y_pred, 4),
                    lower_bound=round(lower, 4) if lower is not None else None,
                    upper_bound=round(upper, 4) if upper is not None else None,
                    confidence_level=payload.confidence_level,
                    epistemic_level=EpistemicLevel.PREDICTED,
                    uncertainty_status="CALCULATED",
                )
            )

        # 8. Run Backtesting
        if payload.run_backtest:
            backtest_report = TemporalHoldoutBacktester.evaluate_backtest(
                features=features,
                model_name=payload.model_name,
                model_version=payload.model_version,
            )
        else:
            backtest_report = TemporalHoldoutBacktester.evaluate_backtest(
                features=[],
            )

        # 9. Cryptographic Provenance Fingerprint (Requirement 41)
        provenance_payload = {
            "run_id": forecast_run_id,
            "aoi_id": payload.aoi_id,
            "metric": payload.metric.value,
            "model_name": payload.model_name,
            "model_version": payload.model_version,
            "scenario": payload.scenario.value,
            "training_start_year": min_year,
            "training_end_year": max_year,
            "training_samples_count": len(features),
            "forecast_start_year": payload.forecast_start_year,
            "forecast_end_year": payload.forecast_end_year,
            "model_metadata": model.get_metadata(),
            "source_scene_count": len(filtered_obs),
            "epistemic_level": "PREDICTED",
            "deterministic_pipeline": True,
            "ai_interpretation_invoked": False,
        }

        provenance_str = json.dumps(provenance_payload, sort_keys=True)
        sha256_hash = hashlib.sha256(provenance_str.encode("utf-8")).hexdigest()
        provenance_payload["provenance_hash_sha256"] = sha256_hash

        # Evidence strength determination
        if len(features) >= 6 and backtest_report.status == "COMPLETED":
            strength = EvidenceStrength.STRONG
        elif len(features) >= 4:
            strength = EvidenceStrength.MODERATE
        else:
            strength = EvidenceStrength.LIMITED

        now_utc = datetime.now(timezone.utc).isoformat()

        return ForecastRunResult(
            run_id=forecast_run_id,
            aoi_id=payload.aoi_id,
            metric=payload.metric,
            unit="index_value" if payload.metric in [ForecastMetric.NDVI, ForecastMetric.NDWI, ForecastMetric.NDBI, ForecastMetric.SAVI] else "km2",
            model_name=payload.model_name,
            model_version=payload.model_version,
            scenario=payload.scenario,
            training_start_year=min_year,
            training_end_year=max_year,
            training_observation_count=len(features),
            forecast_horizon_years=payload.forecast_end_year - payload.forecast_start_year + 1,
            predictions=predictions,
            backtest=backtest_report,
            quality_filter_report=quality_report,
            provenance=provenance_payload,
            epistemic_level=EpistemicLevel.PREDICTED,
            evidence_strength=strength,
            status=ForecastStatus.COMPLETED,
            created_at=now_utc,
        )
