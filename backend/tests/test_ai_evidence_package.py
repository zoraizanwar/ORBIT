from app.models.enums import EpistemicLevel, EvidenceStrength
from app.services.ai.models import EvidenceItem, EvidenceRelationshipItem
from app.services.ai.evidence_retriever import EvidenceRetriever


def test_evidence_package_assembly_and_digest():
    items = [
        EvidenceItem(
            id="ev-1",
            type="SCENE",
            epistemic_level=EpistemicLevel.OBSERVED,
            source_id="S2A_20230715",
            source_type="Sentinel-2 L2A",
            description="Scene observation",
        ),
        EvidenceItem(
            id="ev-2",
            type="INDEX_MEASUREMENT",
            epistemic_level=EpistemicLevel.CALCULATED,
            source_id="dNDVI",
            source_type="Spectral Calculation",
            value=-0.24,
            unit="index_delta",
            description="Vegetation loss delta",
        ),
    ]

    relationships = [
        EvidenceRelationshipItem(
            source_id="ev-1",
            target_id="ev-2",
            relationship_type="DERIVED_FROM",
        )
    ]

    pkg = EvidenceRetriever.assemble_package(
        aoi_id="aoi-sinop",
        aoi_name="Sinop Sector",
        evidence_items=items,
        relationships=relationships,
    )

    assert pkg.aoi_id == "aoi-sinop"
    assert len(pkg.evidence_items) == 2
    assert len(pkg.relationships) == 1
    assert pkg.has_contradictions is False
    assert len(pkg.package_hash_sha256) == 64


def test_evidence_package_contradiction_detection():
    pkg = EvidenceRetriever.get_seed_evidence_package(
        aoi_id="aoi-sinop",
        include_contradiction=True,
    )

    assert pkg.has_contradictions is True
    assert pkg.contradiction_count >= 1
    assert any(r.relationship_type == "CONTRADICTS" for r in pkg.relationships)
