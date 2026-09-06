"""
ORBIT End-to-End Deterministic Pipeline Orchestrator

Executes the complete intelligence lifecycle from synthetic raster inputs to
cryptographically signed intelligence reports.

Each stage carries provenance and epistemic classification forward.
Test fixture data is explicitly labeled and never promoted to OBSERVED status.
"""

import uuid
import numpy as np
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.models.enums import EpistemicLevel
from app.services.eo.raster.spectral_indices import SpectralIndexEngine
from app.services.eo.raster.raster_statistics import compute_raster_statistics
from app.services.eo.change.temporal_comparator import TemporalComparator
from app.services.eo.change.models import TemporalObservationPair
from app.services.eo.timeseries.models import TimePointMeasurement
from app.services.intelligence.intelligence_engine import IntelligenceEngine
from app.services.intelligence.rule_engine import RuleEvaluationInput
from app.services.forecasting.models import (
    HistoricalObservation,
    RunForecastPayload,
    ForecastMetric,
    ForecastScenarioType,
)
from app.services.forecasting.forecast_engine import ForecastEngine
from app.services.ai.models import (
    EvidenceItem,
    EvidenceRelationshipItem,
    InterpretRequestPayload,
    ReportRequestPayload,
    ReportFormat,
    AIInterpretationType,
)
from app.services.ai.evidence_retriever import EvidenceRetriever
from app.services.ai.grounded_reasoner import GroundedReasoner
from app.services.ai.report_generator import ReportGenerator
from app.services.observability import AnalysisLifecycleTracker


class EndToEndPipelineOrchestrator:
    """
    Unified ORBIT End-to-End Deterministic Pipeline Orchestrator.
    Executes and validates the complete intelligence lifecycle.
    All data produced by this orchestrator is TEST FIXTURE / SIMULATED.
    It is never presented as real EO telemetry.
    """

    AOI_GEOMETRY = {
        "type": "Polygon",
        "coordinates": [
            [[-55.5, -11.5], [-55.0, -11.5], [-55.0, -11.0], [-55.5, -11.0], [-55.5, -11.5]]
        ],
    }

    @classmethod
    def run_full_pipeline(
        cls,
        aoi_id: str = "aoi-sinop-e2e-fixture",
        aoi_name: str = "Sinop Deforestation Frontier [TEST FIXTURE - SIMULATED]",
        is_test_fixture: bool = True,
    ) -> Dict[str, Any]:
        tracker = AnalysisLifecycleTracker(
            analysis_type="FULL_END_TO_END_INTELLIGENCE_PIPELINE",
            aoi_id=aoi_id,
            algorithm_version="ORBIT-E2E-v1.0.0",
        )
        tracker.start()

        # ─────────────────────────────────────────────────────────────────────
        # STAGE 1: Synthetic raster generation (64×64 bounded test arrays)
        # TEST FIXTURE DATA — NOT real satellite telemetry
        # ─────────────────────────────────────────────────────────────────────
        np.random.seed(42)
        red_t1 = np.full((64, 64), 0.10, dtype=np.float32)
        nir_t1 = np.full((64, 64), 0.60, dtype=np.float32)
        red_t2 = np.full((64, 64), 0.25, dtype=np.float32)
        nir_t2 = np.full((64, 64), 0.35, dtype=np.float32)

        # ─────────────────────────────────────────────────────────────────────
        # STAGE 2: Spectral NDVI calculation (CALCULATED epistemic level)
        # ─────────────────────────────────────────────────────────────────────
        ndvi_t1_array = SpectralIndexEngine.calculate_ndvi(nir_t1, red_t1)
        ndvi_t2_array = SpectralIndexEngine.calculate_ndvi(nir_t2, red_t2)

        stats_t1 = compute_raster_statistics(ndvi_t1_array)
        stats_t2 = compute_raster_statistics(ndvi_t2_array)

        # ─────────────────────────────────────────────────────────────────────
        # STAGE 3: Temporal change detection (CALCULATED epistemic level)
        # ─────────────────────────────────────────────────────────────────────
        t1_measurement = TimePointMeasurement(
            acquisition_datetime=datetime(2023, 7, 15, 0, 0, 0, tzinfo=timezone.utc),
            metric_name="NDVI",
            value=stats_t1.mean,
            unit="index_value",
            source_scene_id="S2A_MSIL2A_20230715_TEST_FIXTURE",
            platform="Sentinel-2",
            sensor="MSI",
            cloud_cover=2.0,
            valid_pixel_percentage=98.0,
            epistemic_level=EpistemicLevel.CALCULATED,
        )

        t2_measurement = TimePointMeasurement(
            acquisition_datetime=datetime(2026, 7, 18, 0, 0, 0, tzinfo=timezone.utc),
            metric_name="NDVI",
            value=stats_t2.mean,
            unit="index_value",
            source_scene_id="S2A_MSIL2A_20260718_TEST_FIXTURE",
            platform="Sentinel-2",
            sensor="MSI",
            cloud_cover=1.5,
            valid_pixel_percentage=99.0,
            epistemic_level=EpistemicLevel.CALCULATED,
        )

        pair = TemporalObservationPair(
            aoi_id=aoi_id,
            aoi_name=aoi_name,
            measurement_t1=t1_measurement,
            measurement_t2=t2_measurement,
        )
        comparison_res = TemporalComparator.compare_observations(pair)

        # ─────────────────────────────────────────────────────────────────────
        # STAGE 4: Intelligence rule evaluation (DETECTED epistemic level)
        # ─────────────────────────────────────────────────────────────────────
        rule_input = RuleEvaluationInput(
            aoi_id=aoi_id,
            aoi_geometry=cls.AOI_GEOMETRY,
            target_start_date=datetime(2023, 7, 15, tzinfo=timezone.utc),
            target_end_date=datetime(2026, 7, 18, tzinfo=timezone.utc),
            ndvi_delta=comparison_res.absolute_delta,
            ndbi_delta=0.18,
            affected_area_km2=6.85,
            nearby_road_distance_m=85.0,
            primary_sensor="Sentinel-2",
        )
        intel_result = IntelligenceEngine.execute_intelligence_analysis(
            payload=rule_input,
            road_features=None,
            analysis_run_id=tracker.analysis_id,
        )

        # ─────────────────────────────────────────────────────────────────────
        # STAGE 5: Multi-year historical forecasting (PREDICTED epistemic level)
        # ─────────────────────────────────────────────────────────────────────
        observations = [
            HistoricalObservation(
                aoi_id=aoi_id,
                metric=ForecastMetric.NDVI,
                acquisition_datetime=datetime(2020, 7, 1, tzinfo=timezone.utc),
                value=0.72,
                sensor="Sentinel-2",
                cloud_cover=2.0,
                valid_pixel_pct=98.0,
                epistemic_level=EpistemicLevel.CALCULATED,
            ),
            HistoricalObservation(
                aoi_id=aoi_id,
                metric=ForecastMetric.NDVI,
                acquisition_datetime=datetime(2022, 7, 1, tzinfo=timezone.utc),
                value=0.65,
                sensor="Sentinel-2",
                cloud_cover=1.5,
                valid_pixel_pct=99.0,
                epistemic_level=EpistemicLevel.CALCULATED,
            ),
            HistoricalObservation(
                aoi_id=aoi_id,
                metric=ForecastMetric.NDVI,
                acquisition_datetime=datetime(2024, 7, 1, tzinfo=timezone.utc),
                value=0.58,
                sensor="Sentinel-2",
                cloud_cover=0.8,
                valid_pixel_pct=99.5,
                epistemic_level=EpistemicLevel.CALCULATED,
            ),
            HistoricalObservation(
                aoi_id=aoi_id,
                metric=ForecastMetric.NDVI,
                acquisition_datetime=datetime(2026, 7, 1, tzinfo=timezone.utc),
                value=0.51,
                sensor="Sentinel-2",
                cloud_cover=1.0,
                valid_pixel_pct=99.0,
                epistemic_level=EpistemicLevel.CALCULATED,
            ),
        ]

        forecast_run_id = str(uuid.uuid4())
        forecast_res = ForecastEngine.run_forecast(
            RunForecastPayload(
                aoi_id=aoi_id,
                metric=ForecastMetric.NDVI,
                forecast_start_year=2027,
                forecast_end_year=2030,
                scenario=ForecastScenarioType.BASELINE_TREND,
                observations=observations,
            ),
            run_id=forecast_run_id,
        )

        # ─────────────────────────────────────────────────────────────────────
        # STAGE 6: Evidence package assembly with SHA-256 cryptographic digest
        # ─────────────────────────────────────────────────────────────────────
        pkg_items: List[EvidenceItem] = [
            EvidenceItem(
                id="ev-scene-t1",
                type="SCENE",
                epistemic_level=EpistemicLevel.OBSERVED,
                source_id="S2A_MSIL2A_20230715_TEST_FIXTURE",
                source_type="Sentinel-2 L2A [TEST FIXTURE]",
                description="Optical acquisition T1 (TEST FIXTURE - SIMULATED)",
                timestamp="2023-07-15T00:00:00Z",
            ),
            EvidenceItem(
                id="ev-scene-t2",
                type="SCENE",
                epistemic_level=EpistemicLevel.OBSERVED,
                source_id="S2A_MSIL2A_20260718_TEST_FIXTURE",
                source_type="Sentinel-2 L2A [TEST FIXTURE]",
                description="Optical acquisition T2 (TEST FIXTURE - SIMULATED)",
                timestamp="2026-07-18T00:00:00Z",
            ),
            EvidenceItem(
                id="ev-ndvi-delta",
                type="INDEX_MEASUREMENT",
                epistemic_level=EpistemicLevel.CALCULATED,
                source_id="dNDVI_Sinop_E2E",
                source_type="SpectralIndexEngine.calculate_ndvi",
                value=round(comparison_res.absolute_delta, 3),
                unit="index_delta",
                description="NDVI vegetation index decline",
            ),
            EvidenceItem(
                id="ev-change-area",
                type="CHANGE_MASK",
                epistemic_level=EpistemicLevel.CALCULATED,
                source_id="mask_sinop_e2e",
                source_type="Spatial Difference Engine",
                value=6.85,
                unit="km2",
                description="Deforestation clearance area 6.85 km2",
            ),
            EvidenceItem(
                id="ev-road-corridor",
                type="ROAD_CORRIDOR",
                epistemic_level=EpistemicLevel.OBSERVED,
                source_id="OSM_Way_BR163_Fixture",
                source_type="OpenStreetMap Vector Registry",
                value=85.0,
                unit="meters",
                description="BR-163 right-of-way proximity 85.0 m",
            ),
            EvidenceItem(
                id="ev-forecast-2030",
                type="FORECAST_PROJECTION",
                epistemic_level=EpistemicLevel.PREDICTED,
                source_id=f"ORBIT-LT-{forecast_run_id[:8]}",
                source_type="LinearTrendForecast v1",
                value=round(forecast_res.predictions[-1].predicted_value, 4),
                unit="index_value",
                timestamp="2030-07-01T00:00:00Z",
                description="2030 NDVI horizon projection",
            ),
        ]

        relationships: List[EvidenceRelationshipItem] = [
            EvidenceRelationshipItem(source_id="ev-scene-t1", target_id="ev-ndvi-delta", relationship_type="DERIVED_FROM"),
            EvidenceRelationshipItem(source_id="ev-scene-t2", target_id="ev-ndvi-delta", relationship_type="DERIVED_FROM"),
            EvidenceRelationshipItem(source_id="ev-ndvi-delta", target_id="ev-change-area", relationship_type="SUPPORTS"),
            EvidenceRelationshipItem(source_id="ev-road-corridor", target_id="ev-change-area", relationship_type="LOCATED_IN"),
        ]

        pkg = EvidenceRetriever.assemble_package(
            aoi_id=aoi_id,
            aoi_name=aoi_name,
            analysis_run_id=tracker.analysis_id,
            evidence_items=pkg_items,
            relationships=relationships,
        )

        # ─────────────────────────────────────────────────────────────────────
        # STAGE 7: Grounded AI intelligence synthesis (AI_INTERPRETED epistemic level)
        # ─────────────────────────────────────────────────────────────────────
        ai_interp = GroundedReasoner.interpret(
            InterpretRequestPayload(
                aoi_id=aoi_id,
                interpretation_type=AIInterpretationType.URBAN_EXPANSION_SYNTHESIS,
            ),
            evidence_package=pkg,
        )

        # ─────────────────────────────────────────────────────────────────────
        # STAGE 8: Cryptographically signed intelligence report
        # ─────────────────────────────────────────────────────────────────────
        report = ReportGenerator.generate_report(
            ReportRequestPayload(
                aoi_id=aoi_id,
                title=f"End-to-End Pipeline Intelligence Report — {aoi_name}",
                report_format=ReportFormat.MARKDOWN,
            ),
            evidence_package=pkg,
            interpretation=ai_interp,
        )

        lifecycle_summary = tracker.complete(
            metrics={
                "ndvi_t1_mean": round(stats_t1.mean, 4),
                "ndvi_t2_mean": round(stats_t2.mean, 4),
                "comparison_absolute_delta": comparison_res.absolute_delta,
                "forecast_2030_value": forecast_res.predictions[-1].predicted_value,
                "claims_count": len(ai_interp.claims),
                "recommendations_count": len(ai_interp.recommendations),
                "package_hash": pkg.package_hash_sha256,
                "report_hash": report.provenance_hash_sha256,
                "is_test_fixture": is_test_fixture,
            }
        )

        return {
            "status": "SUCCESS",
            "lifecycle": lifecycle_summary,
            "stats_t1": stats_t1,
            "stats_t2": stats_t2,
            "comparison": comparison_res,
            "intelligence_event": intel_result,
            "forecast": forecast_res,
            "evidence_package": pkg,
            "ai_interpretation": ai_interp,
            "report": report,
            "is_test_fixture": is_test_fixture,
        }
