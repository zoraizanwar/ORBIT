import math
from typing import List, Tuple, Dict
from app.models.enums import EpistemicLevel
from app.services.forecasting.models import (
    HistoricalObservation,
    QualityFilterReport,
)


class QualityFilterPipeline:
    """
    Deterministic quality filtering pipeline for historical time-series observations.
    Filters invalid numeric values, excessive cloud cover, insufficient valid pixels,
    and invalid epistemic levels.
    """

    @classmethod
    def filter_observations(
        cls,
        observations: List[HistoricalObservation],
        max_cloud_cover: float = 30.0,
        min_valid_pixel_pct: float = 80.0,
    ) -> Tuple[List[HistoricalObservation], QualityFilterReport]:
        accepted: List[HistoricalObservation] = []
        reasons: Dict[str, int] = {}
        seen_timestamps = set()

        for obs in observations:
            # 1. Epistemic level check (PREDICTED is strictly forbidden as historical training input)
            if obs.epistemic_level == EpistemicLevel.PREDICTED:
                reasons["PREDICTED_EPISTEMIC_LEVEL_LEAKAGE"] = (
                    reasons.get("PREDICTED_EPISTEMIC_LEVEL_LEAKAGE", 0) + 1
                )
                continue

            # 2. Value finite & not NaN / Inf
            if obs.value is None or math.isnan(obs.value) or math.isinf(obs.value):
                reasons["NON_FINITE_OR_NAN_VALUE"] = (
                    reasons.get("NON_FINITE_OR_NAN_VALUE", 0) + 1
                )
                continue

            # 3. Duplicate timestamp rejection
            ts_key = obs.acquisition_datetime.isoformat()
            if ts_key in seen_timestamps:
                reasons["DUPLICATE_TIMESTAMP"] = (
                    reasons.get("DUPLICATE_TIMESTAMP", 0) + 1
                )
                continue

            # 4. Valid pixel percentage check
            if obs.valid_pixel_pct < min_valid_pixel_pct:
                reasons["INSUFFICIENT_VALID_PIXELS"] = (
                    reasons.get("INSUFFICIENT_VALID_PIXELS", 0) + 1
                )
                continue

            # 5. Cloud cover check (Optical only; SAR cloud_cover is None and passes safely)
            if obs.cloud_cover is not None and obs.cloud_cover > max_cloud_cover:
                reasons["EXCESSIVE_CLOUD_COVER"] = (
                    reasons.get("EXCESSIVE_CLOUD_COVER", 0) + 1
                )
                continue

            # Observation passed all quality gates
            seen_timestamps.add(ts_key)
            accepted.append(obs)

        # Sort chronologically
        accepted.sort(key=lambda x: x.acquisition_datetime)

        report = QualityFilterReport(
            total_raw_observations=len(observations),
            accepted_count=len(accepted),
            rejected_count=len(observations) - len(accepted),
            rejection_reasons=reasons,
            validity_status="PASSED" if len(accepted) > 0 else "ALL_REJECTED",
        )

        return accepted, report
