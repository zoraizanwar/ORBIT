from datetime import datetime, timezone
from typing import Optional
from app.services.intelligence.exceptions import TemporalCorrelationError
from app.services.intelligence.models import TemporalContextResult


class TemporalCorrelator:
    """
    Deterministic temporal correlation engine evaluating observation intervals and temporal tolerance.
    """

    @classmethod
    def evaluate_temporal_alignment(
        cls,
        start_date: datetime,
        end_date: datetime,
        reference_start: Optional[datetime] = None,
        reference_end: Optional[datetime] = None,
        tolerance_days: int = 45,
    ) -> TemporalContextResult:
        if start_date >= end_date:
            raise TemporalCorrelationError(
                f"Start date ({start_date.isoformat()}) must be strictly earlier than end date ({end_date.isoformat()})"
            )

        interval_days = (end_date - start_date).days

        if reference_start and reference_end:
            start_diff = abs((start_date - reference_start).days)
            end_diff = abs((end_date - reference_end).days)

            if start_diff <= tolerance_days and end_diff <= tolerance_days:
                alignment = "CONGRUENT_WITHIN_TOLERANCE"
            elif (start_date <= reference_end) and (end_date >= reference_start):
                alignment = "PARTIAL_TEMPORAL_OVERLAP"
            else:
                alignment = "TEMPORALLY_DISJOINT"
        else:
            alignment = "AUTHORITATIVE_INTERVAL"

        return TemporalContextResult(
            start_date=start_date,
            end_date=end_date,
            interval_days=interval_days,
            temporal_alignment=alignment,
            temporal_tolerance_days=tolerance_days,
        )
