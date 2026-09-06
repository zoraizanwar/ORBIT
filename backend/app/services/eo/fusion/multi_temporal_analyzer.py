from datetime import datetime
from typing import Any, Dict, List, Optional
from app.services.eo.fusion.models import (
    ObservationMeasurement,
    MultiTemporalSeriesAnalysis,
    TemporalStepAnalysis,
    TemporalSeriesState,
)


class MultiTemporalChangeAnalyzer:
    """
    Multi-Temporal Earth Observation Change Series Analyzer.
    Analyzes temporal trajectories (T1 -> T2 -> ... -> Tn) across sequential observations.
    Computes absolute/relative deltas, directional persistence, recovery, and oscillation.
    Strictly deterministic; never infers causality or fabricates observations.
    """

    RULE_ID = "RULE-MULTI-TEMPORAL-SERIES-001"
    ALGORITHM_VERSION = "ORBIT-MultiTemporal-v1.0.0"
    THRESHOLD_VERSION = "v1.0"
    SIGNIFICANT_DELTA_THRESHOLD = 0.05
    RECOVERY_REBOUND_RATIO = 0.50

    @classmethod
    def analyze_series(
        cls,
        metric_name: str,
        measurements: List[ObservationMeasurement],
    ) -> MultiTemporalSeriesAnalysis:
        """
        Analyzes a chronological sequence of measurements for a specific metric.
        """
        # Filter valid measurements with non-null values
        valid_meas = [m for m in measurements if m.value is not None]
        
        # Sort chronologically by timestamp
        valid_meas.sort(key=lambda m: m.timestamp)

        obs_count = len(measurements)
        valid_count = len(valid_meas)

        if valid_count < 2:
            base_val = valid_meas[0].value if valid_meas else 0.0
            return MultiTemporalSeriesAnalysis(
                metric=metric_name,
                observation_count=obs_count,
                valid_observation_count=valid_count,
                time_span_days=0.0,
                baseline_value=base_val,
                latest_value=base_val,
                net_absolute_delta=0.0,
                net_relative_delta_percentage=0.0,
                overall_state=TemporalSeriesState.INSUFFICIENT_DATA,
                persistence_ratio=0.0,
                recovery_detected=False,
                steps=[],
                rule_id=cls.RULE_ID,
                algorithm_version=cls.ALGORITHM_VERSION,
                threshold_version=cls.THRESHOLD_VERSION,
            )

        baseline_val = valid_meas[0].value
        latest_val = valid_meas[-1].value
        net_abs_delta = round(latest_val - baseline_val, 4)
        net_rel_pct = round(
            (net_abs_delta / abs(baseline_val) * 100.0) if baseline_val != 0 else 0.0,
            2,
        )

        t_start_dt = valid_meas[0].timestamp
        t_end_dt = valid_meas[-1].timestamp
        total_time_span_days = round((t_end_dt - t_start_dt).total_seconds() / 86400.0, 2)

        # Build step-by-step analysis
        steps: List[TemporalStepAnalysis] = []
        consecutive_same_direction_count = 0
        direction_changes = 0
        prev_direction: Optional[str] = None
        min_val = baseline_val
        max_val = baseline_val

        for i in range(len(valid_meas) - 1):
            m1 = valid_meas[i]
            m2 = valid_meas[i + 1]

            step_delta = round(m2.value - m1.value, 4)
            step_rel = round(
                (step_delta / abs(m1.value) * 100.0) if m1.value != 0 else 0.0,
                2,
            )
            step_days = round((m2.timestamp - m1.timestamp).total_seconds() / 86400.0, 2)

            if abs(step_delta) < cls.SIGNIFICANT_DELTA_THRESHOLD:
                direction = "STABLE"
            elif step_delta > 0:
                direction = "INCREASING"
            else:
                direction = "DECREASING"

            if prev_direction and direction != "STABLE" and prev_direction != "STABLE":
                if direction != prev_direction:
                    direction_changes += 1

            if direction != "STABLE":
                prev_direction = direction

            min_val = min(min_val, m2.value)
            max_val = max(max_val, m2.value)

            steps.append(
                TemporalStepAnalysis(
                    step_index=i + 1,
                    t_start=m1.timestamp.isoformat(),
                    t_end=m2.timestamp.isoformat(),
                    delta_days=step_days,
                    start_value=m1.value,
                    end_value=m2.value,
                    absolute_delta=step_delta,
                    relative_delta_percentage=step_rel,
                    step_direction=direction,
                )
            )

        # Detect recovery (e.g. drop from 0.85 -> 0.40 then rebound to 0.70)
        recovery_detected = False
        if len(valid_meas) >= 3 and baseline_val > 0.5:
            # Check if there was a sharp drop and then a recovery of at least RECOVERY_REBOUND_RATIO of the drop
            drop_mag = baseline_val - min_val
            rebound_mag = latest_val - min_val
            if drop_mag >= cls.SIGNIFICANT_DELTA_THRESHOLD * 2 and rebound_mag >= drop_mag * cls.RECOVERY_REBOUND_RATIO:
                recovery_detected = True

        # Determine overall series state
        non_stable_steps = [s for s in steps if s.step_direction != "STABLE"]
        dec_steps = [s for s in steps if s.step_direction == "DECREASING"]
        inc_steps = [s for s in steps if s.step_direction == "INCREASING"]

        if recovery_detected:
            state = TemporalSeriesState.RECOVERY
        elif direction_changes >= 2:
            state = TemporalSeriesState.OSCILLATING
        elif len(dec_steps) >= 2 and len(inc_steps) == 0:
            state = TemporalSeriesState.PERSISTENT_CHANGE
        elif len(inc_steps) >= 2 and len(dec_steps) == 0:
            state = TemporalSeriesState.PERSISTENT_CHANGE
        elif len(dec_steps) == 1 and len(steps) >= 2 and abs(net_abs_delta) < cls.SIGNIFICANT_DELTA_THRESHOLD:
            state = TemporalSeriesState.TEMPORARY_CHANGE
        elif net_abs_delta <= -cls.SIGNIFICANT_DELTA_THRESHOLD:
            state = TemporalSeriesState.DECREASING
        elif net_abs_delta >= cls.SIGNIFICANT_DELTA_THRESHOLD:
            state = TemporalSeriesState.INCREASING
        else:
            state = TemporalSeriesState.NO_CHANGE

        persistence_ratio = round(
            (max(len(dec_steps), len(inc_steps)) / len(steps)) if steps else 0.0,
            2,
        )

        return MultiTemporalSeriesAnalysis(
            metric=metric_name,
            observation_count=obs_count,
            valid_observation_count=valid_count,
            time_span_days=total_time_span_days,
            baseline_value=baseline_val,
            latest_value=latest_val,
            net_absolute_delta=net_abs_delta,
            net_relative_delta_percentage=net_rel_pct,
            overall_state=state,
            persistence_ratio=persistence_ratio,
            recovery_detected=recovery_detected,
            steps=steps,
            rule_id=cls.RULE_ID,
            algorithm_version=cls.ALGORITHM_VERSION,
            threshold_version=cls.THRESHOLD_VERSION,
        )
