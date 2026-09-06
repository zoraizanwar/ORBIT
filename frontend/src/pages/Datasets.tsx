import React from 'react';
import { MOCK_DATASET_REGISTRY } from '../mock/demoData';
import { Satellite, Database, CheckCircle2 } from 'lucide-react';

export const Datasets: React.FC = () => {
  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full font-sans" data-testid="datasets-page">
      {/* Header */}
      <div className="border-b border-orbit-border/60 pb-4">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono font-bold tracking-widest text-orbit-emerald bg-emerald-950/60 px-2.5 py-1 rounded border border-orbit-emerald/40 uppercase">
            AUTHORITATIVE SATELLITE DATA
          </span>
        </div>
        <h1 className="text-xl font-bold text-orbit-text mt-1">
          Satellite Data Providers & Imagery Registry
        </h1>
        <p className="text-xs text-orbit-muted mt-0.5 max-w-2xl leading-relaxed">
          Where ORBIT gets its satellite photos: Free, open, and authoritative scientific space agencies around the world (ESA, NASA, and OpenStreetMap).
        </p>
      </div>

      {/* Explainer Box */}
      <div className="p-4 bg-orbit-carbon border border-orbit-border rounded-xl flex items-start gap-3 shadow-sm">
        <Database className="w-5 h-5 text-orbit-emerald shrink-0 mt-0.5" />
        <div className="text-xs space-y-1 text-orbit-muted leading-relaxed">
          <span className="font-bold text-orbit-text">Zero Vendor Lock-In & Open Science:</span>
          <p>
            ORBIT connects directly to open public satellites. You do not need expensive proprietary cloud subscriptions to monitor our planet.
          </p>
        </div>
      </div>

      {/* Datasets Cards */}
      <div className="space-y-4">
        {MOCK_DATASET_REGISTRY.map((ds) => (
          <div
            key={ds.id}
            className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 space-y-4 shadow-sm hover:border-orbit-emerald/40 transition"
          >
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 border-b border-orbit-border/60 pb-3">
              <div className="space-y-1">
                <span className="text-[10px] font-mono font-bold text-orbit-emerald bg-emerald-950/40 px-2 py-0.5 rounded border border-orbit-emerald/30 uppercase">
                  {ds.provider}
                </span>
                <h2 className="text-base font-bold text-orbit-text mt-1 flex items-center gap-2">
                  <Satellite className="w-4 h-4 text-orbit-sky shrink-0" />
                  <span>{ds.dataset_name}</span>
                </h2>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <span className="text-[10px] font-mono font-bold text-orbit-sky bg-sky-950/40 px-2.5 py-1 rounded border border-orbit-sky/30">
                  {ds.modality === 'OPTICAL' ? '📷 Optical Color & Infrared' : ds.modality === 'SAR' ? '📡 All-Weather Radar' : '🗺️ Map Vectors'}
                </span>
                <span className="text-[10px] font-mono font-bold text-orbit-emerald bg-emerald-950/40 px-2.5 py-1 rounded border border-orbit-emerald/30 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>Connected</span>
                </span>
              </div>
            </div>

            <p className="text-xs text-orbit-text leading-relaxed bg-orbit-slate/20 p-3 rounded-lg border border-orbit-border/40">
              {ds.description}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-1">
              <div className="p-2.5 bg-orbit-slate/30 rounded-lg border border-orbit-border/40">
                <span className="text-[10px] font-mono text-orbit-muted uppercase block">License & Open Access</span>
                <strong className="text-orbit-emerald text-[11px] block mt-0.5">{ds.license}</strong>
              </div>

              <div className="p-2.5 bg-orbit-slate/30 rounded-lg border border-orbit-border/40">
                <span className="text-[10px] font-mono text-orbit-muted uppercase block">Official Attribution</span>
                <span className="text-orbit-text text-[11px] block mt-0.5">{ds.attribution}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
