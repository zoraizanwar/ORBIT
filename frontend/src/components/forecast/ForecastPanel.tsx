import React, { useState } from 'react';
import {
  ForecastRunResult,
  ForecastScenarioType,
} from '../../types/forecasting';
import {
  DEMO_FORECAST_FIXTURE,
  DEMO_HISTORICAL_SERIES,
} from '../../services/forecastService';
import { ForecastChart } from './ForecastChart';
import { PredictionCard } from './PredictionCard';
import { BacktestDiagnosticsCard } from './BacktestDiagnosticsCard';
import { EpistemicBadge } from '../intelligence/EpistemicBadge';
import { EvidenceStrengthBadge } from '../intelligence/EvidenceStrengthBadge';

type ForecastTab =
  | 'OVERVIEW'
  | 'SERIES'
  | 'MODEL'
  | 'PROJECTIONS'
  | 'SCENARIOS'
  | 'BACKTEST'
  | 'PROVENANCE';

export const ForecastPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ForecastTab>('OVERVIEW');
  const [selectedScenario, setSelectedScenario] = useState<ForecastScenarioType>('BASELINE_TREND');
  const [forecastResult] = useState<ForecastRunResult>(DEMO_FORECAST_FIXTURE);

  return (
    <div className="flex flex-col h-full bg-gray-950 text-gray-100 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-800 flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-base font-bold text-white tracking-wide">
              Forecasting & Future Prediction Engine
            </h2>
            <EpistemicBadge level={forecastResult.epistemic_level} />
            <EvidenceStrengthBadge strength={forecastResult.evidence_strength} />
          </div>
          <p className="text-xs text-gray-400 mt-0.5">
            Calibrated baseline projections grounded in historical satellite measurements (2018–2026).
          </p>
        </div>

        {/* Scenario Switcher */}
        <div className="flex items-center space-x-2">
          <label className="text-xs text-gray-400">Scenario:</label>
          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value as ForecastScenarioType)}
            className="bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded px-2.5 py-1 focus:ring-1 focus:ring-purple-500 font-mono"
          >
            <option value="BASELINE_TREND">BASELINE TREND (Linear Extrapolation)</option>
            <option value="CONSERVATION_POLICY">CONSERVATION POLICY (Targeted Inundation/Reforestation)</option>
            <option value="SSP2-4.5_BUSINESS_AS_USUAL">SSP2-4.5 (Middle of the Road)</option>
          </select>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center space-x-1 px-4 border-b border-gray-800 bg-gray-900/40 text-xs">
        {(
          [
            { key: 'OVERVIEW', label: 'Overview' },
            { key: 'SERIES', label: 'Historical Series' },
            { key: 'MODEL', label: 'Model Diagnostics' },
            { key: 'PROJECTIONS', label: 'Future Projections' },
            { key: 'SCENARIOS', label: 'Scenarios' },
            { key: 'BACKTEST', label: 'Backtest' },
            { key: 'PROVENANCE', label: 'Lineage & Provenance' },
          ] as { key: ForecastTab; label: string }[]
        ).map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-3 py-2 font-medium border-b-2 transition-colors ${
              activeTab === tab.key
                ? 'border-purple-500 text-purple-300 font-bold bg-purple-950/20'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {activeTab === 'OVERVIEW' && (
          <div className="space-y-4">
            {/* Visual Trajectory Chart */}
            <ForecastChart
              historical={DEMO_HISTORICAL_SERIES}
              predictions={forecastResult.predictions}
              metric={forecastResult.metric}
            />

            {/* Quick Metrics & Summary */}
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3 bg-gray-900/70 border border-gray-800 rounded-lg">
                <div className="text-[11px] text-gray-400 uppercase">Training Window</div>
                <div className="text-sm font-bold text-white font-mono mt-1">
                  {forecastResult.training_start_year} – {forecastResult.training_end_year} ({forecastResult.training_observation_count} obs)
                </div>
              </div>
              <div className="p-3 bg-gray-900/70 border border-gray-800 rounded-lg">
                <div className="text-[11px] text-gray-400 uppercase">Projection Horizon</div>
                <div className="text-sm font-bold text-purple-300 font-mono mt-1">
                  2027 – {forecastResult.predictions[forecastResult.predictions.length - 1].target_year} ({forecastResult.forecast_horizon_years} years)
                </div>
              </div>
              <div className="p-3 bg-gray-900/70 border border-gray-800 rounded-lg">
                <div className="text-[11px] text-gray-400 uppercase">Backtest Fit (R²)</div>
                <div className="text-sm font-bold text-emerald-400 font-mono mt-1">
                  {forecastResult.backtest.overall_metrics?.r_squared.toFixed(3) ?? 'N/A'}
                </div>
              </div>
            </div>

            {/* Backtest Diagnostics */}
            <BacktestDiagnosticsCard backtest={forecastResult.backtest} />
          </div>
        )}

        {activeTab === 'SERIES' && (
          <div className="space-y-3">
            <div className="text-xs font-bold text-gray-400 uppercase tracking-wider">
              Calibrated Historical Measurements ({DEMO_HISTORICAL_SERIES.length} observations)
            </div>
            <div className="divide-y divide-gray-800/60 bg-gray-900/60 rounded-lg border border-gray-800">
              {DEMO_HISTORICAL_SERIES.map((obs) => (
                <div key={obs.id} className="p-2.5 flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center space-x-2">
                    <span className="text-cyan-400 font-bold">
                      {new Date(obs.acquisition_datetime).getFullYear()}
                    </span>
                    <span className="text-gray-400">{obs.sensor}</span>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="text-gray-200">NDVI: {obs.value.toFixed(2)}</span>
                    <EpistemicBadge level={obs.epistemic_level ?? 'CALCULATED'} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'MODEL' && (
          <div className="space-y-3">
            <div className="text-xs font-bold text-gray-400 uppercase tracking-wider">
              Forecasting Model Calibration & Parameters
            </div>
            <div className="p-4 bg-gray-900/80 border border-gray-800 rounded-lg space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-gray-800 pb-2">
                <span className="text-gray-400">Model Name:</span>
                <span className="text-white font-bold">{forecastResult.model_name}</span>
              </div>
              <div className="flex items-center justify-between border-b border-gray-800 pb-2">
                <span className="text-gray-400">Model Version:</span>
                <span className="text-white font-bold">{forecastResult.model_version}</span>
              </div>
              <div className="flex items-center justify-between border-b border-gray-800 pb-2">
                <span className="text-gray-400">Equation:</span>
                <span className="text-purple-300 font-bold">y(t) = β₀ + β₁·t (Ordinary Least Squares)</span>
              </div>
              <div className="flex items-center justify-between border-b border-gray-800 pb-2">
                <span className="text-gray-400">Residual Standard Error:</span>
                <span className="text-cyan-400">0.0078</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Security / Execution Mode:</span>
                <span className="text-emerald-400">Deterministic Pure-Statistical Baseline</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'PROJECTIONS' && (
          <div className="space-y-3">
            <div className="text-xs font-bold text-purple-400 uppercase tracking-wider">
              Point Projections & 95% Confidence Intervals [Epistemic: PREDICTED]
            </div>
            <div className="grid grid-cols-2 gap-3">
              {forecastResult.predictions.map((p) => (
                <PredictionCard
                  key={p.target_year}
                  prediction={p}
                  metric={forecastResult.metric}
                  modelName={forecastResult.model_name}
                  modelVersion={forecastResult.model_version}
                  scenario={forecastResult.scenario}
                />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'SCENARIOS' && (
          <div className="space-y-3">
            <div className="text-xs font-bold text-gray-400 uppercase tracking-wider">
              Future Prediction Scenarios & Assumptions
            </div>
            <div className="grid grid-cols-1 gap-3">
              <div className="p-3 bg-gray-900/70 border border-gray-800 rounded-lg space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-white">BASELINE TREND (Current Policy)</span>
                  <span className="text-xs px-2 py-0.5 rounded bg-blue-950 text-blue-400 font-mono">ACTIVE</span>
                </div>
                <p className="text-xs text-gray-400">
                  Unmodified continuation of historical deforestation, urban expansion, and climatic shifts observed over 2018–2026.
                </p>
              </div>
              <div className="p-3 bg-gray-900/70 border border-gray-800 rounded-lg space-y-1.5 opacity-80">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-white">CONSERVATION POLICY</span>
                  <span className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">SIMULATED</span>
                </div>
                <p className="text-xs text-gray-400">
                  Assumes strict boundary enforcement along protected highway corridors and riparian buffer reforestation (+0.02 index boost).
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'BACKTEST' && (
          <BacktestDiagnosticsCard backtest={forecastResult.backtest} />
        )}

        {activeTab === 'PROVENANCE' && (
          <div className="space-y-3 font-mono text-xs">
            <div className="text-xs font-bold text-gray-400 uppercase tracking-wider font-sans">
              Cryptographic Lineage & Calculation Fingerprint
            </div>
            <div className="p-4 bg-gray-900/80 border border-gray-800 rounded-lg space-y-2">
              <div>
                <span className="text-gray-500">SHA-256 Fingerprint: </span>
                <span className="text-purple-400 break-all">
                  {forecastResult.provenance.provenance_hash_sha256}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Deterministic Pipeline: </span>
                <span className="text-emerald-400 font-bold">TRUE</span>
              </div>
              <div>
                <span className="text-gray-500">AI Interpretation: </span>
                <span className="text-gray-300">NOT INVOKED (Pure Statistical)</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
