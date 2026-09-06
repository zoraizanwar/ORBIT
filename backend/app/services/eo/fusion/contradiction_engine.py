import uuid
from typing import Any, Dict, List, Optional
from app.services.eo.fusion.models import (
    ObservationMeasurement,
    ContradictionFinding,
    FusionRelationship,
)


class CrossSensorContradictionEngine:
    """
    Cross-Sensor Geospatial Contradiction & Corroboration Engine.
    Evaluates multi-modal signals (Optical MSI, SAR C-band, OSM vector infrastructure).
    Identifies agreement, discrepancies, and sensor contradictions without erasing conflicting data.
    """

    @classmethod
    def evaluate_cross_sensor_evidence(
        cls,
        optical_measurements: Dict[str, float],
        sar_measurements: Optional[Dict[str, float]] = None,
        infrastructure_context: Optional[Dict[str, Any]] = None,
        observation_ids: Optional[List[str]] = None,
    ) -> List[ContradictionFinding]:
        """
        Evaluates cross-sensor signals and returns structured contradiction/corroboration findings.
        """
        findings: List[ContradictionFinding] = []
        obs_ids = observation_ids or ["obs-optical-001", "obs-sar-001"]

        ndvi_delta = optical_measurements.get("NDVI_DELTA", 0.0)
        ndwi_delta = optical_measurements.get("NDWI_DELTA", 0.0)
        ndbi_delta = optical_measurements.get("NDBI_DELTA", 0.0)

        sar_delta_vv = (sar_measurements or {}).get("VV_DELTA", 0.0)
        sar_current_vv = (sar_measurements or {}).get("VV_CURRENT", -12.0)
        road_distance_m = (infrastructure_context or {}).get("nearest_road_distance_meters", 500.0)

        # 1. Optical Vegetation Decline vs SAR Structural Stability
        if ndvi_delta <= -0.25 and sar_measurements is not None:
            if abs(sar_delta_vv) < 0.5:
                findings.append(
                    ContradictionFinding(
                        finding_id=f"FINDING-{uuid.uuid4().hex[:8]}",
                        relationship=FusionRelationship.CONTRADICTED,
                        primary_sensor="Sentinel-2 MSI (Optical)",
                        primary_metric="NDVI_DELTA",
                        primary_value=ndvi_delta,
                        secondary_sensor="Sentinel-1 C-SAR (Microwave)",
                        secondary_metric="VV_DELTA",
                        secondary_value=sar_delta_vv,
                        explanation=(
                            f"Strong optical canopy decline (ΔNDVI={ndvi_delta:.3f}) is contradicted "
                            f"by stable SAR structural backscatter (ΔVV={sar_delta_vv:.2f} dB). "
                            "Potential cause: seasonal phenology, moisture variation, or sensor artifact."
                        ),
                        evidence_ids=obs_ids,
                    )
                )
            elif sar_delta_vv <= -2.0:
                findings.append(
                    ContradictionFinding(
                        finding_id=f"FINDING-{uuid.uuid4().hex[:8]}",
                        relationship=FusionRelationship.CORROBORATED,
                        primary_sensor="Sentinel-2 MSI (Optical)",
                        primary_metric="NDVI_DELTA",
                        primary_value=ndvi_delta,
                        secondary_sensor="Sentinel-1 C-SAR (Microwave)",
                        secondary_metric="VV_DELTA",
                        secondary_value=sar_delta_vv,
                        explanation=(
                            f"Optical vegetation decline (ΔNDVI={ndvi_delta:.3f}) is corroborated "
                            f"by structural roughness loss in SAR backscatter (ΔVV={sar_delta_vv:.2f} dB)."
                        ),
                        evidence_ids=obs_ids,
                    )
                )

        # 2. Optical Water Decline vs SAR Persistent Specular Reflection
        if ndwi_delta <= -0.30 and sar_measurements is not None:
            if sar_current_vv < -18.0:
                findings.append(
                    ContradictionFinding(
                        finding_id=f"FINDING-{uuid.uuid4().hex[:8]}",
                        relationship=FusionRelationship.CONTRADICTED,
                        primary_sensor="Sentinel-2 MSI (Optical)",
                        primary_metric="NDWI_DELTA",
                        primary_value=ndwi_delta,
                        secondary_sensor="Sentinel-1 C-SAR (Microwave)",
                        secondary_metric="VV_CURRENT",
                        secondary_value=sar_current_vv,
                        explanation=(
                            f"Optical water loss signal (ΔNDWI={ndwi_delta:.3f}) contradicted by "
                            f"persistent smooth-water SAR backscatter (VV={sar_current_vv:.1f} dB)."
                        ),
                        evidence_ids=obs_ids,
                    )
                )

        # 3. Built-up Expansion vs Road Corridor Proximity
        if ndbi_delta >= 0.20:
            if road_distance_m <= 1500.0:
                findings.append(
                    ContradictionFinding(
                        finding_id=f"FINDING-{uuid.uuid4().hex[:8]}",
                        relationship=FusionRelationship.CORROBORATED,
                        primary_sensor="Sentinel-2 MSI (Optical)",
                        primary_metric="NDBI_DELTA",
                        primary_value=ndbi_delta,
                        secondary_sensor="OpenStreetMap (Vector Infrastructure)",
                        secondary_metric="ROAD_DISTANCE_METERS",
                        secondary_value=float(road_distance_m),
                        explanation=(
                            f"Built-up expansion (ΔNDBI={ndbi_delta:.3f}) is corroborated by "
                            f"proximity to active road corridor ({road_distance_m:.0f}m)."
                        ),
                        evidence_ids=obs_ids,
                    )
                )
            elif road_distance_m > 5000.0:
                findings.append(
                    ContradictionFinding(
                        finding_id=f"FINDING-{uuid.uuid4().hex[:8]}",
                        relationship=FusionRelationship.CONTRADICTED,
                        primary_sensor="Sentinel-2 MSI (Optical)",
                        primary_metric="NDBI_DELTA",
                        primary_value=ndbi_delta,
                        secondary_sensor="OpenStreetMap (Vector Infrastructure)",
                        secondary_metric="ROAD_DISTANCE_METERS",
                        secondary_value=float(road_distance_m),
                        explanation=(
                            f"Built-up signal (ΔNDBI={ndbi_delta:.3f}) lacks supporting road infrastructure "
                            f"(isolated location, {road_distance_m:.0f}m from nearest road corridor)."
                        ),
                        evidence_ids=obs_ids,
                    )
                )

        # 4. Default Corroboration if canopy decline aligns with road corridor
        if ndvi_delta <= -0.20 and road_distance_m <= 2000.0 and not findings:
            findings.append(
                ContradictionFinding(
                    finding_id=f"FINDING-{uuid.uuid4().hex[:8]}",
                    relationship=FusionRelationship.CORROBORATED,
                    primary_sensor="Sentinel-2 MSI (Optical)",
                    primary_metric="NDVI_DELTA",
                    primary_value=ndvi_delta,
                    secondary_sensor="OpenStreetMap (Vector Infrastructure)",
                    secondary_metric="ROAD_DISTANCE_METERS",
                    secondary_value=float(road_distance_m),
                    explanation=(
                        f"Significant canopy loss (ΔNDVI={ndvi_delta:.3f}) strongly correlates "
                        f"with proximity to primary transport infrastructure ({road_distance_m:.0f}m)."
                    ),
                    evidence_ids=obs_ids,
                )
            )

        return findings
