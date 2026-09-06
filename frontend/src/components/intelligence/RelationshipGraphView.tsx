import React, { useState } from 'react';
import { EvidenceGraphResult, EvidenceNode } from '../../types/intelligence';
import { EpistemicBadge } from './EpistemicBadge';
import { EvidenceStrengthBadge } from './EvidenceStrengthBadge';

interface Props {
  graph: EvidenceGraphResult;
  selectedNodeId?: string;
  onSelectNode?: (node: EvidenceNode) => void;
}

export const RelationshipGraphView: React.FC<Props> = ({
  graph,
  selectedNodeId,
  onSelectNode,
}) => {
  const [activeNode, setActiveNode] = useState<EvidenceNode | null>(
    graph.nodes[0] || null
  );

  const handleNodeClick = (node: EvidenceNode) => {
    setActiveNode(node);
    if (onSelectNode) {
      onSelectNode(node);
    }
  };

  const getRelationshipColor = (relType: string) => {
    switch (relType) {
      case 'SUPPORTS':
      case 'CORROBORATES':
        return 'text-emerald-400 border-emerald-500/40 bg-emerald-950/20';
      case 'CONTRADICTS':
        return 'text-rose-400 border-rose-500/60 bg-rose-950/30';
      case 'LOCATED_IN':
      case 'SPATIALLY_OVERLAPS':
        return 'text-sky-400 border-sky-500/40 bg-sky-950/20';
      case 'DERIVED_FROM':
      case 'SOURCE_OF':
        return 'text-amber-400 border-amber-500/40 bg-amber-950/20';
      default:
        return 'text-gray-400 border-gray-700 bg-gray-900';
    }
  };

  const getNodeIcon = (nodeType: string) => {
    switch (nodeType) {
      case 'ANALYSIS_RESULT':
        return '🎯';
      case 'CHANGE_EVENT':
        return '⚡';
      case 'MEASUREMENT':
        return '📐';
      case 'ROAD_DATA':
        return '🛣️';
      case 'RAW_SCENE':
        return '🛰️';
      default:
        return '📄';
    }
  };

  return (
    <div className="space-y-4">
      {/* Contradiction Alert Banner */}
      {graph.has_contradictions && (
        <div className="p-3 bg-rose-950/40 border border-rose-500/60 rounded-md flex items-start space-x-3">
          <span className="text-xl">⚠️</span>
          <div>
            <div className="text-xs font-bold text-rose-300 uppercase tracking-wider">
              Contradictory Evidence Detected ({graph.contradiction_count})
            </div>
            <div className="text-xs text-rose-200/80 mt-0.5">
              One or more sensor observations or evidence streams diverge in direction or magnitude. Evidence strength is downgraded to INSUFFICIENT for safety.
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left: Interactive Nodes & Edges Visual Hierarchy */}
        <div className="lg:col-span-2 space-y-3 bg-gray-900/60 border border-gray-800 rounded-lg p-3">
          <div className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center justify-between">
            <span>Evidence Graph Nodes ({graph.nodes.length})</span>
            <span className="text-[10px] text-gray-500 font-mono">DETERMINISTIC DAG</span>
          </div>

          <div className="space-y-2">
            {graph.nodes.map((node) => {
              const isSelected = (selectedNodeId || activeNode?.id) === node.id;
              const isRoot = node.node_type === 'ANALYSIS_RESULT';

              return (
                <div
                  key={node.id}
                  onClick={() => handleNodeClick(node)}
                  className={`p-2.5 rounded border transition-all cursor-pointer flex items-center justify-between ${
                    isSelected
                      ? 'bg-blue-950/40 border-blue-500 ring-1 ring-blue-500'
                      : isRoot
                      ? 'bg-gray-800/80 border-gray-700 hover:border-gray-600'
                      : 'bg-gray-950/40 border-gray-800 hover:border-gray-700'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <span className="text-base">{getNodeIcon(node.node_type)}</span>
                    <div>
                      <div className="text-xs font-semibold text-gray-200 flex items-center space-x-1.5">
                        <span>{node.label}</span>
                        {isRoot && (
                          <span className="text-[9px] px-1 py-0.2 bg-blue-500/20 text-blue-300 rounded border border-blue-500/40">
                            ROOT INTEL
                          </span>
                        )}
                      </div>
                      <div className="text-[10px] text-gray-400 font-mono">
                        {node.source_identifier}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-1.5">
                    <EpistemicBadge level={node.epistemic_level} />
                    <EvidenceStrengthBadge strength={node.evidence_strength} />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Relationship Edges */}
          <div className="pt-2 border-t border-gray-800">
            <div className="text-[11px] font-bold uppercase tracking-wider text-gray-400 mb-2">
              Relationship Edges ({graph.edges.length})
            </div>
            <div className="space-y-1.5">
              {graph.edges.map((edge) => {
                const sourceNode = graph.nodes.find((n) => n.id === edge.source_node_id);
                const targetNode = graph.nodes.find((n) => n.id === edge.target_node_id);

                return (
                  <div
                    key={edge.id}
                    className={`p-2 rounded border text-xs flex items-center justify-between font-mono ${getRelationshipColor(
                      edge.relationship_type
                    )}`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold">{sourceNode?.label || edge.source_node_id}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded border border-current font-bold uppercase">
                        --[{edge.relationship_type}]--&gt;
                      </span>
                      <span className="font-semibold">{targetNode?.label || edge.target_node_id}</span>
                    </div>

                    {edge.provenance?.formula && (
                      <span className="text-[10px] opacity-75">{edge.provenance.formula}</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right: Selected Node Detail Inspector */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-lg p-3 space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider text-gray-400">
            Evidence Node Inspector
          </div>

          {activeNode ? (
            <div className="space-y-2.5 text-xs">
              <div>
                <div className="text-[10px] text-gray-500 uppercase tracking-wider">Node Title</div>
                <div className="font-semibold text-gray-200 mt-0.5">{activeNode.label}</div>
              </div>

              <div>
                <div className="text-[10px] text-gray-500 uppercase tracking-wider">Source Telemetry / Asset</div>
                <div className="font-mono text-gray-300 mt-0.5">{activeNode.source_identifier}</div>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-1">
                <div>
                  <div className="text-[10px] text-gray-500 uppercase tracking-wider">Epistemic Tier</div>
                  <div className="mt-1">
                    <EpistemicBadge level={activeNode.epistemic_level} />
                  </div>
                </div>
                <div>
                  <div className="text-[10px] text-gray-500 uppercase tracking-wider">Pedigree Strength</div>
                  <div className="mt-1">
                    <EvidenceStrengthBadge strength={activeNode.evidence_strength} />
                  </div>
                </div>
              </div>

              {activeNode.properties && Object.keys(activeNode.properties).length > 0 && (
                <div className="pt-2 border-t border-gray-800">
                  <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">
                    Node Properties
                  </div>
                  <pre className="p-2 bg-black/40 border border-gray-800 rounded text-[10px] font-mono text-gray-300 overflow-x-auto">
                    {JSON.stringify(activeNode.properties, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="text-xs text-gray-500 italic py-6 text-center">
              Select an evidence node to inspect properties.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
