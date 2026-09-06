import React from 'react';
import {
  Scale,
} from 'lucide-react';

interface Props {
  score: number;
  qualityScore: number;
  observationCountScore: number;
  temporalScore: number;
  spatialScore: number;
  corroborationScore: number;
  contradictionPenalty: number;
}

export const EvidenceFusionScoreCard: React.FC<Props> = ({
  score,
  qualityScore,
  observationCountScore,
  temporalScore,
  spatialScore,
  corroborationScore,
  contradictionPenalty,
}) => {
  return (
    <div
      className="p-3 bg-orbit-carbon/95 border border-orbit-border rounded-xl font-mono text-xs select-none space-y-2.5 shadow-xl"
      data-testid="evidence-fusion-score-card"
    >
      <div className="flex items-center justify-between pb-1.5 border-b border-orbit-border">
        <div className="flex items-center gap-1.5 text-orbit-emerald font-bold text-[11px]">
          <Scale className="w-3.5 h-3.5" />
          <span>DETERMINISTIC EVIDENCE STRENGTH</span>
        </div>
        <span className="text-[11px] font-bold text-orbit-emerald px-2 py-0.5 rounded bg-orbit-emerald/10 border border-orbit-emerald/40">
          {(score * 100).toFixed(1)} / 100
        </span>
      </div>

      <div className="space-y-1.5 text-[10px]">
        <div className="flex justify-between text-orbit-muted">
          <span>Observation Quality (Q):</span>
          <span className="text-orbit-text font-bold">{(qualityScore * 100).toFixed(0)}%</span>
        </div>
        <div className="flex justify-between text-orbit-muted">
          <span>Multi-Epoch Count (N):</span>
          <span className="text-orbit-text font-bold">{(observationCountScore * 100).toFixed(0)}%</span>
        </div>
        <div className="flex justify-between text-orbit-muted">
          <span>Temporal Consistency (T):</span>
          <span className="text-orbit-text font-bold">{(temporalScore * 100).toFixed(0)}%</span>
        </div>
        <div className="flex justify-between text-orbit-muted">
          <span>Spatial Overlap IoU (S):</span>
          <span className="text-orbit-text font-bold">{(spatialScore * 100).toFixed(0)}%</span>
        </div>
        <div className="flex justify-between text-orbit-muted">
          <span>Cross-Sensor Corroboration:</span>
          <span className="text-orbit-emerald font-bold">+{(corroborationScore * 100).toFixed(0)}%</span>
        </div>
        {contradictionPenalty > 0 && (
          <div className="flex justify-between text-rose-400">
            <span>Contradiction Penalty:</span>
            <span className="font-bold">-{(contradictionPenalty * 100).toFixed(0)}%</span>
          </div>
        )}
      </div>

      <div className="text-[9px] text-orbit-muted pt-1 border-t border-orbit-border">
        Classification: <strong className="text-orbit-text">Deterministic Multi-Criteria Metric</strong> (Not statistical probability).
      </div>
    </div>
  );
};
