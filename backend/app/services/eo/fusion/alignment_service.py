import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from app.services.eo.fusion.models import (
    ObservationSource,
    AlignmentReport,
    AlignmentStatus,
)


class TemporalWindowService:
    """
    Evaluates temporal proximity between multi-source observations.
    Supports conservative configurable windows (+-3, +-7, +-14, +-30 days).
    Preserves exact acquisition timestamps.
    """

    DEFAULT_TOLERANCE_DAYS = 14.0

    @classmethod
    def calculate_offset_days(cls, t1: datetime, t2: datetime) -> float:
        """Calculates absolute temporal offset in fractional days."""
        delta = abs((t2 - t1).total_seconds())
        return round(delta / 86400.0, 4)

    @classmethod
    def is_within_window(
        cls,
        t1: datetime,
        t2: datetime,
        window_days: float = DEFAULT_TOLERANCE_DAYS,
    ) -> bool:
        """Checks if two timestamps are within the specified temporal window."""
        return cls.calculate_offset_days(t1, t2) <= window_days


class SpatialResolutionService:
    """
    Evaluates GSD (Ground Sampling Distance) between observations.
    Determines compatibility and records transformation provenance when resampling is required.
    """

    SAME_RESOLUTION_THRESHOLD = 0.05  # within 5% ratio is considered identical
    COMPATIBLE_RATIO_MAX = 4.0        # up to 4x ratio (e.g., 10m to 30m) is compatible

    @classmethod
    def evaluate_resolution_compatibility(
        cls,
        gsd_source: float,
        gsd_target: float,
    ) -> Tuple[str, float, bool, Optional[str]]:
        """
        Returns (compatibility_status, ratio, needs_resampling, suggested_method).
        """
        if gsd_source <= 0 or gsd_target <= 0 or math.isnan(gsd_source) or math.isnan(gsd_target):
            return "MISMATCH", float("inf"), False, None

        ratio = round(max(gsd_source, gsd_target) / min(gsd_source, gsd_target), 3)

        if abs(ratio - 1.0) <= cls.SAME_RESOLUTION_THRESHOLD:
            return "IDENTICAL", ratio, False, None
        elif ratio <= cls.COMPATIBLE_RATIO_MAX:
            return "COMPATIBLE", ratio, True, "BILINEAR_AREA_WEIGHTED"
        else:
            return "MISMATCH", ratio, True, "INCOMPATIBLE_RESOLUTION_MISMATCH"


class ObservationAlignmentService:
    """
    Multi-Source Observation Alignment Engine.
    Aligns observations based on spatial overlap, temporal proximity, compatible CRS,
    and resolution limits. Never silently transforms incompatible observations.
    """

    @classmethod
    def compute_bbox_overlap_percentage(
        cls,
        bbox1: List[float],
        bbox2: List[float],
    ) -> float:
        """
        Computes intersection over union (IoU) / overlap percentage between two WGS84 bounding boxes.
        Format: [min_lon, min_lat, max_lon, max_lat]
        """
        if len(bbox1) != 4 or len(bbox2) != 4:
            return 0.0

        min_x1, min_y1, max_x1, max_y1 = bbox1
        min_x2, min_y2, max_x2, max_y2 = bbox2

        inter_min_x = max(min_x1, min_x2)
        inter_min_y = max(min_y1, min_y2)
        inter_max_x = min(max_x1, max_x2)
        inter_max_y = min(max_y1, max_y2)

        if inter_min_x >= inter_max_x or inter_min_y >= inter_max_y:
            return 0.0

        inter_area = (inter_max_x - inter_min_x) * (inter_max_y - inter_min_y)
        area1 = (max_x1 - min_x1) * (max_y1 - min_y1)
        area2 = (max_x2 - min_x2) * (max_y2 - min_y2)

        if area1 <= 0 or area2 <= 0:
            return 0.0

        min_area = min(area1, area2)
        overlap_pct = (inter_area / min_area) * 100.0
        return round(min(overlap_pct, 100.0), 2)

    @classmethod
    def align_observations(
        cls,
        source: ObservationSource,
        target: ObservationSource,
        temporal_window_days: float = 14.0,
        min_spatial_overlap_pct: float = 10.0,
    ) -> AlignmentReport:
        """
        Executes strict multi-criteria alignment between two candidate observations.
        """
        reasons: List[str] = []
        is_fixture = source.is_test_fixture or target.is_test_fixture

        # 1. Temporal Check
        offset_days = TemporalWindowService.calculate_offset_days(
            source.acquisition_datetime,
            target.acquisition_datetime,
        )
        is_temporal_ok = offset_days <= temporal_window_days
        if not is_temporal_ok:
            reasons.append(
                f"Temporal offset {offset_days:.1f} days exceeds max window {temporal_window_days:.1f} days"
            )

        # 2. Spatial Overlap Check
        overlap_pct = cls.compute_bbox_overlap_percentage(source.bbox, target.bbox)
        is_spatial_ok = overlap_pct >= min_spatial_overlap_pct
        if not is_spatial_ok:
            reasons.append(
                f"Spatial overlap {overlap_pct:.1f}% below minimum threshold {min_spatial_overlap_pct:.1f}%"
            )

        # 3. CRS Check
        is_crs_ok = (source.crs.upper() == target.crs.upper())
        if not is_crs_ok:
            reasons.append(f"CRS mismatch: {source.crs} vs {target.crs}")

        # 4. Resolution Check
        res_status, res_ratio, needs_resample, resample_method = (
            SpatialResolutionService.evaluate_resolution_compatibility(
                source.gsd_meters,
                target.gsd_meters,
            )
        )
        if res_status == "MISMATCH":
            reasons.append(
                f"GSD resolution ratio {res_ratio:.1f}x exceeds maximum compatible limit (4.0x)"
            )

        # 5. Determine Overall Status
        if is_temporal_ok and is_spatial_ok and is_crs_ok and res_status != "MISMATCH":
            if res_status == "IDENTICAL" and overlap_pct >= 80.0:
                status = AlignmentStatus.ALIGNED
            else:
                status = AlignmentStatus.PARTIALLY_ALIGNED
        else:
            status = AlignmentStatus.INCOMPATIBLE

        return AlignmentReport(
            source_observation_id=source.id,
            target_observation_id=target.id,
            temporal_offset_days=offset_days,
            spatial_overlap_percentage=overlap_pct,
            source_gsd_m=source.gsd_meters,
            target_gsd_m=target.gsd_meters,
            resolution_ratio=res_ratio,
            status=status,
            reasons=reasons,
            resampling_applied=needs_resample and status != AlignmentStatus.INCOMPATIBLE,
            resampling_method=resample_method if needs_resample and status != AlignmentStatus.INCOMPATIBLE else None,
            is_test_fixture=is_fixture,
        )
