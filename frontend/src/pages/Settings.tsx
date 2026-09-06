import React from 'react';
import { Globe, Shield, CheckCircle2 } from 'lucide-react';

export const Settings: React.FC = () => {
  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full font-sans" data-testid="settings-page">
      {/* Header */}
      <div className="border-b border-orbit-border/60 pb-4">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono font-bold tracking-widest text-orbit-emerald bg-emerald-950/60 px-2.5 py-1 rounded border border-orbit-emerald/40 uppercase">
            SYSTEM PREFERENCES
          </span>
        </div>
        <h1 className="text-xl font-bold text-orbit-text mt-1">
          Workstation & Map Settings
        </h1>
        <p className="text-xs text-orbit-muted mt-0.5 max-w-2xl leading-relaxed">
          Configure how the Earth map renders, geographic coordinates, and automatic anti-hallucination guardrails.
        </p>
      </div>

      <div className="space-y-6 max-w-3xl text-xs">
        {/* Section 1: Earth Map & Coordinates */}
        <div className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 space-y-4 shadow-sm">
          <div className="flex items-center gap-2 border-b border-orbit-border/60 pb-3">
            <Globe className="w-5 h-5 text-orbit-emerald" />
            <h2 className="text-sm font-bold text-orbit-text">Geographic & Map Preferences</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-orbit-muted font-bold block">World Coordinate Format</label>
              <div className="bg-orbit-slate/50 border border-orbit-border rounded-lg p-2.5 text-orbit-emerald font-mono font-bold">
                WGS84 (Standard Global GPS Latitude & Longitude)
              </div>
              <span className="text-[11px] text-orbit-muted/80 block">Standard coordinates used worldwide by GPS and satellites.</span>
            </div>

            <div className="space-y-1">
              <label className="text-orbit-muted font-bold block">Area Measurement Engine</label>
              <div className="bg-orbit-slate/50 border border-orbit-border rounded-lg p-2.5 text-orbit-sky font-mono font-bold">
                Exact Ellipsoidal Math (PostGIS Geodesic)
              </div>
              <span className="text-[11px] text-orbit-muted/80 block">Accounts for Earth curvature so hectare calculations are exact.</span>
            </div>
          </div>
        </div>

        {/* Section 2: Anti-Hallucination Guardrails */}
        <div className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 space-y-4 shadow-sm">
          <div className="flex items-center gap-2 border-b border-orbit-border/60 pb-3">
            <Shield className="w-5 h-5 text-orbit-emerald" />
            <h2 className="text-sm font-bold text-orbit-text">Anti-Hallucination & Truth Guardrails</h2>
          </div>

          <div className="space-y-3 text-orbit-text leading-relaxed">
            <div className="flex items-start gap-2.5 p-2.5 bg-orbit-slate/20 rounded-lg border border-orbit-border/40">
              <CheckCircle2 className="w-4 h-4 text-orbit-emerald shrink-0 mt-0.5" />
              <div>
                <strong className="block text-orbit-emerald">Strict Fact Verification (Zero AI Guesswork)</strong>
                <span className="text-orbit-muted text-[11px]">
                  AI summaries must quote exact satellite observation IDs and pixel measurements from the verified database.
                </span>
              </div>
            </div>

            <div className="flex items-start gap-2.5 p-2.5 bg-orbit-slate/20 rounded-lg border border-orbit-border/40">
              <CheckCircle2 className="w-4 h-4 text-orbit-emerald shrink-0 mt-0.5" />
              <div>
                <strong className="block text-orbit-emerald">Strict Separation of Past vs Future</strong>
                <span className="text-orbit-muted text-[11px]">
                  Future projections are always visually and mathematically separated from raw historical satellite observations.
                </span>
              </div>
            </div>

            <div className="flex items-start gap-2.5 p-2.5 bg-orbit-slate/20 rounded-lg border border-orbit-border/40">
              <CheckCircle2 className="w-4 h-4 text-orbit-emerald shrink-0 mt-0.5" />
              <div>
                <strong className="block text-orbit-emerald">Cryptographic SHA-256 Data Seals</strong>
                <span className="text-orbit-muted text-[11px]">
                  Every generated report carries an immutable digital seal verifying that telemetry was not modified.
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
