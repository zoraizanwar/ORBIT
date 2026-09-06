import React, { useState } from 'react';
import { MOCK_FUTURE_PREDICTIONS } from '../mock/demoData';
import { PredictionCard } from '../components/intelligence/PredictionCard';
import { Sliders, Sparkles } from 'lucide-react';

export const Predictions: React.FC = () => {
  const [selectedScenario, setSelectedScenario] = useState<string>('ALL');

  const filtered =
    selectedScenario === 'ALL'
      ? MOCK_FUTURE_PREDICTIONS
      : MOCK_FUTURE_PREDICTIONS.filter((p) => p.scenario === selectedScenario);

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full font-sans" data-testid="predictions-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-orbit-border/60 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold tracking-widest text-purple-400 bg-purple-950/60 px-2.5 py-1 rounded border border-purple-800 uppercase">
              FUTURE SIMULATION & SCENARIOS
            </span>
          </div>
          <h1 className="text-xl font-bold text-orbit-text mt-1">
            Future Forecasting & Prediction Engine
          </h1>
          <p className="text-xs text-orbit-muted mt-0.5 max-w-2xl leading-relaxed">
            Using 40 years of past satellite history (1984–2024) to estimate how monitored forests, water levels, and roads may change through 2030.
          </p>
        </div>

        {/* Scenario Filter Controls */}
        <div className="flex items-center gap-2 bg-orbit-carbon border border-orbit-border rounded-lg p-1.5 font-mono text-xs">
          <Sliders className="w-3.5 h-3.5 text-orbit-muted ml-2 mr-1" />
          <span className="text-orbit-muted text-[11px] font-bold">SCENARIO:</span>
          {[
            { key: 'ALL', label: 'All Scenarios' },
            { key: 'BUSINESS_AS_USUAL', label: 'Normal Trend' },
            { key: 'ACCELERATED_INFRASTRUCTURE', label: 'Faster Road Building' },
          ].map((sc) => (
            <button
              key={sc.key}
              onClick={() => setSelectedScenario(sc.key)}
              className={`px-3 py-1.5 rounded-md transition text-xs cursor-pointer ${
                selectedScenario === sc.key
                  ? 'bg-purple-600 text-white font-bold shadow-sm'
                  : 'text-orbit-muted hover:text-orbit-text'
              }`}
            >
              {sc.label}
            </button>
          ))}
        </div>
      </div>

      {/* Principle Banner */}
      <div className="p-4 bg-purple-950/20 border border-purple-500/30 rounded-xl flex items-start gap-3 shadow-sm">
        <Sparkles className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
        <div className="space-y-1 text-xs text-orbit-muted leading-relaxed">
          <h3 className="font-bold text-purple-300">
            How does ORBIT calculate future predictions?
          </h3>
          <p>
            ORBIT trains statistical models on 40 years of past satellite measurements to predict future deforestation and water changes. Every projection includes an <strong>uncertainty range (95% Confidence Interval)</strong> so you can see both best-case and worst-case possibilities.
          </p>
        </div>
      </div>

      {/* Grid of Prediction Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filtered.map((pred) => (
          <PredictionCard key={pred.id} prediction={pred} />
        ))}
      </div>
    </div>
  );
};
