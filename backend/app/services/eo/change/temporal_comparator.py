from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.models.enums import EpistemicLevel
from app.services.eo.change.exceptions import (
    IncompatibleMeasurementsError,
    IncompatibleSensorsError,
    IncompatibleUnitsError,
    TemporalOrderError,
    InsufficientDataError,
)
from app.services.eo.change.models import (
    TemporalObservationPair,
    ChangeComparisonResult,
)
from app.services.eo.change.thresholds import (
    ChangeMetric,
    ChangeClass,
    ChangeThresholdConfig,
    get_default_thresholds_for_metric,
)
from app.services.eo.raster.band_resolver import normalize_sensor_family


class TemporalComparator:
    """
    Deterministic Pairwise Temporal Comparison Engine for Earth Observation measurements.
    """

    @classmethod
    def compare_observations(
        cls,
        pair: TemporalObservationPair,
    ) -> ChangeComparisonResult:
        m1 = pair.measurement_t1
        m2 = pair.measurement_t2

        # 1. Temporal Ordering Validation
        if m1.acquisition_datetime >= m2.acquisition_datetime:
            raise TemporalOrderError(
                f"T1 acquisition date ({m1.acquisition_datetime.isoformat()}) "
                f"must be strictly earlier than T2 ({m2.acquisition_datetime.isoformat()})"
            )

        # 2. Metric & Unit Compatibility
        # Normalize metric name
        metric_str = m1.metric_name.upper().replace("_MEAN", "")
        m2_metric_str = m2.metric_name.upper().replace("_MEAN", "")

        if metric_str != m2_metric_str:
            raise IncompatibleMeasurementsError(
                f"Cannot compare mismatched metrics: T1 has '{m1.metric_name}', T2 has '{m2.metric_name}'"
            )

        if m1.unit.lower() != m2.unit.lower():
            raise IncompatibleUnitsError(
                f"Cannot compare mismatched units: T1 has '{m1.unit}', T2 has '{m2.unit}'"
            )

        # Match to ChangeMetric enum
        try:
            matched_metric = ChangeMetric(metric_str)
        except ValueError:
            matched_metric = ChangeMetric.CUSTOM

        # 3. Resolve Threshold Configuration
        threshold_cfg = pair.threshold_config or get_default_thresholds_for_metric(matched_metric)

        # 4. Sensor Compatibility Validation
        s1_family = normalize_sensor_family(m1.platform)
        s2_family = normalize_sensor_family(m2.platform)

        if not threshold_cfg.allow_cross_sensor and s1_family != s2_family:
            raise IncompatibleSensorsError(
                f"Sensor cross-comparison not permitted between {s1_family} and {s2_family}"
            )

        # Optical vs SAR cross-comparison protection
        is_s1_sar = "SAR" in s1_family or "SENTINEL-1" in s1_family
        is_s2_sar = "SAR" in s2_family or "SENTINEL-1" in s2_family
        if is_s1_sar != is_s2_sar:
            raise IncompatibleSensorsError(
                f"Direct spectral comparison between SAR ({s1_family}) and Optical ({s2_family}) is invalid."
            )

        # 5. Quality & Cloud Cover Checks
        quality_assessment = {
            "t1_valid_pixel_pct": m1.valid_pixel_percentage,
            "t2_valid_pixel_pct": m2.valid_pixel_percentage,
            "t1_cloud_cover": m1.cloud_cover,
            "t2_cloud_cover": m2.cloud_cover,
            "sensor_family_t1": s1_family,
            "sensor_family_t2": s2_family,
            "quality_status": "PASSED",
        }

        if (
            m1.valid_pixel_percentage < threshold_cfg.min_valid_pixel_percentage
            or m2.valid_pixel_percentage < threshold_cfg.min_valid_pixel_percentage
        ):
            quality_assessment["quality_status"] = "LOW_VALID_PIXELS"

        if (m1.cloud_cover is not None and m1.cloud_cover > threshold_cfg.max_cloud_cover_percentage) or (
            m2.cloud_cover is not None and m2.cloud_cover > threshold_cfg.max_cloud_cover_percentage
        ):
            quality_assessment["quality_status"] = "HIGH_CLOUD_COVER"

        # 6. Delta and Percentage Change Calculations
        abs_delta = round(m2.value - m1.value, 4)

        # Handle relative/percentage change with safe zero-denominator handling
        if abs(m1.value) > 1e-5:
            rel_change = round(abs_delta / abs(m1.value), 4)
            pct_change = round(rel_change * 100.0, 2)
        else:
            rel_change = None
            pct_change = None

        # 7. Deterministic Classification
        if quality_assessment["quality_status"] != "PASSED":
            classification = ChangeClass.INSUFFICIENT_DATA
            is_sig = False
        elif abs_delta >= threshold_cfg.significant_increase_threshold:
            classification = ChangeClass.SIGNIFICANT_INCREASE
            is_sig = True
        elif abs_delta >= threshold_cfg.increase_threshold:
            classification = ChangeClass.INCREASE
            is_sig = False
        elif abs_delta <= threshold_cfg.significant_decrease_threshold:
            classification = ChangeClass.SIGNIFICANT_DECREASE
            is_sig = True
        elif abs_delta <= threshold_cfg.decrease_threshold:
            classification = ChangeClass.DECREASE
            is_sig = False
        else:
            classification = ChangeClass.NO_CHANGE
            is_sig = False

        # Calculate interval in days
        interval_days = (m2.acquisition_datetime - m1.acquisition_datetime).days

        # 8. Provenance Trace
        now_utc = datetime.now(timezone.utc).isoformat()
        provenance = {
            "algorithm": "ORBIT Multi-Temporal Comparison Engine v1.0",
            "t1_scene_id": m1.source_scene_id,
            "t2_scene_id": m2.source_scene_id,
            "t1_acquisition": m1.acquisition_datetime.isoformat(),
            "t2_acquisition": m2.acquisition_datetime.isoformat(),
            "metric": matched_metric.value,
            "threshold_version": threshold_cfg.threshold_version,
            "thresholds": threshold_cfg.model_dump(),
            "calculation_formula": "delta = V_t2 - V_t1; pct = (delta / |V_t1|) * 100",
            "epistemic_level": "CALCULATED",
            "calculated_at": now_utc,
        }

        return ChangeComparisonResult(
            aoi_id=pair.aoi_id,
            aoi_name=pair.aoi_name,
            metric=matched_metric,
            unit=m1.unit,
            t1_acquisition=m1.acquisition_datetime,
            t2_acquisition=m2.acquisition_datetime,
            interval_days=interval_days,
            t1_scene_id=m1.source_scene_id,
            t2_scene_id=m2.source_scene_id,
            t1_platform=m1.platform,
            t2_platform=m2.platform,
            t1_value=m1.value,
            t2_value=m2.value,
            absolute_delta=abs_delta,
            relative_change=rel_change,
            percentage_change=pct_change,
            classification=classification,
            is_significant=is_sig,
            threshold_used=threshold_cfg.model_dump(),
            quality_assessment=quality_assessment,
            provenance=provenance,
            epistemic_level=EpistemicLevel.CALCULATED,
        )
