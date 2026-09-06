import uuid
from datetime import datetime, timezone
import pytest
from app.models.enums import (
    UserRole,
    ProjectStatus,
    SensingModality,
    AnalysisStatus,
    EpistemicLevel,
    EvidenceStrength,
    SupportClassification,
    FuturePredictionType,
    IslamicSourceGrade,
    ReportStatus,
)
from app.models.auth.user import User
from app.models.workspace.project import Project
from app.models.workspace.area_of_interest import AreaOfInterest
from app.models.geo.road_feature import RoadFeature
from app.models.eo.dataset_registry import DatasetRegistry
from app.models.eo.imagery_scene import ImageryScene
from app.models.analysis.analysis_run import AnalysisRun
from app.models.intelligence.measurement import Measurement
from app.models.intelligence.detected_change import DetectedChange
from app.models.intelligence.geographic_event import GeographicEvent
from app.models.intelligence.evidence_record import EvidenceRecord
from app.models.intelligence.report import Report
from app.models.history_deep.historical_annual_summary import HistoricalAnnualSummary
from app.models.history_deep.future_prediction import FuturePrediction
from app.models.history_deep.geological_epoch import GeologicalEpoch
from app.models.history_deep.islamic_geographic_record import IslamicGeographicRecord
from geoalchemy2.elements import WKTElement


def test_user_model_instantiation():
    user = User(
        id=uuid.uuid4(),
        email="analyst@orbit.geoint",
        password_hash="argon2id_hash_placeholder",
        full_name="Senior GEOINT Analyst",
        role=UserRole.ANALYST,
        is_active=True,
    )
    assert user.email == "analyst@orbit.geoint"
    assert user.role == UserRole.ANALYST
    assert "analyst@orbit.geoint" in repr(user)


def test_workspace_models_instantiation():
    user_id = uuid.uuid4()
    proj = Project(
        id=uuid.uuid4(),
        user_id=user_id,
        name="Amazon Basin Deforestation Monitoring",
        description="Tracking canopy disturbance along Highway BR-163",
        status=ProjectStatus.ACTIVE,
    )
    assert proj.status == ProjectStatus.ACTIVE
    assert "Amazon Basin" in repr(proj)

    aoi = AreaOfInterest(
        id=uuid.uuid4(),
        project_id=proj.id,
        name="Mato Grosso Sector 4",
        geometry=WKTElement("MULTIPOLYGON((( -55.0 -12.0, -54.0 -12.0, -54.0 -11.0, -55.0 -11.0, -55.0 -12.0 )))", srid=4326),
        surface_area_km2=12345.67,
    )
    assert aoi.surface_area_km2 == 12345.67
    assert "Mato Grosso" in repr(aoi)


def test_geo_road_feature_instantiation():
    road = RoadFeature(
        id=uuid.uuid4(),
        osm_id=123456789,
        geometry=WKTElement("LINESTRING(-55.0 -12.0, -54.5 -11.5)", srid=4326),
        highway_class="primary",
        name="Trans-Amazonian Highway",
        ref="BR-230",
        surface="asphalt",
        lanes=2,
        oneway=False,
        bridge=False,
        tunnel=False,
        length_m=75000.0,
    )
    assert road.osm_id == 123456789
    assert road.highway_class == "primary"
    assert "Trans-Amazonian Highway" in repr(road)


def test_eo_dataset_and_scene_instantiation():
    dataset = DatasetRegistry(
        id="copernicus-s2-l2a",
        provider="European Space Agency (ESA)",
        dataset_name="Sentinel-2 MSI Level-2A",
        modality=SensingModality.OPTICAL,
        license="EU Copernicus Open Access",
        attribution="Contains modified Copernicus Sentinel data [2026]",
        redistribution_allowed=True,
        commercial_use_allowed=True,
    )
    assert dataset.modality == SensingModality.OPTICAL
    assert "copernicus-s2-l2a" in repr(dataset)

    scene = ImageryScene(
        id=uuid.uuid4(),
        dataset_id=dataset.id,
        provider_scene_id="S2A_MSIL2A_20240720T140051_N0510_R067_T21LYJ",
        acquisition_datetime=datetime.now(timezone.utc),
        platform="Sentinel-2A",
        sensor="MSI",
        modality=SensingModality.OPTICAL,
        cloud_cover=4.2,
        processing_level="Level-2A",
        spatial_resolution=10.0,
        geometry=WKTElement("POLYGON((-55.0 -12.0, -54.0 -12.0, -54.0 -11.0, -55.0 -11.0, -55.0 -12.0))", srid=4326),
        metadata_payload={"sun_azimuth": 45.2, "sun_elevation": 62.1},
    )
    assert scene.cloud_cover == 4.2
    assert scene.spatial_resolution == 10.0


def test_analysis_and_intelligence_models():
    run_id = uuid.uuid4()
    aoi_id = uuid.uuid4()
    proj_id = uuid.uuid4()

    run = AnalysisRun(
        id=run_id,
        project_id=proj_id,
        area_of_interest_id=aoi_id,
        status=AnalysisStatus.COMPLETED,
        analysis_type="BI_TEMPORAL_CHANGE",
        start_date=datetime(2023, 7, 1, tzinfo=timezone.utc),
        end_date=datetime(2024, 7, 1, tzinfo=timezone.utc),
        parameters={"index": "dNDVI", "otsu": True},
    )
    assert run.status == AnalysisStatus.COMPLETED

    measurement = Measurement(
        id=uuid.uuid4(),
        analysis_run_id=run_id,
        measurement_type="affected_area_km2",
        value=14.23,
        unit="km2",
        uncertainty=0.15,
        epistemic_level=EpistemicLevel.CALCULATED,
        methodology="PostGIS ST_Area(geom::geography)",
        source="Sentinel-2A MSI L2A",
    )
    assert measurement.value == 14.23
    assert measurement.epistemic_level == EpistemicLevel.CALCULATED

    detected_change = DetectedChange(
        id=uuid.uuid4(),
        analysis_run_id=run_id,
        change_type="VEGETATION_LOSS",
        geometry=WKTElement("MULTIPOLYGON((( -55.0 -12.0, -54.9 -12.0, -54.9 -11.9, -55.0 -11.9, -55.0 -12.0 )))", srid=4326),
        affected_area=14.23,
        confidence=0.94,
        evidence_strength=EvidenceStrength.STRONG,
        detection_method="Tier_2_Adaptive_Otsu_dNDVI",
        before_date=datetime(2023, 7, 1, tzinfo=timezone.utc),
        after_date=datetime(2024, 7, 1, tzinfo=timezone.utc),
    )
    assert detected_change.evidence_strength == EvidenceStrength.STRONG
    assert detected_change.affected_area == 14.23

    event = GeographicEvent(
        id=uuid.uuid4(),
        analysis_run_id=run_id,
        event_type="CANOPY_DEFORESTATION_SURGE",
        geometry=WKTElement("MULTIPOLYGON((( -55.0 -12.0, -54.9 -12.0, -54.9 -11.9, -55.0 -11.9, -55.0 -12.0 )))", srid=4326),
        severity="CRITICAL",
        confidence=0.95,
        evidence_strength=EvidenceStrength.STRONG,
        start_date=datetime(2023, 7, 1, tzinfo=timezone.utc),
        end_date=datetime(2024, 7, 1, tzinfo=timezone.utc),
    )
    assert event.severity == "CRITICAL"

    evidence = EvidenceRecord(
        id=uuid.uuid4(),
        analysis_run_id=run_id,
        source_type="SATELLITE_TELEMETRY",
        source_id="S2A_MSIL2A_20240720T...",
        claim_type="CANOPY_LOSS_MAGNITUDE",
        claim_reference="affected_area_km2",
        input_checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        algorithm="PostGIS_ST_Area_Spheroid",
        evidence_strength=EvidenceStrength.STRONG,
    )
    assert len(evidence.input_checksum) == 64

    report = Report(
        id=uuid.uuid4(),
        analysis_run_id=run_id,
        title="Amazon Deforestation Corridor Intelligence Briefing",
        status=ReportStatus.COMPLETED,
    )
    assert report.status == ReportStatus.COMPLETED


def test_history_deep_models_instantiation():
    aoi_id = uuid.uuid4()

    summary = HistoricalAnnualSummary(
        id=uuid.uuid4(),
        area_of_interest_id=aoi_id,
        year=2023,
        support_classification=SupportClassification.STRONGLY_SUPPORTED,
        summary_data={"mean_ndvi": 0.68, "built_up_km2": 42.1},
        data_sources={"sentinel_scenes_count": 18},
    )
    assert summary.support_classification == SupportClassification.STRONGLY_SUPPORTED

    prediction = FuturePrediction(
        id=uuid.uuid4(),
        area_of_interest_id=aoi_id,
        prediction_type=FuturePredictionType.URBAN_EXPANSION,
        target_year=2035,
        prediction_value=85.4,
        lower_bound=79.2,
        upper_bound=92.1,
        unit="km2",
        model_name="Prophet_Urban_Trend",
        training_start_year=2000,
        training_end_year=2024,
        confidence=0.85,
        evidence_strength=EvidenceStrength.MODERATE,
    )
    assert prediction.prediction_type == FuturePredictionType.URBAN_EXPANSION
    assert prediction.target_year == 2035

    epoch = GeologicalEpoch(
        id=uuid.uuid4(),
        name="Holocene",
        start_age=0.0117,
        end_age=0.0,
        description="Current interglacial epoch spanning the last 11,700 years of Earth history.",
        evidence_type="Greenland Ice Core Chronology (GICC05)",
    )
    assert epoch.name == "Holocene"
    assert epoch.start_age > epoch.end_age

    islamic_rec = IslamicGeographicRecord(
        id=uuid.uuid4(),
        title="Lowest Land Depression (Adna al-Ard)",
        source_type="QURANIC_AYAH",
        classification=IslamicSourceGrade.QURAN,
        description="Geographic region referenced in Surah Al-Rum denoting the Dead Sea depression basin.",
        geographic_reference="Dead Sea Basin / Jordan Rift Valley",
        source="Surah Al-Rum (30:2-4)",
    )
    assert islamic_rec.classification == IslamicSourceGrade.QURAN
    assert "Lowest Land" in repr(islamic_rec)
