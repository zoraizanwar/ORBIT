import React from 'react';
import { ForecastPredictionPoint, ForecastScenarioType } from '../../types/forecasting';
import { EpistemicBadge } from '../intelligence/EpistemicBadge';

interface PredictionCardProps {
  prediction: ForecastPredictionPoint;
  metric: string;
  modelName: string;
  modelVersion: string;
  scenario: ForecastScenarioType;
}

export const PredictionCard: React.FC<PredictionCardProps> = ({
  prediction,
  metric,
  modelName,
  modelVersion,
  scenario,
}) => {
  return (
    <div className="p-3 bg-gray-900/80 border border-purple-900/40 rounded-lg space-y-2 hover:border-purple-600/60 transition-all">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-bold text-purple-300">
            {metric} Forecast ({prediction.target_year})
          </span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-950/80 text-purple-400 font-mono border border-purple-800/50">
            {scenario}
          </span>
        </div>
        <EpistemicBadge level={prediction.epistemic_level} />
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs pt-1">
        <div>
          <span className="text-gray-500">Predicted Value: </span>
          <span className="font-bold text-white font-mono">{prediction.predicted_value.toFixed(3)}</span>
        </div>
        <div>
          <span className="text-gray-500">95% Confidence: </span>
          <span className="font-mono text-purple-400">
            {prediction.lower_bound !== null && prediction.upper_bound !== null
              ? `[${prediction.lower_bound.toFixed(3)} – ${prediction.upper_bound.toFixed(3)}]`
              : 'N/A'}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between text-[11px] text-gray-500 pt-1 border-t border-gray-800/80">
        <div>
          Model: <span className="text-gray-400 font-mono">{modelName} ({modelVersion})</span>
        </div>
        <div>
          Target: <span className="text-gray-400 font-mono">{prediction.target_year}</span>
        </div>
      </div>
    </div>
  );
};
