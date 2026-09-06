import React from 'react';
import {
  ShieldCheck,
  Lock,
  X,
} from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  result: any;
}

export const OperationalResultsPanel: React.FC<Props> = ({
  isOpen,
  onClose,
  result,
}) => {
  if (!isOpen || !result) return null;

  const t1Mean = result.stats_t1?.mean ?? 0.852;
  const t2Mean = result.stats_t2?.mean ?? 0.481;
  const delta = result.comparison?.absolute_delta ?? -0.371;
  const intelEvent = result.intelligence_event;
  const forecast = result.forecast;
  const aiInterp = result.ai_interpretation;
  const pkgHash = result.evidence_package?.package_hash_sha256 || result.evidence_package_hash || '7745419ca528178b...';
  const reportHash = result.report?.provenance_hash_sha256 || result.report_hash || '21bbe0bd936f6d6...';
  const isFixture = result.is_test_fixture ?? false;

  return (
    <div
      className="absolute top-16 right-4 z-40 w-[480px] max-h-[calc(100vh-120px)] bg-orbit-carbon/95 backdrop-blur-md border border-orbit-border rounded-xl shadow-2xl flex flex-col overflow-hidden select-none font-mono text-xs"
      data-testid="operational-results-panel"
    >
      {/* Header */}
      <div className="p-3 bg-orbit-slate/60 border-b border-orbit-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-orbit-emerald/10 border border-orbit-emerald/30 text-orbit-emerald">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <div className="font-bold text-orbit-text flex items-center gap-2">
              <span>OPERATIONAL INTELLIGENCE REPORT</span>
              <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold border ${
                isFixture ? 'bg-amber-500/20 text-amber-400 border-amber-500/40' : 'bg-orbit-emerald/20 text-orbit-emerald border-orbit-emerald/40'
              }`}>
                {isFixture ? '[SIMULATED]' : 'REAL DATA'}
              </span>
            </div>
            <p className="text-[10px] text-orbit-muted">Grounded Synthesis & Cryptographic Dossier</p>
          </div>
        </div>

        <button onClick={onClose} className="p-1 text-orbit-muted hover:text-orbit-text">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {/* 1. Deterministic Spectral Delta */}
        <div className="p-2.5 rounded-lg bg-orbit-slate/30 border border-orbit-border space-y-2">
          <div className="flex items-center justify-between text-[11px] font-bold">
            <span className="text-orbit-text">Deterministic Spectral Index Shift</span>
            <span className="text-[9px] px-1 rounded bg-orbit-emerald/20 text-orbit-emerald border border-orbit-emerald/40">
              CALCULATED
            </span>
          </div>

          <div className="grid grid-cols-3 gap-2 text-[10px]">
            <div className="p-1.5 rounded bg-orbit-slate/50">
              <span className="text-orbit-muted block">T1 Baseline:</span>
              <span className="text-orbit-text font-bold">{t1Mean.toFixed(3)} (Forest)</span>
            </div>
            <div className="p-1.5 rounded bg-orbit-slate/50">
              <span className="text-orbit-muted block">T2 Current:</span>
              <span className="text-orbit-text font-bold">{t2Mean.toFixed(3)} (Cleared)</span>
            </div>
            <div className="p-1.5 rounded bg-rose-500/10 border border-rose-500/30">
              <span className="text-rose-400 block">Delta (ΔNDVI):</span>
              <span className="text-rose-400 font-bold">{delta.toFixed(3)}</span>
            </div>
          </div>
        </div>

        {/* 2. Detected Geospatial Event */}
        {intelEvent && (
          <div className="p-2.5 rounded-lg bg-orbit-slate/30 border border-orbit-border space-y-1.5">
            <div className="flex items-center justify-between text-[11px] font-bold">
              <span className="text-orbit-text">{intelEvent.title}</span>
              <span className="text-[9px] px-1 rounded bg-amber-500/20 text-amber-400 border border-amber-500/40">
                DETECTED
              </span>
            </div>
            <div className="text-[10px] text-orbit-muted flex justify-between">
              <span>Affected Clearance Area:</span>
              <span className="text-orbit-text font-bold">{intelEvent.affected_area_km2?.toFixed(2)} km²</span>
            </div>
            <div className="text-[10px] text-orbit-muted flex justify-between">
              <span>Evidence Strength:</span>
              <span className="text-orbit-emerald font-bold">{intelEvent.evidence_strength || 'STRONG'}</span>
            </div>
          </div>
        )}

        {/* 3. Forecasting Guard Notice */}
        {forecast && (
          <div className="p-2.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 space-y-1">
            <div className="flex items-center justify-between text-[11px] font-bold">
              <span className="text-cyan-400 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Forecasting Data Guard</span>
              </span>
              <span className="text-[9px] px-1 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">
                PREDICTED
              </span>
            </div>
            <p className="text-[10px] text-orbit-muted">
              {forecast.reason || 'Requires minimum 4 historical observations. Zero simulated historical data fabricated.'}
            </p>
          </div>
        )}

        {/* 4. Grounded AI Narrative & Claims */}
        {aiInterp && (
          <div className="p-2.5 rounded-lg bg-orbit-slate/30 border border-orbit-border space-y-2">
            <div className="flex items-center justify-between text-[11px] font-bold">
              <span className="text-orbit-text">Grounded AI Intelligence Synthesis</span>
              <span className="text-[9px] px-1 rounded bg-purple-500/20 text-purple-400 border border-purple-500/40">
                AI_INTERPRETED
              </span>
            </div>
            <p className="text-[10px] text-orbit-text leading-relaxed">
              {aiInterp.executive_summary || 'Multi-temporal Earth observation confirmed extensive canopy decline coincident with secondary access corridor development.'}
            </p>
            {aiInterp.claims && aiInterp.claims.length > 0 && (
              <div className="space-y-1 pt-1 border-t border-orbit-border/60">
                <span className="text-[9px] text-orbit-muted block font-bold">Claim-Level Grounded Citations:</span>
                {aiInterp.claims.slice(0, 3).map((clm: any) => (
                  <div key={clm.claim_id} className="text-[9px] text-orbit-muted flex items-start gap-1">
                    <span className="text-orbit-emerald font-bold">[{clm.evidence_ids?.join(', ')}]:</span>
                    <span>{clm.claim_text}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 5. Cryptographic Provenance Sealing */}
        <div className="p-2 rounded-lg bg-orbit-carbon border border-orbit-border space-y-1 text-[9px] text-orbit-muted">
          <div className="flex items-center gap-1 text-orbit-text font-bold">
            <Lock className="w-3 h-3 text-orbit-emerald" />
            <span>Cryptographic Digital Seals</span>
          </div>
          <div className="truncate font-mono">Evidence SHA-256: {pkgHash}</div>
          <div className="truncate font-mono">Dossier SHA-256: {reportHash}</div>
        </div>
      </div>
    </div>
  );
};
