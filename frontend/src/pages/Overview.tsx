import React from 'react';
import {
  MOCK_PROJECTS,
  MOCK_GEOGRAPHIC_EVENTS,
  MOCK_LATEST_SCENE,
  MOCK_FUTURE_PREDICTIONS,
  MOCK_HISTORICAL_SUMMARIES,
  MOCK_DATASET_REGISTRY,
} from '../mock/demoData';
import { EvidenceStrengthBadge } from '../components/intelligence/EvidenceStrengthBadge';
import { HistoricalSupportBadge } from '../components/history/HistoricalSupportBadge';
import { EpistemicBadge } from '../components/intelligence/EpistemicBadge';
import {
  Globe,
  Activity,
  AlertTriangle,
  Database,
  TrendingUp,
  Clock,
} from 'lucide-react';

interface Props {
  onNavigateToMap: () => void;
}

export const Overview: React.FC<Props> = ({ onNavigateToMap }) => {
  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full font-sans" data-testid="overview-page">
      {/* Top Banner: Planetary Geospatial Intelligence Mission Status */}
      <div className="bg-orbit-carbon border border-orbit-border rounded-xl p-6 relative overflow-hidden shadow-lg">
        <div className="absolute right-0 top-0 bottom-0 w-96 bg-gradient-to-l from-orbit-emerald/10 to-transparent pointer-events-none"></div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold tracking-widest text-orbit-emerald bg-emerald-950/60 px-2.5 py-1 rounded border border-orbit-emerald/40 uppercase">
                OPERATIONAL STATUS • OBSERVATION READY
              </span>
              <span className="text-xs font-mono text-orbit-muted">
                PostGIS 3.4 Spatial Indexing Active
              </span>
            </div>
            <h1 className="text-2xl font-bold text-orbit-text mt-2">
              ORBIT Scientific Earth Intelligence Workstation
            </h1>
            <p className="text-sm text-orbit-muted mt-1 max-w-3xl font-normal">
              Autonomous multi-sensor satellite telemetry fusion, bi-temporal change detection, empirical historical reconstruction (1972–Present), and uncertainty-bounded scenario forecasting.
            </p>
          </div>

          <button
            onClick={onNavigateToMap}
            className="px-5 py-2.5 rounded-lg bg-orbit-emerald hover:bg-emerald-400 text-orbit-void font-mono font-bold text-xs transition shadow-glow-emerald flex items-center gap-2 shrink-0"
          >
            <Globe className="w-4 h-4" />
            <span>LAUNCH MAP WORKSPACE</span>
          </button>
        </div>
      </div>

      {/* Grid Row 1: Global Observation Status & Active Investigations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Card 1: Active Investigations */}
        <div className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-orbit-border/60 pb-3">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-orbit-emerald" />
              <h2 className="text-sm font-mono font-bold text-orbit-text uppercase">
                ACTIVE INVESTIGATIONS
              </h2>
            </div>
            <span className="text-xs font-mono font-bold text-orbit-emerald bg-orbit-emerald/10 px-2 py-0.5 rounded border border-orbit-emerald/30">
              {MOCK_PROJECTS.length} ACTIVE
            </span>
          </div>

          <div className="space-y-3">
            {MOCK_PROJECTS.map((p) => (
              <div
                key={p.id}
                className="p-3 bg-orbit-slate/30 hover:bg-orbit-slate/60 transition rounded-lg border border-orbit-border/60 cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-orbit-text font-mono truncate">{p.name}</h3>
                  <span className="text-[10px] font-mono text-orbit-emerald uppercase">{p.status}</span>
                </div>
                <p className="text-[11px] text-orbit-muted mt-1 line-clamp-2">{p.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Card 2: Recent Geographic Events */}
        <div className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-orbit-border/60 pb-3">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-orbit-warning" />
              <h2 className="text-sm font-mono font-bold text-orbit-text uppercase">
                DETECTED GEOGRAPHIC EVENTS
              </h2>
            </div>
            <span className="text-xs font-mono font-bold text-orbit-warning bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
              {MOCK_GEOGRAPHIC_EVENTS.length} CLUSTERS
            </span>
          </div>

          <div className="space-y-3">
            {MOCK_GEOGRAPHIC_EVENTS.map((evt) => (
              <div
                key={evt.id}
                className="p-3 bg-orbit-slate/30 rounded-lg border border-orbit-border/60 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-orbit-amber">
                    {evt.event_type}
                  </span>
                  <EvidenceStrengthBadge strength={evt.evidence_strength} size="sm" />
                </div>
                <p className="text-[11px] text-orbit-muted">{evt.description}</p>
                <div className="flex items-center justify-between text-[10px] font-mono text-orbit-muted pt-1 border-t border-orbit-border/40">
                  <span>Affected: {evt.affected_area_km2} km²</span>
                  <span>Confidence: {(evt.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Card 3: Latest Telemetry Acquisition */}
        <div className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-orbit-border/60 pb-3">
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-orbit-sky" />
              <h2 className="text-sm font-mono font-bold text-orbit-text uppercase">
                LATEST TELEMETRY SCENE
              </h2>
            </div>
            <EpistemicBadge level="OBSERVED" size="sm" />
          </div>

          <div className="p-3.5 bg-orbit-slate/30 rounded-lg border border-orbit-border/60 space-y-2 font-mono text-xs">
            <div className="text-[11px] text-orbit-text break-all font-semibold">
              {MOCK_LATEST_SCENE.provider_scene_id}
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px] text-orbit-muted pt-2 border-t border-orbit-border/40">
              <div>Platform: <span className="text-orbit-text">{MOCK_LATEST_SCENE.platform}</span></div>
              <div>Sensor: <span className="text-orbit-text">{MOCK_LATEST_SCENE.sensor}</span></div>
              <div>Resolution: <span className="text-orbit-text">{MOCK_LATEST_SCENE.spatial_resolution}m</span></div>
              <div>Cloud Cover: <span className="text-orbit-emerald">{MOCK_LATEST_SCENE.cloud_cover}%</span></div>
            </div>
          </div>

          <div className="p-3 bg-emerald-950/20 border border-orbit-emerald/30 rounded-lg text-xs font-mono text-orbit-emerald">
            ✓ Co-registered with Copernicus Sentinel-1 SAR GRD and USGS Landsat Collection 2.
          </div>
        </div>
      </div>

      {/* Grid Row 2: Multi-Decadal Historical Coverage & Future Predictions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Historical Coverage Matrix */}
        <div className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-orbit-border/60 pb-3">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-orbit-emerald" />
              <h2 className="text-sm font-mono font-bold text-orbit-text uppercase">
                HISTORICAL OBSERVATION MATRIX (1972–2026)
              </h2>
            </div>
            <span className="text-xs font-mono text-orbit-muted">54 YEARS SPAN</span>
          </div>

          <div className="space-y-2">
            {MOCK_HISTORICAL_SUMMARIES.slice(0, 4).map((h) => (
              <div
                key={h.id}
                className="p-2.5 bg-orbit-slate/20 rounded-md border border-orbit-border/50 flex items-center justify-between font-mono text-xs"
              >
                <div className="flex items-center gap-3">
                  <span className="font-bold text-orbit-text">{h.year}</span>
                  <span className="text-orbit-muted text-[11px]">
                    Mean NDVI: <strong className="text-orbit-emerald">{h.summary_data.mean_ndvi ?? 'N/A'}</strong>
                  </span>
                </div>
                <HistoricalSupportBadge classification={h.support_classification} size="sm" />
              </div>
            ))}
          </div>
        </div>

        {/* Future Predictions Horizon */}
        <div className="bg-orbit-carbon border border-purple-500/30 rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-orbit-border/60 pb-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-purple-400" />
              <h2 className="text-sm font-mono font-bold text-purple-300 uppercase">
                SCIENTIFIC PROJECTION HORIZON (2030–2050)
              </h2>
            </div>
            <span className="text-[10px] font-mono font-bold text-purple-400 bg-purple-950/60 px-2 py-0.5 rounded border border-purple-800">
              SIMULATION
            </span>
          </div>

          <div className="space-y-3">
            {MOCK_FUTURE_PREDICTIONS.map((pred) => (
              <div
                key={pred.id}
                className="p-3 bg-orbit-slate/20 rounded-lg border border-purple-500/30 flex items-center justify-between font-mono text-xs"
              >
                <div>
                  <div className="font-semibold text-purple-200">
                    {pred.prediction_type.replace(/_/g, ' ')}
                  </div>
                  <div className="text-[11px] text-orbit-muted mt-0.5">
                    Scenario: {pred.scenario} • Model: {pred.model_name}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-bold text-purple-300">
                    {pred.prediction_value > 0 ? `+${pred.prediction_value}` : pred.prediction_value} {pred.unit}
                  </div>
                  <div className="text-[10px] text-purple-400">Target: {pred.target_year}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Grid Row 3: Open Data Source Registry & Licensing Status */}
      <div className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-orbit-border/60 pb-3">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-orbit-emerald" />
            <h2 className="text-sm font-mono font-bold text-orbit-text uppercase">
              EARTH OBSERVATION DATASET REGISTRY & LICENSING
            </h2>
          </div>
          <span className="text-xs font-mono text-orbit-emerald">PUBLIC & OPEN DATASETS ONLY</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
          {MOCK_DATASET_REGISTRY.map((ds) => (
            <div key={ds.id} className="p-3.5 bg-orbit-slate/20 rounded-lg border border-orbit-border/60 space-y-2">
              <div className="font-bold text-orbit-text">{ds.dataset_name}</div>
              <div className="text-[11px] text-orbit-muted">Provider: {ds.provider}</div>
              <div className="text-[10px] text-orbit-emerald bg-emerald-950/40 p-1.5 rounded border border-orbit-emerald/30">
                License: {ds.license}
              </div>
              <div className="text-[9px] text-orbit-muted/80">Attribution: {ds.attribution}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
