import statistics
from typing import List, Tuple
from app.services.forecasting.exceptions import InsufficientDataError
from app.services.forecasting.models import (
    AggregatedObservation,
    FeatureVector,
)


class FeatureExtractor:
    """
    Feature engineering layer for time-series forecasting.
    Normalizes time coordinates, extracts rolling statistics, and validates temporal span.
    """

    @classmethod
    def extract_features(
        cls,
        series: List[AggregatedObservation],
        min_observations: int = 4,
        min_span_years: float = 2.0,
    ) -> Tuple[List[FeatureVector], int, int]:
        """
        Extracts feature vectors from aggregated observations.
        Raises InsufficientDataError if count or temporal span requirements are not satisfied.
        """
        if len(series) < min_observations:
            raise InsufficientDataError(
                f"Time-series contains only {len(series)} observations; at least {min_observations} are required.",
                required_count=min_observations,
                available_count=len(series),
            )

        years = [s.year for s in series]
        min_year = min(years)
        max_year = max(years)
        span_years = max_year - min_year

        if span_years < min_span_years:
            raise InsufficientDataError(
                f"Time-series temporal span ({span_years:.1f} years) is less than the required minimum ({min_span_years:.1f} years).",
                required_count=int(min_span_years),
                available_count=int(span_years),
            )

        features: List[FeatureVector] = []
        base_year = min_year

        for idx, obs in enumerate(series):
            # Time coordinate relative to baseline year
            t_coord = float(obs.year - base_year)
            if obs.month is not None:
                t_coord += (obs.month - 1) / 12.0
            elif obs.quarter is not None:
                t_coord += (obs.quarter - 1) / 4.0

            # Rolling window (last 3 observations)
            window_vals = [series[k].value for k in range(max(0, idx - 2), idx + 1)]
            rolling_mean = float(statistics.mean(window_vals))
            rolling_std = float(statistics.stdev(window_vals)) if len(window_vals) > 1 else 0.0

            features.append(
                FeatureVector(
                    time_coordinate=round(t_coord, 4),
                    year=obs.year,
                    value=obs.value,
                    rolling_mean_3=round(rolling_mean, 4),
                    rolling_std_3=round(rolling_std, 4),
                )
            )

        return features, min_year, max_year
