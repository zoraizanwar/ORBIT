import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.enums import EpistemicLevel, EvidenceStrength, AnalysisStatus, FuturePredictionType
from app.models.history_deep.future_prediction import FuturePrediction
from app.models.analysis.analysis_run import AnalysisRun
from app.services.forecasting import (
    ForecastEngine,
    PrepareSeriesPayload,
    RunForecastPayload,
    ForecastRunResult,
    BacktestReport,
    TemporalHoldoutBacktester,
    FeatureExtractor,
    TemporalAggregator,
    QualityFilterPipeline,
    ForecastMetric,
    InsufficientDataError,
    InvalidHorizonError,
    ForecastingError,
)

router = APIRouter(prefix="/forecast", tags=["Forecasting & Future Predictions"])


class BacktestPayload(BaseModel):
    observations: List[Any]
    temporal_resolution: str = "ANNUAL"
    aggregation_method: str = "MEDIAN"
    min_observations: int = 4
    min_span_years: float = 2.0


@router.post(
    "/prepare",
    summary="Prepare & Quality-Filter Time-Series Observations",
    description="Applies multi-stage data quality filtering, timestamp deduplication, and temporal aggregation.",
)
async def prepare_series(
    payload: PrepareSeriesPayload,
) -> Dict[str, Any]:
    try:
        return ForecastEngine.prepare_series(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Time-series preparation failed: {str(e)}",
        ) from e


@router.post(
    "/run",
    response_model=ForecastRunResult,
    summary="Execute Statistical Trend Forecasting Run",
    description="Fits calibrated baseline forecasting model on historical observations and computes future predictions with prediction intervals [Epistemic: PREDICTED].",
)
async def run_forecast(
    payload: RunForecastPayload,
    session: AsyncSession = Depends(get_db),
) -> ForecastRunResult:
    try:
        run_id_val = str(uuid.uuid4())
        aoi_uuid = uuid.UUID(payload.aoi_id) if len(payload.aoi_id) == 36 else None

        # 1. Execute Forecast Engine
        result = ForecastEngine.run_forecast(
            payload=payload,
            run_id=run_id_val,
        )

        # 2. Persist to analysis.runs and history_deep.future_predictions if AOI is valid UUID
        if aoi_uuid and payload.project_id:
            analysis_run = AnalysisRun(
                id=uuid.UUID(run_id_val),
                project_id=payload.project_id,
                area_of_interest_id=aoi_uuid,
                status=AnalysisStatus.COMPLETED,
                analysis_type="TIME_SERIES_FORECAST",
                start_date=datetime(result.training_start_year, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(payload.forecast_end_year, 12, 31, tzinfo=timezone.utc),
                parameters={
                    "metric": payload.metric.value,
                    "model_name": payload.model_name,
                    "model_version": payload.model_version,
                    "scenario": payload.scenario.value,
                    "forecast_start_year": payload.forecast_start_year,
                    "forecast_end_year": payload.forecast_end_year,
                },
                pipeline_version=payload.model_version,
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
            )
            session.add(analysis_run)

            # Map to FuturePredictionType
            pred_type_map = {
                ForecastMetric.NDVI: FuturePredictionType.VEGETATION_TREND,
                ForecastMetric.NDWI: FuturePredictionType.WATER_COVERAGE,
                ForecastMetric.NDBI: FuturePredictionType.URBAN_EXPANSION,
                ForecastMetric.BUILT_UP_AREA: FuturePredictionType.URBAN_EXPANSION,
                ForecastMetric.VEGETATED_AREA: FuturePredictionType.VEGETATION_TREND,
                ForecastMetric.SURFACE_WATER_AREA: FuturePredictionType.WATER_COVERAGE,
            }
            pred_enum_type = pred_type_map.get(payload.metric, FuturePredictionType.VEGETATION_TREND)

            for p in result.predictions:
                pred_db = FuturePrediction(
                    id=uuid.uuid4(),
                    area_of_interest_id=aoi_uuid,
                    analysis_run_id=uuid.UUID(run_id_val),
                    prediction_type=pred_enum_type,
                    metric=payload.metric.value,
                    target_year=p.target_year,
                    prediction_value=p.predicted_value,
                    lower_bound=p.lower_bound,
                    upper_bound=p.upper_bound,
                    unit=result.unit,
                    model_name=result.model_name,
                    model_version=result.model_version,
                    training_start_year=result.training_start_year,
                    training_end_year=result.training_end_year,
                    confidence=p.confidence_level,
                    evidence_strength=result.evidence_strength,
                    scenario=result.scenario.value,
                    assumptions={"model_type": result.model_name, "scenario": result.scenario.value},
                    limitations={"extrapolation_horizon": result.forecast_horizon_years},
                    provenance=result.provenance,
                )
                session.add(pred_db)

            await session.commit()

        return result
    except InsufficientDataError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "status": "INSUFFICIENT_DATA",
                "reason": str(e),
                "required_observations": e.required_count,
                "available_observations": e.available_count,
            },
        ) from e
    except InvalidHorizonError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except ForecastingError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forecasting calculation failed: {str(e)}",
        ) from e


@router.post(
    "/backtest",
    response_model=BacktestReport,
    summary="Evaluate Out-of-Sample Historical Backtest",
    description="Runs expanding-window temporal holdout backtesting to measure MAE, RMSE, and R².",
)
async def evaluate_backtest(
    payload: PrepareSeriesPayload,
) -> BacktestReport:
    try:
        filtered_obs, _ = QualityFilterPipeline.filter_observations(payload.observations)
        aggregated = TemporalAggregator.aggregate_series(
            observations=filtered_obs,
            resolution=payload.temporal_resolution,
            method=payload.aggregation_method,
        )
        features, _, _ = FeatureExtractor.extract_features(
            series=aggregated,
            min_observations=4,
            min_span_years=2.0,
        )
        return TemporalHoldoutBacktester.evaluate_backtest(features=features)
    except InsufficientDataError as e:
        return BacktestReport(
            status="INSUFFICIENT_DATA",
            splits_count=0,
            splits=[],
            overall_metrics=None,
            model_name="LINEAR_TREND",
            model_version="ORBIT-LT-v1",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Backtesting evaluation failed: {str(e)}",
        ) from e


@router.get(
    "/series",
    summary="Query Future Predictions",
    description="Queries stored future predictions with filtering by AOI, metric, target year range.",
)
async def query_predictions(
    aoi_id: Optional[uuid.UUID] = Query(None),
    metric: Optional[str] = Query(None),
    start_year: Optional[int] = Query(None),
    end_year: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    query = select(FuturePrediction)
    conditions = []
    if aoi_id:
        conditions.append(FuturePrediction.area_of_interest_id == aoi_id)
    if metric:
        conditions.append(FuturePrediction.metric == metric)
    if start_year:
        conditions.append(FuturePrediction.target_year >= start_year)
    if end_year:
        conditions.append(FuturePrediction.target_year <= end_year)
    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(FuturePrediction.target_year).offset(offset).limit(limit)
    res = await session.execute(query)
    predictions = res.scalars().all()

    return {
        "total": len(predictions),
        "offset": offset,
        "limit": limit,
        "items": [
            {
                "id": str(p.id),
                "aoi_id": str(p.area_of_interest_id),
                "analysis_run_id": str(p.analysis_run_id) if p.analysis_run_id else None,
                "metric": p.metric,
                "prediction_type": p.prediction_type.value,
                "target_year": p.target_year,
                "predicted_value": p.prediction_value,
                "lower_bound": p.lower_bound,
                "upper_bound": p.upper_bound,
                "unit": p.unit,
                "model_name": p.model_name,
                "model_version": p.model_version,
                "training_start_year": p.training_start_year,
                "training_end_year": p.training_end_year,
                "confidence": p.confidence,
                "evidence_strength": p.evidence_strength.value,
                "scenario": p.scenario,
                "epistemic_level": "PREDICTED",
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in predictions
        ],
    }


@router.get(
    "/{prediction_id}",
    summary="Get Prediction By ID",
    description="Retrieves a single prediction record.",
)
async def get_prediction(
    prediction_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    res = await session.execute(select(FuturePrediction).where(FuturePrediction.id == prediction_id))
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction {prediction_id} not found",
        )

    return {
        "id": str(p.id),
        "aoi_id": str(p.area_of_interest_id),
        "analysis_run_id": str(p.analysis_run_id) if p.analysis_run_id else None,
        "metric": p.metric,
        "prediction_type": p.prediction_type.value,
        "target_year": p.target_year,
        "predicted_value": p.prediction_value,
        "lower_bound": p.lower_bound,
        "upper_bound": p.upper_bound,
        "unit": p.unit,
        "model_name": p.model_name,
        "model_version": p.model_version,
        "training_start_year": p.training_start_year,
        "training_end_year": p.training_end_year,
        "confidence": p.confidence,
        "evidence_strength": p.evidence_strength.value,
        "scenario": p.scenario,
        "epistemic_level": "PREDICTED",
        "provenance": p.provenance,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


@router.get(
    "/{prediction_id}/provenance",
    summary="Get Prediction Provenance",
    description="Retrieves complete calculation trace and cryptographic lineage for a future prediction.",
)
async def get_prediction_provenance(
    prediction_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    res = await session.execute(select(FuturePrediction).where(FuturePrediction.id == prediction_id))
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction {prediction_id} not found",
        )

    return {
        "prediction_id": str(p.id),
        "model_name": p.model_name,
        "model_version": p.model_version,
        "metric": p.metric,
        "scenario": p.scenario,
        "training_start_year": p.training_start_year,
        "training_end_year": p.training_end_year,
        "target_year": p.target_year,
        "epistemic_level": "PREDICTED",
        "provenance_trace": p.provenance,
    }
