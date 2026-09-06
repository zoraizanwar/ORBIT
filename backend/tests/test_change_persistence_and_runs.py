import uuid
from datetime import datetime, timezone
import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon, MultiPolygon
from app.models.enums import AnalysisStatus, EvidenceStrength
from app.models.analysis.analysis_run import AnalysisRun
from app.models.intelligence.detected_change import DetectedChange
from alembic.config import Config
from alembic.script import ScriptDirectory


def test_detected_change_model_instantiation():
    poly = Polygon([[-54.7, -11.5], [-54.6, -11.5], [-54.6, -11.4], [-54.7, -11.4], [-54.7, -11.5]])
    multi_poly = MultiPolygon([poly])
    wkb_geom = from_shape(multi_poly, srid=4326)

    run_id = uuid.uuid4()
    chg = DetectedChange(
        analysis_run_id=run_id,
        change_type="VEGETATION_LOSS",
        geometry=wkb_geom,
        affected_area=14.23,
        percentage_change=-18.4,
        confidence=0.95,
        evidence_strength=EvidenceStrength.STRONG,
        detection_method="Tier_2_Adaptive_Otsu_dNDVI",
        before_date=datetime(2023, 7, 15, tzinfo=timezone.utc),
        after_date=datetime(2026, 7, 18, tzinfo=timezone.utc),
    )

    assert chg.change_type == "VEGETATION_LOSS"
    assert chg.affected_area == 14.23
    assert chg.confidence == 0.95
    assert chg.evidence_strength == EvidenceStrength.STRONG
    assert chg.before_date < chg.after_date


def test_analysis_run_with_detected_changes_relationship():
    project_id = uuid.uuid4()
    aoi_id = uuid.uuid4()

    run = AnalysisRun(
        project_id=project_id,
        area_of_interest_id=aoi_id,
        status=AnalysisStatus.COMPLETED,
        analysis_type="BI_TEMPORAL_CHANGE",
        start_date=datetime(2023, 7, 15, tzinfo=timezone.utc),
        end_date=datetime(2026, 7, 18, tzinfo=timezone.utc),
        parameters={"metric": "NDVI", "threshold_version": "NDVI_CANOPY_v1"},
        pipeline_version="1.0.0",
    )

    assert run.analysis_type == "BI_TEMPORAL_CHANGE"
    assert run.status == AnalysisStatus.COMPLETED
    assert run.parameters["metric"] == "NDVI"


def test_alembic_migration_0005_script_validity():
    import os
    alembic_cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    config = Config(alembic_cfg_path)
    script_dir = ScriptDirectory.from_config(config)

    rev_0005 = script_dir.get_revision("0005_change_detection_foundation")
    assert rev_0005 is not None
    assert rev_0005.down_revision == "0004_raster_analysis_foundation"
