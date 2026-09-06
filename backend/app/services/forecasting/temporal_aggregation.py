import statistics
from collections import defaultdict
from datetime import datetime, timezone
from typing import List
from app.models.enums import EpistemicLevel
from app.services.forecasting.models import (
    HistoricalObservation,
    TemporalResolution,
    AggregationMethod,
    AggregatedObservation,
)


class TemporalAggregator:
    """
    Deterministic temporal aggregation engine.
    Aggregates point observations into standardized monthly, quarterly, or annual series.
    """

    @classmethod
    def aggregate_series(
        cls,
        observations: List[HistoricalObservation],
        resolution: TemporalResolution = TemporalResolution.ANNUAL,
        method: AggregationMethod = AggregationMethod.MEDIAN,
    ) -> List[AggregatedObservation]:
        if not observations:
            return []

        buckets = defaultdict(list)

        for obs in observations:
            dt = obs.acquisition_datetime
            year = dt.year

            if resolution == TemporalResolution.ANNUAL:
                key = f"{year}"
                month = None
                quarter = None
            elif resolution == TemporalResolution.QUARTERLY:
                q = (dt.month - 1) // 3 + 1
                key = f"{year}-Q{q}"
                month = None
                quarter = q
            else:  # MONTHLY
                m = dt.month
                key = f"{year}-{m:02d}"
                month = m
                quarter = (m - 1) // 3 + 1

            buckets[(key, year, month, quarter)].append(obs)

        result: List[AggregatedObservation] = []

        for (key, year, month, quarter), obs_list in sorted(buckets.items(), key=lambda x: x[0][0]):
            values = [o.value for o in obs_list]
            if method == AggregationMethod.MEDIAN:
                agg_val = float(statistics.median(values))
            elif method == AggregationMethod.MEAN:
                agg_val = float(statistics.mean(values))
            else:  # SUM
                agg_val = float(sum(values))

            date_start = min(o.acquisition_datetime for o in obs_list)
            date_end = max(o.acquisition_datetime for o in obs_list)

            result.append(
                AggregatedObservation(
                    period_key=key,
                    year=year,
                    month=month,
                    quarter=quarter,
                    value=round(agg_val, 4),
                    observation_count=len(obs_list),
                    aggregation_method=method,
                    date_start=date_start,
                    date_end=date_end,
                    epistemic_level=EpistemicLevel.CALCULATED,
                    source_observation_ids=[o.id for o in obs_list],
                )
            )

        return result
