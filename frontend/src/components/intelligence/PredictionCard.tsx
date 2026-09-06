import React from 'react';
import { FuturePrediction } from '../../types';
import { EvidenceStrengthBadge } from './EvidenceStrengthBadge';
import { TrendingUp, AlertTriangle, Calendar, Cpu } from 'lucide-react';

interface Props {
  prediction: FuturePrediction;
}

export const PredictionCard: React.FC<Props> = ({ prediction }) => {
  return (
    <div
      className="bg-orbit-carbon border border-purple-500/30 rounded-xl p-5 shadow-lg relative overflow-hidden group hover:border-purple-500/60 transition"
      data-testid={`prediction-card-${prediction.id}`}
    >
      {/* Top Banner Tag declaring this is a Simulation/Projection */}
      <div className="flex items-center justify-between gap-2 pb-3 border-b border-orbit-border/60">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-purple-500/10 rounded-md border border-purple-500/30">
            <TrendingUp className="w-4 h-4 text-purple-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold tracking-widest text-purple-400 uppercase bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/30">
                SCIENTIFIC PROJECTION • NOT AN OBSERVATION
              </span>
            </div>
            <h4 className="text-sm font-semibold text-orbit-text mt-0.5">
              {prediction.prediction_type.replace(/_/g, ' ')}
            </h4>
          </div>
        </div>
        <div className="text-right">
          <span className="text-xs font-mono font-bold text-purple-300 bg-purple-950/60 px-2.5 py-1 rounded border border-purple-800">
            TARGET: {prediction.target_year}
          </span>
        </div>
      </div>

      {/* Main Forecast Metric Value */}
      <div className="my-4 bg-orbit-slate/40 p-4 rounded-lg border border-orbit-border/40 flex items-center justify-between">
        <div>
          <div className="text-xs font-mono text-orbit-muted uppercase tracking-wider">
            Model-Based Projected Value
          </div>
          <div className="text-2xl font-bold font-mono text-purple-300 mt-1 flex items-baseline gap-2">
            <span>{prediction.prediction_value > 0 ? `+${prediction.prediction_value}` : prediction.prediction_value}</span>
            <span className="text-sm font-normal text-orbit-muted">{prediction.unit}</span>
          </div>
          {prediction.lower_bound !== undefined && prediction.upper_bound !== undefined && (
            <div className="text-xs font-mono text-orbit-muted mt-1">
              95% Confidence Bounds: [{prediction.lower_bound} to {prediction.upper_bound} {prediction.unit}]
            </div>
          )}
        </div>
        <div className="text-right space-y-1.5">
          <div className="text-xs text-orbit-muted font-mono">Scenario: <span className="text-orbit-text font-medium">{prediction.scenario}</span></div>
          <div className="text-xs text-orbit-muted font-mono">Model Confidence: <span className="text-orbit-sky font-semibold">{(prediction.confidence * 100).toFixed(0)}%</span></div>
        </div>
      </div>

      {/* Metadata Badges & Lineage */}
      <div className="grid grid-cols-2 gap-2 text-xs font-mono text-orbit-muted mb-3">
        <div className="flex items-center gap-1.5 bg-orbit-slate/20 p-2 rounded border border-orbit-border/30">
          <Cpu className="w-3.5 h-3.5 text-purple-400 shrink-0" />
          <span className="truncate">Model: {prediction.model_name} ({prediction.model_version})</span>
        </div>
        <div className="flex items-center gap-1.5 bg-orbit-slate/20 p-2 rounded border border-orbit-border/30">
          <Calendar className="w-3.5 h-3.5 text-orbit-cyan shrink-0" />
          <span>Baseline: {prediction.training_start_year}–{prediction.training_end_year}</span>
        </div>
      </div>

      {/* Evidence Strength rating */}
      <div className="flex items-center justify-between pt-3 border-t border-orbit-border/40">
        <div className="text-xs text-orbit-muted">Underlying Baseline Data Quality:</div>
        <EvidenceStrengthBadge strength={prediction.evidence_strength} size="sm" />
      </div>

      {/* Scientific Limitation Disclaimer */}
      <div className="mt-3 p-2.5 bg-amber-500/5 border border-amber-500/20 rounded-md text-[11px] text-amber-200/80 flex items-start gap-2">
        <AlertTriangle className="w-4 h-4 text-orbit-warning shrink-0 mt-0.5" />
        <p>
          <strong>Scientific Notice:</strong> Projections represent conditional scenario estimates based on historical baseline trends. Unforeseen policy changes, climate tipping points, or extreme events can alter outcomes.
        </p>
      </div>
    </div>
  );
};
