import abc
import math
from typing import Dict, List, Optional, Tuple, Type
from app.services.forecasting.exceptions import ModelFitError
from app.services.forecasting.models import (
    FeatureVector,
    ModelEvaluationMetrics,
)


class ForecastModelInterface(abc.ABC):
    """
    Abstract interface for all ORBIT time-series forecasting models.
    Enables future plug-and-play model replacement (ARIMA, Prophet, LSTM) without altering database or API schemas.
    """

    @abc.abstractmethod
    def fit(self, features: List[FeatureVector]) -> None:
        """Fits model parameters on historical features."""
        pass

    @abc.abstractmethod
    def predict(
        self,
        target_t: float,
        confidence_level: float = 0.95,
    ) -> Tuple[float, Optional[float], Optional[float]]:
        """
        Returns (predicted_value, lower_bound, upper_bound).
        """
        pass

    @abc.abstractmethod
    def evaluate(self, features: List[FeatureVector]) -> ModelEvaluationMetrics:
        """Evaluates model performance against given feature vectors."""
        pass

    @abc.abstractmethod
    def get_metadata(self) -> Dict[str, any]:
        """Returns model parameters, version, and diagnostic metadata."""
        pass


class LinearTrendModel(ForecastModelInterface):
    """
    Deterministic Linear Trend Regression Model (ORBIT-LT-v1).
    Fits ordinary linear regression y = beta_0 + beta_1 * t and calculates analytical prediction intervals.
    """

    MODEL_NAME = "LINEAR_TREND"
    MODEL_VERSION = "ORBIT-LT-v1"

    def __init__(self):
        self.is_fitted = False
        self.beta_0: float = 0.0
        self.beta_1: float = 0.0
        self.mean_t: float = 0.0
        self.sum_sq_t: float = 0.0
        self.residual_std_error: float = 0.0
        self.r_squared: float = 0.0
        self.n_samples: int = 0

    def fit(self, features: List[FeatureVector]) -> None:
        n = len(features)
        if n < 2:
            raise ModelFitError(f"LinearTrendModel requires at least 2 samples to fit, got {n}.")

        t_vals = [f.time_coordinate for f in features]
        y_vals = [f.value for f in features]

        mean_t = sum(t_vals) / n
        mean_y = sum(y_vals) / n

        num = sum((t - mean_t) * (y - mean_y) for t, y in zip(t_vals, y_vals))
        den = sum((t - mean_t) ** 2 for t in t_vals)

        if den == 0:
            # All time coordinates identical
            self.beta_1 = 0.0
            self.beta_0 = mean_y
        else:
            self.beta_1 = num / den
            self.beta_0 = mean_y - (self.beta_1 * mean_t)

        self.mean_t = mean_t
        self.sum_sq_t = den
        self.n_samples = n

        # Residual analysis
        ss_res = 0.0
        ss_tot = 0.0
        for t, y in zip(t_vals, y_vals):
            y_pred = self.beta_0 + (self.beta_1 * t)
            ss_res += (y - y_pred) ** 2
            ss_tot += (y - mean_y) ** 2

        if ss_tot == 0:
            self.r_squared = 1.0
        else:
            self.r_squared = max(0.0, min(1.0, 1.0 - (ss_res / ss_tot)))

        df = max(1, n - 2)
        self.residual_std_error = math.sqrt(ss_res / df)
        self.is_fitted = True

    def predict(
        self,
        target_t: float,
        confidence_level: float = 0.95,
    ) -> Tuple[float, Optional[float], Optional[float]]:
        if not self.is_fitted:
            raise ModelFitError("Cannot predict with an unfitted LinearTrendModel.")

        y_hat = self.beta_0 + (self.beta_1 * target_t)

        # Approximate t-critical for 95% CI (1.96 standard normal approximation or small sample correction)
        t_crit = 1.96
        if self.n_samples <= 5:
            t_crit = 2.57
        elif self.n_samples <= 10:
            t_crit = 2.23

        # Analytical prediction standard error
        if self.sum_sq_t > 0:
            h_ii = (1.0 / self.n_samples) + (((target_t - self.mean_t) ** 2) / self.sum_sq_t)
            se_pred = self.residual_std_error * math.sqrt(1.0 + h_ii)
        else:
            se_pred = self.residual_std_error

        margin = t_crit * se_pred
        lower = round(y_hat - margin, 4)
        upper = round(y_hat + margin, 4)

        return round(y_hat, 4), lower, upper

    def evaluate(self, features: List[FeatureVector]) -> ModelEvaluationMetrics:
        if not self.is_fitted:
            raise ModelFitError("Cannot evaluate with an unfitted LinearTrendModel.")

        if not features:
            return ModelEvaluationMetrics(mae=0.0, rmse=0.0, r_squared=0.0, sample_size=0)

        n = len(features)
        t_vals = [f.time_coordinate for f in features]
        y_vals = [f.value for f in features]

        mean_y = sum(y_vals) / n
        abs_errors = []
        sq_errors = []
        ss_tot = 0.0

        for t, y in zip(t_vals, y_vals):
            y_pred = self.beta_0 + (self.beta_1 * t)
            err = y - y_pred
            abs_errors.append(abs(err))
            sq_errors.append(err ** 2)
            ss_tot += (y - mean_y) ** 2

        mae = sum(abs_errors) / n
        rmse = math.sqrt(sum(sq_errors) / n)
        ss_res = sum(sq_errors)

        if ss_tot == 0:
            r2 = 1.0
        else:
            r2 = max(0.0, min(1.0, 1.0 - (ss_res / ss_tot)))

        return ModelEvaluationMetrics(
            mae=round(mae, 4),
            rmse=round(rmse, 4),
            r_squared=round(r2, 4),
            sample_size=n,
        )

    def get_metadata(self) -> Dict[str, any]:
        return {
            "model_name": self.MODEL_NAME,
            "model_version": self.MODEL_VERSION,
            "intercept_beta_0": round(self.beta_0, 6),
            "slope_beta_1": round(self.beta_1, 6),
            "training_samples_count": self.n_samples,
            "residual_std_error": round(self.residual_std_error, 6),
            "training_r_squared": round(self.r_squared, 4),
            "algorithm": "Ordinary_Least_Squares_Trend_Projection",
        }


# Controlled registry of approved forecasting models (Security Requirement 33)
MODEL_REGISTRY: Dict[str, Type[ForecastModelInterface]] = {
    "LINEAR_TREND": LinearTrendModel,
    "ORBIT-LT-v1": LinearTrendModel,
}
