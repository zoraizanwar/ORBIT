import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.models.enums import EpistemicLevel, EvidenceStrength
from app.services.intelligence.models import (
    IntelligenceType,
    EvidenceType,
    EvidenceRelationshipType,
    EvidenceNode,
    EvidenceEdge,
    EvidenceGraphResult,
    RuleEvaluationInput,
    SpatialContextResult,
    TemporalContextResult,
    IntelligenceObjectResult,
)


class DeterministicRuleEngine:
    """
    Deterministic Geospatial Intelligence Rule Engine.
    Correlates multi-spectral indices, spatial infrastructure context, and sensor telemetry.
    """

    @classmethod
    def evaluate_rules(
        cls,
        payload: RuleEvaluationInput,
        spatial_context: SpatialContextResult,
        temporal_context: TemporalContextResult,
        analysis_run_id: str,
    ) -> IntelligenceObjectResult:
        """
        Executes deterministic rule hierarchy against input metrics and spatial context.
        """
        nodes: List[EvidenceNode] = []
        edges: List[EvidenceEdge] = []
        contradictions = 0

        # Root intelligence ID
        intel_id = str(uuid.uuid4())
        intel_node = EvidenceNode(
            id=intel_id,
            node_type=EvidenceType.ANALYSIS_RESULT,
            label="Root Intelligence Object",
            source_identifier=f"analysis_run:{analysis_run_id}",
            epistemic_level=EpistemicLevel.CALCULATED,
            evidence_strength=EvidenceStrength.STRONG,
            acquisition_datetime=payload.target_end_date,
        )
        nodes.append(intel_node)

        # 1. Evaluate Rule 1: Multi-Indicator Urban Expansion (dNDVI drop + dNDBI rise)
        if (
            payload.ndvi_delta is not None
            and payload.ndbi_delta is not None
            and payload.ndvi_delta <= -0.10
            and payload.ndbi_delta >= 0.08
        ):
            rule_id = "RULE_MULTI_URBAN_EXPANSION_v1"
            intel_type = IntelligenceType.URBAN_EXPANSION
            title = f"Multi-Indicator Urban Expansion Candidate ({payload.affected_area_km2:.2f} km²)"
            evidence_sources_count = 2

            # Node for NDVI evidence
            ndvi_node_id = f"ev-ndvi-{str(uuid.uuid4())[:8]}"
            nodes.append(
                EvidenceNode(
                    id=ndvi_node_id,
                    node_type=EvidenceType.CHANGE_EVENT,
                    label="dNDVI Canopy Deficit",
                    source_identifier=payload.primary_sensor,
                    epistemic_level=EpistemicLevel.CALCULATED,
                    evidence_strength=EvidenceStrength.STRONG,
                    properties={"delta": payload.ndvi_delta, "metric": "NDVI"},
                )
            )
            edges.append(
                EvidenceEdge(
                    source_node_id=ndvi_node_id,
                    target_node_id=intel_id,
                    relationship_type=EvidenceRelationshipType.SUPPORTS,
                )
            )

            # Node for NDBI evidence
            ndbi_node_id = f"ev-ndbi-{str(uuid.uuid4())[:8]}"
            nodes.append(
                EvidenceNode(
                    id=ndbi_node_id,
                    node_type=EvidenceType.CHANGE_EVENT,
                    label="dNDBI Built-up Influx",
                    source_identifier=payload.primary_sensor,
                    epistemic_level=EpistemicLevel.CALCULATED,
                    evidence_strength=EvidenceStrength.STRONG,
                    properties={"delta": payload.ndbi_delta, "metric": "NDBI"},
                )
            )
            edges.append(
                EvidenceEdge(
                    source_node_id=ndbi_node_id,
                    target_node_id=intel_id,
                    relationship_type=EvidenceRelationshipType.CORROBORATES,
                )
            )

        # 2. Evaluate Rule 4: Infrastructure Road Corridor Proximity (dNDVI loss near road)
        elif (
            payload.ndvi_delta is not None
            and payload.ndvi_delta <= -0.10
            and spatial_context.intersects_road_corridor
        ):
            rule_id = "RULE_INFRASTRUCTURE_CORRIDOR_v1"
            intel_type = IntelligenceType.INFRASTRUCTURE_CHANGE
            title = f"Road Corridor Clearing Event along {spatial_context.closest_road_name or 'Corridor'}"
            evidence_sources_count = 2

            road_node_id = f"ev-road-{str(uuid.uuid4())[:8]}"
            nodes.append(
                EvidenceNode(
                    id=road_node_id,
                    node_type=EvidenceType.ROAD_DATA,
                    label=f"Road Feature: {spatial_context.closest_road_name}",
                    source_identifier="OpenStreetMap",
                    epistemic_level=EpistemicLevel.OBSERVED,
                    evidence_strength=EvidenceStrength.STRONG,
                    properties={
                        "distance_m": spatial_context.distance_to_closest_road_m,
                        "road_class": spatial_context.closest_road_class,
                    },
                )
            )
            edges.append(
                EvidenceEdge(
                    source_node_id=road_node_id,
                    target_node_id=intel_id,
                    relationship_type=EvidenceRelationshipType.LOCATED_IN,
                )
            )

        # 3. Evaluate Rule 2: Water Dynamics
        elif payload.ndwi_delta is not None and abs(payload.ndwi_delta) >= 0.10:
            rule_id = "RULE_WATER_CHANGE_v1"
            intel_type = IntelligenceType.WATER_CHANGE
            dyn = "Recession" if payload.ndwi_delta < 0 else "Inundation"
            title = f"Surface Water {dyn} Event ({payload.affected_area_km2:.2f} km²)"
            evidence_sources_count = 1

            ndwi_node_id = f"ev-ndwi-{str(uuid.uuid4())[:8]}"
            nodes.append(
                EvidenceNode(
                    id=ndwi_node_id,
                    node_type=EvidenceType.CHANGE_EVENT,
                    label=f"dNDWI Water {dyn}",
                    source_identifier=payload.primary_sensor,
                    epistemic_level=EpistemicLevel.CALCULATED,
                    evidence_strength=EvidenceStrength.STRONG,
                    properties={"delta": payload.ndwi_delta, "metric": "NDWI"},
                )
            )
            edges.append(
                EvidenceEdge(
                    source_node_id=ndwi_node_id,
                    target_node_id=intel_id,
                    relationship_type=EvidenceRelationshipType.SUPPORTS,
                )
            )

        # 4. Evaluate Rule 3: Canopy Vegetation Dynamics
        elif payload.ndvi_delta is not None and abs(payload.ndvi_delta) >= 0.10:
            rule_id = "RULE_VEGETATION_CHANGE_v1"
            intel_type = IntelligenceType.VEGETATION_CHANGE
            dyn = "Loss" if payload.ndvi_delta < 0 else "Gain"
            title = f"Canopy Vegetation {dyn} Candidate ({payload.affected_area_km2:.2f} km²)"
            evidence_sources_count = 1

            ndvi_node_id = f"ev-ndvi-{str(uuid.uuid4())[:8]}"
            nodes.append(
                EvidenceNode(
                    id=ndvi_node_id,
                    node_type=EvidenceType.CHANGE_EVENT,
                    label=f"dNDVI Canopy {dyn}",
                    source_identifier=payload.primary_sensor,
                    epistemic_level=EpistemicLevel.CALCULATED,
                    evidence_strength=EvidenceStrength.STRONG,
                    properties={"delta": payload.ndvi_delta, "metric": "NDVI"},
                )
            )
            edges.append(
                EvidenceEdge(
                    source_node_id=ndvi_node_id,
                    target_node_id=intel_id,
                    relationship_type=EvidenceRelationshipType.SUPPORTS,
                )
            )
        else:
            rule_id = "RULE_GENERAL_SPATIAL_ANOMALY_v1"
            intel_type = IntelligenceType.SPATIAL_ANOMALY
            title = f"Unclassified Spatial Transition ({payload.affected_area_km2:.2f} km²)"
            evidence_sources_count = 1

        # 5. Check Contradictory Evidence
        status = "ACTIVE"
        if (
            payload.secondary_sensor is not None
            and payload.secondary_sensor_signal_delta is not None
            and payload.ndvi_delta is not None
        ):
            # Example: optical shows severe drop (-0.25) but secondary sensor shows zero or opposite signal (+0.10)
            if (payload.ndvi_delta < -0.15 and payload.secondary_sensor_signal_delta > 0.05) or (
                payload.ndvi_delta > 0.15 and payload.secondary_sensor_signal_delta < -0.05
            ):
                contradictions += 1
                status = "CONTRADICTED"
                sec_node_id = f"ev-sec-{str(uuid.uuid4())[:8]}"
                nodes.append(
                    EvidenceNode(
                        id=sec_node_id,
                        node_type=EvidenceType.MEASUREMENT,
                        label=f"Conflicting Telemetry ({payload.secondary_sensor})",
                        source_identifier=payload.secondary_sensor,
                        epistemic_level=EpistemicLevel.OBSERVED,
                        evidence_strength=EvidenceStrength.MODERATE,
                        properties={"delta": payload.secondary_sensor_signal_delta},
                    )
                )
                edges.append(
                    EvidenceEdge(
                        source_node_id=sec_node_id,
                        target_node_id=intel_id,
                        relationship_type=EvidenceRelationshipType.CONTRADICTS,
                        metadata_payload={"conflict_reason": "Cross-sensor directional polarity divergence"},
                    )
                )

        # 6. Determine Evidence Strength Aggregation
        if contradictions > 0:
            agg_strength = EvidenceStrength.INSUFFICIENT
            confidence = 0.50
        elif evidence_sources_count >= 2:
            agg_strength = EvidenceStrength.STRONG
            confidence = 0.94
        elif evidence_sources_count == 1:
            agg_strength = EvidenceStrength.MODERATE
            confidence = 0.85
        else:
            agg_strength = EvidenceStrength.LIMITED
            confidence = 0.60

        graph_result = EvidenceGraphResult(
            nodes=nodes,
            edges=edges,
            has_contradictions=contradictions > 0,
            contradiction_count=contradictions,
        )

        now_utc = datetime.now(timezone.utc).isoformat()
        quality_meta = {
            "evidence_sources_count": len(nodes) - 1,
            "supporting_edges_count": len([e for e in edges if e.relationship_type in [EvidenceRelationshipType.SUPPORTS, EvidenceRelationshipType.CORROBORATES]]),
            "contradiction_edges_count": contradictions,
            "data_completeness_pct": 98.5,
        }

        provenance = {
            "rule_id": rule_id,
            "rule_version": "1.0.0",
            "algorithm_version": "ORBIT-Intelligence-v1.0",
            "epistemic_level": "CALCULATED",
            "deterministic_pipeline": True,
            "ai_interpretation_invoked": False,
            "evaluated_at": now_utc,
        }

        return IntelligenceObjectResult(
            id=intel_id,
            analysis_run_id=analysis_run_id,
            area_of_interest_id=payload.aoi_id,
            intelligence_type=intel_type,
            title=title,
            affected_area_km2=payload.affected_area_km2,
            start_date=payload.target_start_date,
            end_date=payload.target_end_date,
            evidence_strength=agg_strength,
            epistemic_level=EpistemicLevel.CALCULATED,
            confidence=confidence,
            rule_id=rule_id,
            rule_version="1.0.0",
            algorithm_version="ORBIT-Intelligence-v1.0",
            spatial_context=spatial_context,
            temporal_context=temporal_context,
            quality_metadata=quality_meta,
            provenance=provenance,
            evidence_graph=graph_result,
            status=status,
            created_at=now_utc,
        )
