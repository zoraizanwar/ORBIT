from app.models.enums import EpistemicLevel, EvidenceStrength
from app.services.intelligence.models import (
    EvidenceType,
    EvidenceRelationshipType,
    EvidenceNode,
    EvidenceEdge,
    EvidenceGraphResult,
)
from app.services.intelligence.evidence_graph import EvidenceGraphTraverser


def test_evidence_graph_traversal():
    root = EvidenceNode(
        id="node-root",
        node_type=EvidenceType.ANALYSIS_RESULT,
        label="Root Intelligence",
        source_identifier="run-01",
        epistemic_level=EpistemicLevel.CALCULATED,
        evidence_strength=EvidenceStrength.STRONG,
    )
    sup1 = EvidenceNode(
        id="node-sup-1",
        node_type=EvidenceType.CHANGE_EVENT,
        label="dNDVI",
        source_identifier="Sentinel-2",
        epistemic_level=EpistemicLevel.CALCULATED,
        evidence_strength=EvidenceStrength.STRONG,
    )
    contra1 = EvidenceNode(
        id="node-contra-1",
        node_type=EvidenceType.MEASUREMENT,
        label="SAR Stable",
        source_identifier="Sentinel-1",
        epistemic_level=EpistemicLevel.OBSERVED,
        evidence_strength=EvidenceStrength.MODERATE,
    )

    edge1 = EvidenceEdge(
        source_node_id="node-sup-1",
        target_node_id="node-root",
        relationship_type=EvidenceRelationshipType.SUPPORTS,
    )
    edge2 = EvidenceEdge(
        source_node_id="node-contra-1",
        target_node_id="node-root",
        relationship_type=EvidenceRelationshipType.CONTRADICTS,
    )

    graph = EvidenceGraphResult(
        nodes=[root, sup1, contra1],
        edges=[edge1, edge2],
        has_contradictions=True,
        contradiction_count=1,
    )

    supporting = EvidenceGraphTraverser.get_supporting_nodes(graph, "node-root")
    contradicting = EvidenceGraphTraverser.get_contradicting_nodes(graph, "node-root")

    assert len(supporting) == 1
    assert supporting[0].id == "node-sup-1"

    assert len(contradicting) == 1
    assert contradicting[0].id == "node-contra-1"

    # Subgraph filtering
    sub = EvidenceGraphTraverser.filter_subgraph_by_depth(graph, "node-root", max_depth=1)
    assert len(sub.nodes) == 3
    assert len(sub.edges) == 2
