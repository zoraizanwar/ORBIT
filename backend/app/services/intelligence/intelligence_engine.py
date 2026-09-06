from typing import Any, Dict, List, Optional
from app.services.intelligence.models import (
    RuleEvaluationInput,
    IntelligenceObjectResult,
)
from app.services.intelligence.spatial_correlator import SpatialCorrelator
from app.services.intelligence.temporal_correlator import TemporalCorrelator
from app.services.intelligence.rule_engine import DeterministicRuleEngine


class IntelligenceEngine:
    """
    Unified Advanced Geospatial Intelligence Engine.
    """

    @classmethod
    def execute_intelligence_analysis(
        cls,
        payload: RuleEvaluationInput,
        road_features: Optional[List[Dict[str, Any]]] = None,
        analysis_run_id: Optional[str] = None,
    ) -> IntelligenceObjectResult:
        run_id = analysis_run_id or "run-ephemeral"

        # 1. Spatial Context Evaluation
        spatial_context = SpatialCorrelator.evaluate_road_proximity(
            target_geometry=payload.aoi_geometry,
            road_features=road_features,
        )

        # 2. Temporal Context Evaluation
        temporal_context = TemporalCorrelator.evaluate_temporal_alignment(
            start_date=payload.target_start_date,
            end_date=payload.target_end_date,
        )

        # 3. Rule Evaluation & Evidence Graph Assembly
        return DeterministicRuleEngine.evaluate_rules(
            payload=payload,
            spatial_context=spatial_context,
            temporal_context=temporal_context,
            analysis_run_id=run_id,
        )
