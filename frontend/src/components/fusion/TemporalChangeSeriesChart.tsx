import React from 'react';
import {
  Activity,
} from 'lucide-react';

export interface SeriesDataPoint {
  timestamp: string;
  value: number;
  epistemic_level: 'CALCULATED' | 'PREDICTED';
}

interface Props {
  metricName: string;
  points: SeriesDataPoint[];
  state: string;
  netDelta: number;
}

export const TemporalChangeSeriesChart: React.FC<Props> = ({
  metricName,
  points,
  state,
  netDelta,
}) => {
  const calculatedPoints = points.filter((p) => p.epistemic_level === 'CALCULATED');
  const predictedPoints = points.filter((p) => p.epistemic_level === 'PREDICTED');

  return (
    <div
      className="p-3 bg-orbit-carbon/95 border border-orbit-border rounded-xl font-mono text-xs select-none space-y-2.5 shadow-xl"
      data-testid="temporal-change-series-chart"
    >
      <div className="flex items-center justify-between pb-1.5 border-b border-orbit-border">
        <div className="flex items-center gap-1.5 text-orbit-emerald font-bold text-[11px]">
          <Activity className="w-3.5 h-3.5" />
          <span>MULTI-TEMPORAL TRAJECTORY: {metricName}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[9px] px-1.5 py-0.5 rounded bg-orbit-slate text-orbit-text border border-orbit-border font-bold">
            {state}
          </span>
          <span className="text-[9px] px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/40 font-bold">
            Δ {netDelta > 0 ? `+${netDelta.toFixed(3)}` : netDelta.toFixed(3)}
          </span>
        </div>
      </div>

      {/* Discrete Epoch Trajectory Representation */}
      <div className="space-y-1.5 pt-1">
        <div className="text-[9px] text-orbit-muted flex items-center justify-between">
          <span className="text-orbit-emerald font-bold">● CALCULATED (Historical Ground Truth)</span>
          <span className="text-cyan-400 font-bold">○ PREDICTED (Statistical Projection)</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
          {points.map((pt, idx) => {
            const isCalc = pt.epistemic_level === 'CALCULATED';

            return (
              <div
                key={idx}
                className={`p-2 rounded-lg border flex flex-col justify-between ${
                  isCalc
                    ? 'bg-orbit-slate/40 border-orbit-emerald/40 text-orbit-text'
                    : 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300'
                }`}
              >
                <div className="text-[9px] text-orbit-muted flex items-center justify-between">
                  <span>Epoch {idx + 1}</span>
                  <span className="font-bold text-[8px]">{pt.epistemic_level}</span>
                </div>
                <div className="text-sm font-bold my-1">{pt.value.toFixed(3)}</div>
                <div className="text-[9px] text-orbit-muted truncate">
                  {pt.timestamp.split('T')[0]}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="text-[9px] text-orbit-muted pt-1 border-t border-orbit-border flex items-center justify-between">
        <span>Inviolable Isolation:</span>
        <span className="text-orbit-text">Historical {calculatedPoints.length} | Future Forecast {predictedPoints.length}</span>
      </div>
    </div>
  );
};
