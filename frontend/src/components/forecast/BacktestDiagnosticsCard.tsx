import React from 'react';
import { BacktestReport } from '../../types/forecasting';

interface BacktestDiagnosticsCardProps {
  backtest: BacktestReport;
}

export const BacktestDiagnosticsCard: React.FC<BacktestDiagnosticsCardProps> = ({ backtest }) => {
  if (backtest.status === 'INSUFFICIENT_DATA' || !backtest.overall_metrics) {
    return (
      <div className="p-3 bg-gray-900/60 border border-gray-800 rounded-lg text-xs text-gray-400">
        <span className="font-bold text-yellow-400">Backtest Status: INSUFFICIENT DATA</span>
        <p className="text-[11px] text-gray-500 mt-1">
          Historical backtesting requires at least 4 consecutive calibrated observations.
        </p>
      </div>
    );
  }

  const { mae, rmse, r_squared, sample_size } = backtest.overall_metrics;

  return (
    <div className="p-3 bg-gray-900/80 border border-gray-800 rounded-lg space-y-3">
      <div className="flex items-center justify-between">
        <div className="text-xs font-bold text-gray-200">
          Historical Backtest Performance (Out-of-Sample Holdouts)
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono border border-emerald-800/60">
          VALIDATED ({sample_size} splits)
        </span>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="p-2 bg-gray-950 rounded border border-gray-800">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider">Mean Absolute Error</div>
          <div className="text-sm font-bold text-cyan-400 font-mono mt-0.5">{mae.toFixed(4)}</div>
        </div>
        <div className="p-2 bg-gray-950 rounded border border-gray-800">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider">Root Mean Sq Error</div>
          <div className="text-sm font-bold text-cyan-400 font-mono mt-0.5">{rmse.toFixed(4)}</div>
        </div>
        <div className="p-2 bg-gray-950 rounded border border-gray-800">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider">Coefficient of Det (R²)</div>
          <div className="text-sm font-bold text-emerald-400 font-mono mt-0.5">{r_squared.toFixed(3)}</div>
        </div>
      </div>

      {/* Temporal Splits Breakdown */}
      <div className="space-y-1 pt-1">
        <div className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">
          Expanding-Window Holdout Splits
        </div>
        <div className="max-h-32 overflow-y-auto space-y-1 text-xs">
          {backtest.splits.map((split) => (
            <div
              key={split.val_year}
              className="flex items-center justify-between p-1.5 bg-gray-950/60 rounded border border-gray-800/60 font-mono text-[11px]"
            >
              <span className="text-gray-400">
                Train: {split.train_start_year}–{split.train_end_year} → Val: {split.val_year}
              </span>
              <div className="flex items-center space-x-3">
                <span className="text-gray-300">Act: {split.actual_value.toFixed(2)}</span>
                <span className="text-purple-400">Pred: {split.predicted_value.toFixed(2)}</span>
                <span className="text-cyan-400">Err: {split.error > 0 ? `+${split.error.toFixed(3)}` : split.error.toFixed(3)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
