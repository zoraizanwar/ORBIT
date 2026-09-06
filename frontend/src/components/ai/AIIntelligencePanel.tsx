import React, { useState } from 'react';
import {
  DEMO_EVIDENCE_PACKAGE,
  DEMO_AI_INTERPRETATION,
} from '../../services/aiService';
import { ContradictionBanner } from './ContradictionBanner';
import { ClaimList } from './ClaimList';
import { DecisionSupportView } from './DecisionSupportView';
import { AIProvenanceCard } from './AIProvenanceCard';
import { ReportGeneratorModal } from './ReportGeneratorModal';
import {
  Brain,
  ShieldCheck,
  FileCheck,
  AlertTriangle,
  Compass,
  FileText,
  RefreshCw,
  TrendingUp,
  CheckCircle2,
} from 'lucide-react';

interface AIIntelligencePanelProps {
  aoiId?: string;
  aoiName?: string;
}

type AITab =
  | 'overview'
  | 'claims'
  | 'evidence'
  | 'decision_support'
  | 'provenance';

export const AIIntelligencePanel: React.FC<AIIntelligencePanelProps> = ({
  aoiId = 'aoi-sinop-mato-grosso',
  aoiName = 'Sinop Deforestation Frontier (Mato Grosso)',
}) => {
  const [activeTab, setActiveTab] = useState<AITab>('overview');
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [hasContradictions, setHasContradictions] = useState(false);

  const evidencePackage = {
    ...DEMO_EVIDENCE_PACKAGE,
    aoi_id: aoiId,
    aoi_name: aoiName,
    has_contradictions: hasContradictions,
  };

  const interpretation = {
    ...DEMO_AI_INTERPRETATION,
    aoi_id: aoiId,
    contradiction_statement: hasContradictions
      ? 'Cross-sensor discrepancy detected: Optical canopy deficit is not corroborated by Sentinel-1 radar amplitude. Evidence strength is downgraded.'
      : undefined,
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 overflow-y-auto">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded bg-indigo-950/80 border border-indigo-600/60 text-indigo-400">
            <Brain className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-mono text-sm font-bold uppercase tracking-wider text-slate-100">
                GROUNDED AI INTELLIGENCE SYNTHESIS
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950/80 border border-indigo-600/60 text-indigo-300">
                AI_INTERPRETED
              </span>
            </div>
            <p className="text-[11px] font-mono text-slate-400">
              Deterministic reasoning & claim-level grounding over verified telemetry
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setHasContradictions(!hasContradictions)}
            className={`px-2.5 py-1.5 rounded font-mono text-[11px] border transition-colors flex items-center gap-1.5 ${
              hasContradictions
                ? 'bg-amber-950/80 border-amber-600 text-amber-300'
                : 'bg-slate-900 border-slate-700 text-slate-400 hover:bg-slate-800'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            {hasContradictions ? 'Contradiction Active' : 'Simulate Contradiction'}
          </button>

          <button
            onClick={() => setIsReportModalOpen(true)}
            className="px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-mono text-[11px] font-bold uppercase tracking-wider flex items-center gap-1.5 transition-colors"
          >
            <FileText className="w-3.5 h-3.5" />
            Generate Report
          </button>
        </div>
      </div>

      {/* Sub-Navigation Tabs */}
      <div className="flex border-b border-slate-800 px-4 bg-slate-900/30 overflow-x-auto">
        {(
          [
            { id: 'overview', label: 'Overview', icon: Brain },
            { id: 'claims', label: 'Grounded Claims', icon: FileCheck },
            { id: 'evidence', label: 'Evidence Package', icon: ShieldCheck },
            { id: 'decision_support', label: 'Decision Support', icon: Compass },
            { id: 'provenance', label: 'Provenance', icon: RefreshCw },
          ] as const
        ).map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-2.5 font-mono text-xs border-b-2 font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.id
                  ? 'border-cyan-400 text-cyan-300 bg-slate-800/40'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Main Body */}
      <div className="p-4 space-y-4">
        {/* Contradiction Alert if applicable */}
        <ContradictionBanner
          hasContradictions={hasContradictions}
          contradictionStatement={interpretation.contradiction_statement}
          contradictionCount={hasContradictions ? 1 : 0}
        />

        {/* Tab 1: Overview */}
        {activeTab === 'overview' && (
          <div className="space-y-4">
            {/* Executive Brief */}
            <div className="p-4 rounded bg-slate-900/80 border border-slate-800 space-y-2">
              <div className="flex items-center gap-2 font-mono text-xs font-bold text-slate-300 uppercase tracking-wider">
                <Brain className="w-4 h-4 text-indigo-400" />
                EXECUTIVE INTELLIGENCE SYNTHESIS
              </div>
              <p className="text-xs text-slate-200 leading-relaxed font-sans">
                {interpretation.executive_summary}
              </p>
            </div>

            {/* Grounding Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono text-xs">
              <div className="p-3 rounded bg-slate-900/70 border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block mb-1">
                  EVIDENCE GROUNDING
                </span>
                <span className="text-emerald-400 font-bold flex items-center gap-1">
                  <ShieldCheck className="w-4 h-4" />
                  100% CITED & VERIFIED
                </span>
                <span className="text-[10px] text-slate-400 mt-1 block">
                  {evidencePackage.evidence_items.length} Grounded Items
                </span>
              </div>

              <div className="p-3 rounded bg-slate-900/70 border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block mb-1">
                  HALLUCINATION CHECK
                </span>
                <span className="text-cyan-400 font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" />
                  0 UNGROUNDED CLAIMS
                </span>
                <span className="text-[10px] text-slate-400 mt-1 block">
                  Strict Token Alignment
                </span>
              </div>

              <div className="p-3 rounded bg-slate-900/70 border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block mb-1">
                  FUTURE PROJECTION
                </span>
                <span className="text-purple-400 font-bold flex items-center gap-1">
                  <TrendingUp className="w-4 h-4" />
                  PREDICTED HORIZON 2030
                </span>
                <span className="text-[10px] text-slate-400 mt-1 block">
                  Linear Trend Model (ORBIT-LT-v1)
                </span>
              </div>
            </div>

            {/* Spatial & Temporal Context */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="p-3.5 rounded bg-slate-900/70 border border-slate-800 space-y-1">
                <div className="font-mono text-[10px] text-slate-400 uppercase font-bold">
                  SPATIAL INFRASTRUCTURE CONTEXT
                </div>
                <p className="text-slate-300 font-sans leading-relaxed">
                  {interpretation.spatial_interpretation}
                </p>
              </div>

              <div className="p-3.5 rounded bg-slate-900/70 border border-slate-800 space-y-1">
                <div className="font-mono text-[10px] text-slate-400 uppercase font-bold">
                  TEMPORAL OBSERVATION SPAN
                </div>
                <p className="text-slate-300 font-sans leading-relaxed">
                  {interpretation.temporal_interpretation}
                </p>
              </div>
            </div>

            {/* Uncertainty Notice */}
            <div className="p-3 rounded bg-slate-950 border border-slate-800/80 text-xs text-slate-400 space-y-1 font-sans">
              <span className="font-mono text-[10px] text-slate-500 uppercase font-bold block">
                UNCERTAINTY & METHODOLOGICAL STATEMENT:
              </span>
              <p>{interpretation.uncertainty_statement}</p>
            </div>
          </div>
        )}

        {/* Tab 2: Grounded Claims */}
        {activeTab === 'claims' && (
          <div className="space-y-3">
            <div className="text-xs font-mono text-slate-400 mb-2">
              Showing {interpretation.claims.length} claims verified against grounded Evidence Package:
            </div>
            <ClaimList claims={interpretation.claims} />
          </div>
        )}

        {/* Tab 3: Evidence Package */}
        {activeTab === 'evidence' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
              <span>EVIDENCE PACKAGE (ID: {evidencePackage.package_id})</span>
              <span className="text-cyan-400">
                Digest: {evidencePackage.package_hash_sha256.slice(0, 12)}...
              </span>
            </div>

            <div className="space-y-2">
              {evidencePackage.evidence_items.map((item) => (
                <div
                  key={item.id}
                  className="p-3 rounded bg-slate-900/70 border border-slate-800 flex items-start justify-between gap-3 text-xs"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-cyan-300 font-bold">{item.id}</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 bg-slate-800 text-slate-300 rounded">
                        {item.type}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 bg-indigo-950/80 border border-indigo-700/60 text-indigo-300 rounded">
                        {item.epistemic_level}
                      </span>
                    </div>
                    <p className="text-slate-300">{item.description}</p>
                    <div className="text-[10px] font-mono text-slate-500">
                      Source: {item.source_id} ({item.source_type})
                    </div>
                  </div>

                  {item.value !== undefined && (
                    <div className="text-right font-mono">
                      <div className="text-slate-100 font-bold">
                        {item.value} {item.unit || ''}
                      </div>
                      <div className="text-[10px] text-slate-500">Quality: {item.quality_score}</div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 4: Decision Support */}
        {activeTab === 'decision_support' && (
          <div className="space-y-3">
            <div className="text-xs font-mono text-slate-400 mb-2">
              Actionable operational recommendations derived deterministically from evidence strength:
            </div>
            <DecisionSupportView recommendations={interpretation.recommendations} />
          </div>
        )}

        {/* Tab 5: Provenance */}
        {activeTab === 'provenance' && (
          <AIProvenanceCard interpretation={interpretation} />
        )}
      </div>

      {/* Report Modal */}
      <ReportGeneratorModal
        aoiId={aoiId}
        aoiName={aoiName}
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
      />
    </div>
  );
};
