import React, { useState } from 'react';
import {
  MOCK_AOI,
  MOCK_LATEST_SCENE,
  MOCK_MEASUREMENTS,
  MOCK_EVIDENCE_RECORDS,
} from '../../mock/demoData';
import { EvidenceStrengthBadge } from './EvidenceStrengthBadge';
import { EpistemicBadge } from './EpistemicBadge';
import {
  Satellite,
  ChevronRight,
  ChevronLeft,
  Hash,
} from 'lucide-react';

import { FeatureInspectionPayload } from '../../map/mapTypes';
import { RasterIntelligencePanel } from '../raster/RasterIntelligencePanel';
import { ChangeDetectionPanel } from '../change/ChangeDetectionPanel';
import { AdvancedIntelligencePanel } from './AdvancedIntelligencePanel';
import { ForecastPanel } from '../forecast/ForecastPanel';
import { AIIntelligencePanel } from '../ai/AIIntelligencePanel';

interface Props {
  isOpen: boolean;
  onToggle: () => void;
  selectedFeature?: FeatureInspectionPayload | null;
}

export const IntelligencePanel: React.FC<Props> = ({ isOpen, onToggle, selectedFeature }) => {
  const [activeTab, setActiveTab] = useState<'observation' | 'raster' | 'changes' | 'intel' | 'evidence' | 'ai' | 'forecast'>('observation');

  if (!isOpen) {
    return (
      <div className="absolute right-0 top-1/2 -translate-y-1/2 z-20">
        <button
          onClick={onToggle}
          className="bg-orbit-carbon border-l border-y border-orbit-border p-2 rounded-l-lg text-orbit-muted hover:text-orbit-emerald shadow-xl transition flex items-center gap-1 font-mono text-xs"
          title="Open Intelligence Inspector"
          data-testid="open-intelligence-panel-btn"
        >
          <ChevronLeft className="w-4 h-4" />
          <span className="[writing-mode:vertical-rl] tracking-widest text-[10px] uppercase font-bold py-1">
            INTELLIGENCE INSPECTOR
          </span>
        </button>
      </div>
    );
  }

  return (
    <aside
      className="w-80 lg:w-96 bg-orbit-carbon border-l border-orbit-border flex flex-col h-full z-20 select-none shrink-0"
      data-testid="intelligence-panel"
    >
      {/* Inspector Header */}
      <div className="p-3.5 border-b border-orbit-border flex items-center justify-between bg-orbit-slate/40">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-md bg-orbit-emerald/10 text-orbit-emerald border border-orbit-emerald/30">
            <Satellite className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-mono font-bold text-orbit-text tracking-wider uppercase">
              INTELLIGENCE INSPECTOR
            </h3>
            <p className="text-[10px] font-mono text-orbit-muted truncate max-w-[180px]">
              {MOCK_AOI.name}
            </p>
          </div>
        </div>
        <button
          onClick={onToggle}
          className="p-1.5 rounded-md hover:bg-orbit-slate text-orbit-muted hover:text-orbit-text transition"
          title="Collapse Panel"
          data-testid="collapse-intelligence-panel-btn"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Tab Navigation Buttons */}
      <div className="flex border-b border-orbit-border bg-orbit-void/50 text-[10px] font-mono overflow-x-auto scrollbar-none">
        <button
          onClick={() => setActiveTab('observation')}
          className={`flex-1 py-2 px-2 text-center border-b-2 transition whitespace-nowrap ${
            activeTab === 'observation'
              ? 'border-orbit-emerald text-orbit-emerald font-bold bg-orbit-emerald/5'
              : 'border-transparent text-orbit-muted hover:text-orbit-text'
          }`}
        >
          OBSERVE
        </button>
        <button
          onClick={() => setActiveTab('raster')}
          className={`flex-1 py-2 px-2 text-center border-b-2 transition whitespace-nowrap ${
            activeTab === 'raster'
              ? 'border-orbit-emerald text-orbit-emerald font-bold bg-orbit-emerald/5'
              : 'border-transparent text-orbit-muted hover:text-orbit-text'
          }`}
        >
          RASTER
        </button>
        <button
          onClick={() => setActiveTab('changes')}
          className={`flex-1 py-2 px-2 text-center border-b-2 transition whitespace-nowrap ${
            activeTab === 'changes'
              ? 'border-orbit-emerald text-orbit-emerald font-bold bg-orbit-emerald/5'
              : 'border-transparent text-orbit-muted hover:text-orbit-text'
          }`}
        >
          CHANGES
        </button>
        <button
          onClick={() => setActiveTab('intel')}
          className={`flex-1 py-2 px-2 text-center border-b-2 transition whitespace-nowrap ${
            activeTab === 'intel'
              ? 'border-orbit-emerald text-orbit-emerald font-bold bg-orbit-emerald/5'
              : 'border-transparent text-orbit-muted hover:text-orbit-text'
          }`}
        >
          INTEL
        </button>
        <button
          onClick={() => setActiveTab('evidence')}
          className={`flex-1 py-2 px-2 text-center border-b-2 transition whitespace-nowrap ${
            activeTab === 'evidence'
              ? 'border-orbit-emerald text-orbit-emerald font-bold bg-orbit-emerald/5'
              : 'border-transparent text-orbit-muted hover:text-orbit-text'
          }`}
        >
          EVIDENCE
        </button>
        <button
          onClick={() => setActiveTab('ai')}
          className={`flex-1 py-2 px-2 text-center border-b-2 transition whitespace-nowrap ${
            activeTab === 'ai'
              ? 'border-orbit-cyan text-orbit-cyan font-bold bg-orbit-cyan/5'
              : 'border-transparent text-orbit-muted hover:text-orbit-text'
          }`}
        >
          AI SYNTH
        </button>
        <button
          onClick={() => setActiveTab('forecast')}
          className={`flex-1 py-2 px-2 text-center border-b-2 transition whitespace-nowrap ${
            activeTab === 'forecast'
              ? 'border-purple-400 text-purple-300 font-bold bg-purple-950/20'
              : 'border-transparent text-purple-400/60 hover:text-purple-300'
          }`}
        >
          FORECAST
        </button>
      </div>

      {/* Selected Map Feature Banner */}
      {selectedFeature && (
        <div className="p-3 bg-orbit-slate/60 border-b border-orbit-border space-y-1.5 font-mono text-xs">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-orbit-emerald font-bold uppercase tracking-wider">
              INSPECTED {selectedFeature.featureType}
            </span>
            {selectedFeature.evidenceStrength && (
              <EvidenceStrengthBadge strength={selectedFeature.evidenceStrength} size="sm" />
            )}
          </div>
          <div className="font-bold text-orbit-text text-sm truncate">{selectedFeature.name}</div>
          <div className="text-[10px] text-orbit-muted flex items-center justify-between">
            <span>ID: {selectedFeature.featureId}</span>
            <span>
              {selectedFeature.coordinates.lat.toFixed(4)}°, {selectedFeature.coordinates.lng.toFixed(4)}°
            </span>
          </div>
        </div>
      )}

      {/* Tab Content Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono scrollbar-thin text-xs">
        {/* TAB 1: OBSERVATION */}
        {activeTab === 'observation' && (
          <div className="space-y-4">
            <div className="bg-orbit-slate/30 p-3 rounded-lg border border-orbit-border space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-orbit-muted uppercase">LATEST TELEMETRY SCENE</span>
                <EpistemicBadge level="OBSERVED" size="sm" />
              </div>
              <div className="text-xs font-semibold text-orbit-text break-all">
                {MOCK_LATEST_SCENE.provider_scene_id}
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px] pt-2 border-t border-orbit-border/50 text-orbit-muted">
                <div>
                  Platform: <span className="text-orbit-text">{MOCK_LATEST_SCENE.platform}</span>
                </div>
                <div>
                  Sensor: <span className="text-orbit-text">{MOCK_LATEST_SCENE.sensor}</span>
                </div>
                <div>
                  Resolution: <span className="text-orbit-text">{MOCK_LATEST_SCENE.spatial_resolution}m GSD</span>
                </div>
                <div>
                  Cloud Cover: <span className="text-orbit-emerald">{MOCK_LATEST_SCENE.cloud_cover}%</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-[10px] font-bold text-orbit-muted uppercase tracking-wider">
                AUTHORITATIVE MEASUREMENTS (LEVEL 1)
              </div>
              {MOCK_MEASUREMENTS.map((m) => (
                <div key={m.id} className="p-2.5 bg-orbit-slate/20 rounded-md border border-orbit-border/60">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] text-orbit-muted">{m.measurement_type}</span>
                    <EpistemicBadge level={m.epistemic_level} size="sm" />
                  </div>
                  <div className="text-sm font-bold text-orbit-emerald mt-1">
                    {m.value} {m.unit}
                    {m.uncertainty && (
                      <span className="text-[10px] text-orbit-muted font-normal ml-1">
                        (±{m.uncertainty} {m.unit})
                      </span>
                    )}
                  </div>
                  <div className="text-[9px] text-orbit-muted/70 mt-1 truncate">
                    Method: {m.methodology}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB: RASTER INTELLIGENCE */}
        {activeTab === 'raster' && (
          <RasterIntelligencePanel />
        )}

        {/* TAB 2: DETECTED CHANGES */}
        {activeTab === 'changes' && (
          <ChangeDetectionPanel />
        )}

        {/* TAB: ADVANCED GEOSPATIAL INTELLIGENCE */}
        {activeTab === 'intel' && (
          <AdvancedIntelligencePanel />
        )}

        {/* TAB 3: EVIDENCE RECORD */}
        {activeTab === 'evidence' && (
          <div className="space-y-3">
            <div className="text-[10px] font-bold text-orbit-muted uppercase">
              CRYPTOGRAPHIC PROVENANCE DAG
            </div>
            {MOCK_EVIDENCE_RECORDS.map((ev) => (
              <div key={ev.id} className="p-3 bg-orbit-slate/30 rounded-lg border border-orbit-border space-y-2 text-[11px]">
                <div className="flex items-center justify-between">
                  <span className="text-orbit-sky font-semibold">{ev.claim_type}</span>
                  <EvidenceStrengthBadge strength={ev.evidence_strength} size="sm" />
                </div>
                <div>
                  Claim Ref: <span className="text-orbit-text">{ev.claim_reference}</span>
                </div>
                <div className="p-1.5 bg-orbit-void rounded border border-orbit-border font-mono text-[9px] text-orbit-emerald break-all flex items-center gap-1">
                  <Hash className="w-3 h-3 shrink-0" />
                  <span>SHA256: {ev.input_checksum}</span>
                </div>
                <div className="text-[10px] text-orbit-muted">
                  Algorithm: <span className="text-orbit-text">{ev.algorithm}</span> ({ev.processing_version})
                </div>
              </div>
            ))}
          </div>
        )}

        {/* TAB 4: AI SYNTHESIS */}
        {activeTab === 'ai' && (
          <AIIntelligencePanel />
        )}

        {/* TAB 5: FORECAST */}
        {activeTab === 'forecast' && (
          <ForecastPanel />
        )}
      </div>
    </aside>
  );
};
