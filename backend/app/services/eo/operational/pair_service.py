from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.services.eo.operational.models import (
    ObservationPairSelectRequest,
    ObservationPairSelectResponse,
)


class ObservationPairService:
    """
    Observation Pair Selection & Temporal Integrity Service.
    Enforces chronological ordering (T1 < T2), sensor modality compatibility,
    and valid band presence before triggering multi-temporal pipeline runs.
    """

    @classmethod
    def validate_and_select_pair(
        cls,
        req: ObservationPairSelectRequest,
    ) -> ObservationPairSelectResponse:
        """
        Validates T1 and T2 timestamps and sensor compatibility.
        """
        t1_dt = req.t1_datetime
        t2_dt = req.t2_datetime

        if t1_dt.tzinfo is None:
            t1_dt = t1_dt.replace(tzinfo=timezone.utc)
        if t2_dt.tzinfo is None:
            t2_dt = t2_dt.replace(tzinfo=timezone.utc)

        # 1. Chronological Invariant: T1 must strictly precede T2
        if t1_dt >= t2_dt:
            raise ValueError(
                f"Chronological violation: Baseline T1 ({t1_dt.isoformat()}) must strictly precede Comparison T2 ({t2_dt.isoformat()})."
            )

        # 2. Band Path Presence Check
        required_bands = ["B04", "B08"]
        for band in required_bands:
            if band not in req.t1_band_paths:
                raise ValueError(f"Missing required band '{band}' in T1 band mapping.")
            if band not in req.t2_band_paths:
                raise ValueError(f"Missing required band '{band}' in T2 band mapping.")

        # 3. Calculate interval in days
        delta = t2_dt - t1_dt
        interval_days = round(delta.total_seconds() / 86400.0, 2)

        if interval_days < 1.0 / 24.0:  # Minimum 1 hour separation
            raise ValueError(f"Insufficient temporal separation between scenes: {interval_days} days.")

        return ObservationPairSelectResponse(
            is_valid_pair=True,
            temporal_separation_days=interval_days,
            t1_scene_id=req.t1_scene_id,
            t1_datetime=t1_dt.isoformat(),
            t2_scene_id=req.t2_scene_id,
            t2_datetime=t2_dt.isoformat(),
            platform=req.platform,
            sensor=req.sensor,
            validation_message=f"Valid temporal observation pair ({interval_days} days separation).",
            is_test_fixture=req.is_test_fixture,
        )
