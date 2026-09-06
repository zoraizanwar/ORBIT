import math
from typing import List
from app.services.forecasting.models import (
    FeatureVector,
    BacktestSplitResult,
    BacktestReport,
    ModelEvaluationMetrics,
)
from app.services.forecasting.forecast_models import LinearTrendModel


class TemporalHoldoutBacktester:
    """
    Rolling-origin / temporal holdout backtesting engine.
    Strictly prevents future-leakage by evaluating models only on chronologically forward holdouts.
    """

    @classmethod
    def evaluate_backtest(
        cls,
        features: List[FeatureVector],
        model_name: str = "LINEAR_TREND",
        model_version: str = "ORBIT-LT-v1",
        min_train_samples: int = 3,
    ) -> BacktestReport:
        n = len(features)
        if n < min_train_samples + 1:
            return BacktestReport(
                status="INSUFFICIENT_DATA",
                splits_count=0,
                splits=[],
                overall_metrics=None,
                model_name=model_name,
                model_version=model_version,
            )

        splits: List[BacktestSplitResult] = []
        abs_errors: List[float] = []
        sq_errors: List[float] = []
        actuals: List[float] = []

        # Expanding window backtest
        for k in range(min_train_samples, n):
            train_set = features[:k]
            val_point = features[k]

            model = LinearTrendModel()
            model.fit(train_set)

            pred_val, _, _ = model.predict(val_point.time_coordinate)
            err = val_point.value - pred_val
            abs_err = abs(err)

            splits.append(
                BacktestSplitResult(
                    train_start_year=train_set[0].year,
                    train_end_year=train_set[-1].year,
                    val_year=val_point.year,
                    actual_value=round(val_point.value, 4),
                    predicted_value=round(pred_val, 4),
                    error=round(err, 4),
                    absolute_error=round(abs_err, 4),
                )
            )

            abs_errors.append(abs_err)
            sq_errors.append(err ** 2)
            actuals.append(val_point.value)

        # Calculate overall backtest metrics
        k_eval = len(splits)
        mae = sum(abs_errors) / k_eval
        rmse = math.sqrt(sum(sq_errors) / k_eval)

        mean_actual = sum(actuals) / k_eval
        ss_tot = sum((y - mean_actual) ** 2 for y in actuals)
        ss_res = sum(sq_errors)
        r2 = max(0.0, min(1.0, 1.0 - (ss_res / ss_tot))) if ss_tot > 0 else 1.0

        metrics = ModelEvaluationMetrics(
            mae=round(mae, 4),
            rmse=round(rmse, 4),
            r_squared=round(r2, 4),
            sample_size=k_eval,
        )

        return BacktestReport(
            status="COMPLETED",
            splits_count=k_eval,
            splits=splits,
            overall_metrics=metrics,
            model_name=model_name,
            model_version=model_version,
        )
