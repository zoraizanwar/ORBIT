import os
import uuid
from datetime import datetime, timezone
import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon, MultiPolygon
from alembic.config import Config
from alembic.script import ScriptDirectory

from app.models.enums import EpistemicLevel, EvidenceStrength
from app.models.intelligence.intelligence_event import IntelligenceEvent
from app.models.intelligence.evidence_record import EvidenceRecord
from app.models.intelligence.evidence_relationship import EvidenceRelationship


def test_intelligence_event_model_instantiation():
    poly = Polygon([[-54.7, -11.5], [-54.6, -11.5], [-54.6, -11.4], [-54.7, -11.4], [-54.7, -11.5]])
    multi_poly = MultiPolygon([poly])
    wkb_geom = from_shape(multi_poly, srid=4326)

    run_id = uuid.uuid4()
    evt = IntelligenceEvent(
        analysis_run_id=run_id,
        intelligence_type="URBAN_EXPANSION",
        title="Urban Sprawl Expansion Candidate",
        geometry=wkb_geom,
        affected_area=4.52,
        start_date=datetime(2023, 7, 15, tzinfo=timezone.utc),
        end_date=datetime(2026, 7, 18, tzinfo=timezone.utc),
        evidence_strength=EvidenceStrength.STRONG,
        epistemic_level=EpistemicLevel.CALCULATED,
        confidence=0.94,
        rule_id="RULE_MULTI_URBAN_EXPANSION_v1",
        rule_version="1.0.0",
        algorithm_version="ORBIT-Intelligence-v1.0",
        quality_metadata={"evidence_count": 2},
        provenance={"formula": "dNDVI <= -0.10 and dNDBI >= 0.08"},
        status="ACTIVE",
    )

    assert evt.intelligence_type == "URBAN_EXPANSION"
    assert evt.affected_area == 4.52
    assert evt.evidence_strength == EvidenceStrength.STRONG
    assert evt.epistemic_level == EpistemicLevel.CALCULATED
    assert evt.confidence == 0.94


def test_evidence_relationship_instantiation():
    ev_id = uuid.uuid4()
    target_id = str(uuid.uuid4())

    rel = EvidenceRelationship(
        source_evidence_id=ev_id,
        target_entity_type="INTELLIGENCE_EVENT",
        target_entity_id=target_id,
        relationship_type="SUPPORTS",
        weight=1.0,
        metadata_payload={"delta": -0.22, "metric": "NDVI"},
    )

    assert rel.relationship_type == "SUPPORTS"
    assert rel.weight == 1.0
    assert rel.metadata_payload["metric"] == "NDVI"


def test_alembic_migration_0006_script_validity():
    alembic_cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    config = Config(alembic_cfg_path)
    script_dir = ScriptDirectory.from_config(config)

    rev_0006 = script_dir.get_revision("0006_advanced_geo_intel")
    assert rev_0006 is not None
    assert rev_0006.down_revision == "0005_change_detection_foundation"
