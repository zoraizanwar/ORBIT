import React from 'react';
import {
  ArrowRight,
  AlertTriangle,
  Clock,
  X,
} from 'lucide-react';
import { NormalizedImageryScene } from '../../types/earthObservation';

interface Props {
  t1Scene: NormalizedImageryScene | null;
  t2Scene: NormalizedImageryScene | null;
  onClearT1: () => void;
  onClearT2: () => void;
  onProceedToExecution: () => void;
}

export const ObservationPairSelector: React.FC<Props> = ({
  t1Scene,
  t2Scene,
  onClearT1,
  onClearT2,
  onProceedToExecution,
}) => {
  if (!t1Scene && !t2Scene) return null;

  // Validate chronological ordering (T1 < T2)
  let isValidOrder = true;
  let intervalDays = 0;

  if (t1Scene && t2Scene) {
    const t1Date = new Date(t1Scene.acquisition_datetime).getTime();
    const t2Date = new Date(t2Scene.acquisition_datetime).getTime();
    isValidOrder = t1Date < t2Date;
    intervalDays = Math.round((t2Date - t1Date) / (1000 * 60 * 60 * 24));
  }

  const isReady = t1Scene && t2Scene && isValidOrder;

  return (
    <div
      className="absolute bottom-4 left-4 z-20 w-[480px] bg-orbit-carbon/95 backdrop-blur-md border border-orbit-border rounded-xl shadow-2xl p-3 select-none font-mono text-xs space-y-2.5"
      data-testid="observation-pair-selector"
    >
      <div className="flex items-center justify-between pb-1.5 border-b border-orbit-border">
        <div className="flex items-center gap-1.5 text-orbit-emerald font-bold text-[11px]">
          <Clock className="w-3.5 h-3.5" />
          <span>MULTI-TEMPORAL OBSERVATION PAIR</span>
        </div>
        <span className="text-[9px] px-1.5 py-0.5 rounded bg-orbit-slate text-orbit-muted border border-orbit-border">
          {isReady ? `${intervalDays} Days Interval` : 'Awaiting Pair'}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {/* T1 Card */}
        <div className="p-2 rounded-lg bg-orbit-slate/30 border border-orbit-border space-y-1 relative">
          <div className="flex items-center justify-between text-[10px]">
            <span className="font-bold text-orbit-emerald">T1 (Baseline)</span>
            {t1Scene && (
              <button onClick={onClearT1} className="text-orbit-muted hover:text-rose-400">
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
          {t1Scene ? (
            <div className="text-[9px] text-orbit-text space-y-0.5">
              <div className="font-bold truncate">{t1Scene.platform} ({t1Scene.sensor})</div>
              <div className="text-orbit-muted">{t1Scene.acquisition_datetime.split('T')[0]}</div>
              <div className="text-orbit-muted">Cloud: {t1Scene.cloud_cover ?? 0}%</div>
            </div>
          ) : (
            <div className="text-[9px] text-orbit-muted italic py-2">Select baseline scene...</div>
          )}
        </div>

        {/* T2 Card */}
        <div className="p-2 rounded-lg bg-orbit-slate/30 border border-orbit-border space-y-1 relative">
          <div className="flex items-center justify-between text-[10px]">
            <span className="font-bold text-orbit-cyan">T2 (Comparison)</span>
            {t2Scene && (
              <button onClick={onClearT2} className="text-orbit-muted hover:text-rose-400">
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
          {t2Scene ? (
            <div className="text-[9px] text-orbit-text space-y-0.5">
              <div className="font-bold truncate">{t2Scene.platform} ({t2Scene.sensor})</div>
              <div className="text-orbit-muted">{t2Scene.acquisition_datetime.split('T')[0]}</div>
              <div className="text-orbit-muted">Cloud: {t2Scene.cloud_cover ?? 0}%</div>
            </div>
          ) : (
            <div className="text-[9px] text-orbit-muted italic py-2">Select current scene...</div>
          )}
        </div>
      </div>

      {/* Validation Message */}
      {!isValidOrder && (
        <div className="p-1.5 rounded bg-rose-500/10 border border-rose-500/30 text-rose-400 text-[10px] flex items-center gap-1.5">
          <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
          <span>Chronological Error: T1 must strictly precede T2 in time.</span>
        </div>
      )}

      {/* Execution Trigger */}
      <button
        onClick={onProceedToExecution}
        disabled={!isReady}
        className="w-full py-2 bg-orbit-emerald/20 hover:bg-orbit-emerald/30 border border-orbit-emerald/50 text-orbit-emerald rounded-lg font-bold text-[11px] flex items-center justify-center gap-1.5 transition disabled:opacity-40"
      >
        <span>Initialize 8-Tier Analytical Pipeline</span>
        <ArrowRight className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};
