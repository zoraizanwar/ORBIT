import React, { useState } from 'react';
import {
  DEMO_INTELLIGENCE_FIXTURES,
} from '../../services/intelligenceService';
import { IntelligenceObjectResult } from '../../types/intelligence';
import { EpistemicBadge } from './EpistemicBadge';
import { EvidenceStrengthBadge } from './EvidenceStrengthBadge';
import { RelationshipGraphView } from './RelationshipGraphView';
import { SpatialContextCard } from './SpatialContextCard';
import { TemporalContextCard } from './TemporalContextCard';
import { EvidencePanel } from './EvidencePanel';
import { Sparkles, Network, MapPin, FileText, CheckCircle2 } from 'lucide-react';

export const AdvancedIntelligencePanel: React.FC = () => {
  const [fixtures] = useState<IntelligenceObjectResult[]>(DEMO_INTELLIGENCE_FIXTURES);
  const [selectedIntelId, setSelectedIntelId] = useState<string>(fixtures[0].id);
  const [subTab, setSubTab] = useState<'overview' | 'graph' | 'evidence' | 'spatial' | 'trace'>('overview');

  const activeIntel = fixtures.find((f) => f.id === selectedIntelId) || fixtures[0];

  return (
    <div className="space-y-4 font-mono text-xs" data-testid="advanced-intelligence-panel">
      {/* Top Selector: Active Intelligence Event */}
      <div className="space-y-1.5">
        <label className="text-[10px] text-orbit-muted uppercase tracking-wider font-bold">
          SELECT INTELLIGENCE OBJECT
        </label>
        <select
          value={selectedIntelId}
          onChange={(e) => setSelectedIntelId(e.target.value)}
          className="w-full bg-orbit-slate/80 border border-orbit-border text-orbit-text text-xs rounded px-2.5 py-1.5 focus:ring-1 focus:ring-orbit-emerald focus:outline-none"
        >
          {fixtures.map((f) => (
            <option key={f.id} value={f.id}>
              [{f.intelligence_type}] {f.title} ({f.affected_area_km2.toFixed(2)} km²)
            </option>
          ))}
        </select>
      </div>

      {/* Sub-tab Navigation */}
      <div className="flex border-b border-orbit-border bg-orbit-void/40 text-[10px] overflow-x-auto scrollbar-none">
        <button
          onClick={() => setSubTab('overview')}
          className={`flex-1 py-1.5 px-2 text-center border-b-2 transition whitespace-nowrap flex items-center justify-center gap-1 ${
            subTab === 'overview'
              ? 'border-orbit-emerald text-orbit-emerald font-bold bg-orbit-emerald/5'
              : 'border-transparent text-orbit-muted hover:text-orbit-text'
          }`}
        >
          <Sparkles className="w-3 h-3" />
          <span>OVERVIEW</span>
        </button>
        <button
          onClick={() => setSubTab('graph')}
          className={`flex-1 py-1.5 px-2 text-center border-b-2 transition whitespace-nowrap flex items-center justify-center gap-1 ${
            subTab === 'graph'
              ? 'border-orbit-emerald text-orbit-emerald font-bold bg-orbit-emerald/5'
              : 'border-transparent text-orbit-muted hover:text-orbit-text'
          }`}
        >
          <Network className="w-3 h-3" />
          <span>GRAPH</span>
        </button>
        <button
          onClick={() => setSubTab('evidence')}
          className={`flex-1 py-1.5 px-2 text-center border-b-2 transition whitespace-nowrap flex items-center justify-center gap-1 ${
            subTab === 'evidence'
              ? 'border-orbit-emerald text-orbit-emerald font-bold bg-orbit-emerald/5'
              : 'border-transparent text-orbit-muted hover:text-orbit-text'
          }`}
        >
          <FileText className="w-3 h-3" />
          <span>RECORDS</span>
        </button>
        <button
          onClick={() => setSubTab('spatial')}
          className={`flex-1 py-1.5 px-2 text-center border-b-2 transition whitespace-nowrap flex items-center justify-center gap-1 ${
            subTab === 'spatial'
              ? 'border-orbit-emerald text-orbit-emerald font-bold bg-orbit-emerald/5'
              : 'border-transparent text-orbit-muted hover:text-orbit-text'
          }`}
        >
          <MapPin className="w-3 h-3" />
          <span>CONTEXT</span>
        </button>
        <button
          onClick={() => setSubTab('trace')}
          className={`flex-1 py-1.5 px-2 text-center border-b-2 transition whitespace-nowrap flex items-center justify-center gap-1 ${
            subTab === 'trace'
              ? 'border-orbit-emerald text-orbit-emerald font-bold bg-orbit-emerald/5'
              : 'border-transparent text-orbit-muted hover:text-orbit-text'
          }`}
        >
          <CheckCircle2 className="w-3 h-3" />
          <span>TRACE</span>
        </button>
      </div>

      {/* SUBTAB 1: OVERVIEW */}
      {subTab === 'overview' && (
        <div className="space-y-3">
          <div className="bg-orbit-slate/30 p-3 rounded-lg border border-orbit-border space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-orbit-muted uppercase">{activeIntel.intelligence_type}</span>
              <div className="flex items-center space-x-1.5">
                <EpistemicBadge level={activeIntel.epistemic_level} size="sm" />
                <EvidenceStrengthBadge strength={activeIntel.evidence_strength} size="sm" />
              </div>
            </div>

            <div className="text-xs font-bold text-orbit-text">{activeIntel.title}</div>

            <div className="grid grid-cols-2 gap-2 text-[11px] pt-2 border-t border-orbit-border/50 text-orbit-muted">
              <div>
                Affected Surface: <span className="text-orbit-emerald font-bold">{activeIntel.affected_area_km2.toFixed(2)} km²</span>
              </div>
              <div>
                Confidence: <span className="text-orbit-text font-bold">{(activeIntel.confidence * 100).toFixed(0)}%</span>
              </div>
              <div>
                Rule: <span className="text-orbit-text font-mono">{activeIntel.rule_id}</span>
              </div>
              <div>
                Status:{' '}
                <span
                  className={`font-bold ${
                    activeIntel.status === 'CONTRADICTED'
                      ? 'text-rose-400'
                      : 'text-emerald-400'
                  }`}
                >
                  {activeIntel.status}
                </span>
              </div>
            </div>
          </div>

          <SpatialContextCard context={activeIntel.spatial_context} />
          <TemporalContextCard context={activeIntel.temporal_context} />
        </div>
      )}

      {/* SUBTAB 2: EVIDENCE GRAPH */}
      {subTab === 'graph' && (
        <RelationshipGraphView graph={activeIntel.evidence_graph} />
      )}

      {/* SUBTAB 3: EVIDENCE RECORDS */}
      {subTab === 'evidence' && (
        <EvidencePanel />
      )}

      {/* SUBTAB 4: SPATIAL CONTEXT */}
      {subTab === 'spatial' && (
        <div className="space-y-3">
          <SpatialContextCard context={activeIntel.spatial_context} />
          <TemporalContextCard context={activeIntel.temporal_context} />
        </div>
      )}

      {/* SUBTAB 5: PROVENANCE TRACE */}
      {subTab === 'trace' && (
        <div className="space-y-3">
          <div className="p-3 bg-orbit-slate/30 border border-orbit-border rounded-lg space-y-2">
            <div className="text-[10px] font-bold text-orbit-muted uppercase">
              DETERMINISTIC COMPUTATION LINEAGE
            </div>
            <pre className="p-2 bg-black/60 border border-gray-800 rounded text-[10px] font-mono text-orbit-emerald overflow-x-auto">
              {JSON.stringify(activeIntel.provenance, null, 2)}
            </pre>
          </div>

          <div className="p-3 bg-orbit-slate/30 border border-orbit-border rounded-lg space-y-2">
            <div className="text-[10px] font-bold text-orbit-muted uppercase">
              QUALITY & COMPLETENESS METRICS
            </div>
            <pre className="p-2 bg-black/60 border border-gray-800 rounded text-[10px] font-mono text-orbit-cyan overflow-x-auto">
              {JSON.stringify(activeIntel.quality_metadata, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};
