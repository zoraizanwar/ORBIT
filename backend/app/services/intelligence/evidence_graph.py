from typing import List, Optional
from app.services.intelligence.models import (
    EvidenceGraphResult,
    EvidenceNode,
    EvidenceEdge,
    EvidenceRelationshipType,
)


class EvidenceGraphTraverser:
    """
    Traverser for deterministic multi-hop evidence graphs.
    """

    @staticmethod
    def get_supporting_nodes(
        graph: EvidenceGraphResult,
        target_id: str,
    ) -> List[EvidenceNode]:
        support_rel_types = [
            EvidenceRelationshipType.SUPPORTS,
            EvidenceRelationshipType.CORROBORATES,
            EvidenceRelationshipType.DERIVED_FROM,
        ]
        source_ids = {
            edge.source_node_id
            for edge in graph.edges
            if edge.target_node_id == target_id and edge.relationship_type in support_rel_types
        }
        return [node for node in graph.nodes if node.id in source_ids]

    @staticmethod
    def get_contradicting_nodes(
        graph: EvidenceGraphResult,
        target_id: str,
    ) -> List[EvidenceNode]:
        source_ids = {
            edge.source_node_id
            for edge in graph.edges
            if edge.target_node_id == target_id
            and edge.relationship_type == EvidenceRelationshipType.CONTRADICTS
        }
        return [node for node in graph.nodes if node.id in source_ids]

    @staticmethod
    def filter_subgraph_by_depth(
        graph: EvidenceGraphResult,
        root_id: str,
        max_depth: int = 2,
    ) -> EvidenceGraphResult:
        visited_node_ids = {root_id}
        current_level_ids = {root_id}

        filtered_edges: List[EvidenceEdge] = []

        for _ in range(max_depth):
            next_level_ids = set()
            for edge in graph.edges:
                if edge.target_node_id in current_level_ids:
                    visited_node_ids.add(edge.source_node_id)
                    next_level_ids.add(edge.source_node_id)
                    if edge not in filtered_edges:
                        filtered_edges.append(edge)
                elif edge.source_node_id in current_level_ids:
                    visited_node_ids.add(edge.target_node_id)
                    next_level_ids.add(edge.target_node_id)
                    if edge not in filtered_edges:
                        filtered_edges.append(edge)
            current_level_ids = next_level_ids
            if not current_level_ids:
                break

        filtered_nodes = [n for n in graph.nodes if n.id in visited_node_ids]
        has_contradictions = any(
            e.relationship_type == EvidenceRelationshipType.CONTRADICTS for e in filtered_edges
        )

        return EvidenceGraphResult(
            nodes=filtered_nodes,
            edges=filtered_edges,
            has_contradictions=has_contradictions,
            contradiction_count=sum(
                1 for e in filtered_edges if e.relationship_type == EvidenceRelationshipType.CONTRADICTS
            ),
        )
