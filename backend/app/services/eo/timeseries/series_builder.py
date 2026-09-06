from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import numpy as np

from app.models.enums import EpistemicLevel
from app.services.eo.timeseries.models import (
    TimePointMeasurement,
    TemporalMeasurementSeries,
    MissingObservationGap,
)


def build_temporal_series(
    measurements: List[TimePointMeasurement],
    aoi_id: Optional[str] = None,
    aoi_name: Optional[str] = None,
    gap_threshold_days: int = 60,
) -> TemporalMeasurementSeries:
    """
    Assembles, chronologically orders, and evaluates temporal observation continuity.
    """
    if not measurements:
        return TemporalMeasurementSeries(
            aoi_id=aoi_id,
            aoi_name=aoi_name,
            metric_name="UNKNOWN",
            unit="N/A",
            data_points=[],
            total_observations=0,
            epistemic_level=EpistemicLevel.CALCULATED,
        )

    # 1. Sort Chronologically
    sorted_pts = sorted(measurements, key=lambda p: p.acquisition_datetime)
    metric_name = sorted_pts[0].metric_name
    unit = sorted_pts[0].unit

    start_dt = sorted_pts[0].acquisition_datetime
    end_dt = sorted_pts[-1].acquisition_datetime

    # 2. Detect Observation Gaps
    gaps: List[MissingObservationGap] = []
    for i in range(len(sorted_pts) - 1):
        delta = sorted_pts[i + 1].acquisition_datetime - sorted_pts[i].acquisition_datetime
        days = delta.days
        if days > gap_threshold_days:
            gaps.append(
                MissingObservationGap(
                    gap_start=sorted_pts[i].acquisition_datetime,
                    gap_end=sorted_pts[i + 1].acquisition_datetime,
                    duration_days=days,
                    reason="OBSERVATION_INTERVAL_GAP",
                )
            )

    # 3. Simple Annual Slope Estimation (Ordinary Least Squares if >= 2 points)
    slope_per_year: Optional[float] = None
    if len(sorted_pts) >= 2:
        t0 = sorted_pts[0].acquisition_datetime.timestamp()
        t_years = np.array([(p.acquisition_datetime.timestamp() - t0) / (365.25 * 86400.0) for p in sorted_pts])
        y_vals = np.array([p.value for p in sorted_pts])

        if np.max(t_years) > 0.01:
            try:
                poly = np.polyfit(t_years, y_vals, 1)
                slope_per_year = round(float(poly[0]), 4)
            except Exception:
                slope_per_year = None

    quality_summary = {
        "mean_cloud_cover": round(
            float(np.mean([p.cloud_cover for p in sorted_pts if p.cloud_cover is not None])), 2
        ) if any(p.cloud_cover is not None for p in sorted_pts) else None,
        "mean_valid_pixel_pct": round(float(np.mean([p.valid_pixel_percentage for p in sorted_pts])), 2),
        "total_gaps_detected": len(gaps),
    }

    return TemporalMeasurementSeries(
        aoi_id=aoi_id,
        aoi_name=aoi_name,
        metric_name=metric_name,
        unit=unit,
        data_points=sorted_pts,
        total_observations=len(sorted_pts),
        temporal_coverage_start=start_dt,
        temporal_coverage_end=end_dt,
        trend_slope_per_year=slope_per_year,
        observation_gaps=gaps,
        quality_summary=quality_summary,
        epistemic_level=EpistemicLevel.CALCULATED,
    )
