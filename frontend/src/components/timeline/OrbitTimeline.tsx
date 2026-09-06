import React, { useState } from 'react';
import { Clock, Play, Pause, ChevronLeft, ChevronRight, TrendingUp } from 'lucide-react';

interface Props {
  selectedYear: number;
  onYearChange: (year: number) => void;
}

export const OrbitTimeline: React.FC<Props> = ({ selectedYear, onYearChange }) => {
  const [isPlaying, setIsPlaying] = useState(false);

  // Key landmark years in Earth Observation history
  const historicalKeyYears = [
    { year: 1972, label: 'Landsat-1', type: 'historical', support: 'ESTIMATED' },
    { year: 1984, label: 'Landsat-5 TM', type: 'historical', support: 'PARTIALLY_SUPPORTED' },
    { year: 1999, label: 'Landsat-7 ETM+', type: 'historical', support: 'PARTIALLY_SUPPORTED' },
    { year: 2014, label: 'Sentinel-1A (SAR)', type: 'historical', support: 'STRONGLY_SUPPORTED' },
    { year: 2015, label: 'Sentinel-2A (MSI)', type: 'historical', support: 'STRONGLY_SUPPORTED' },
    { year: 2020, label: 'Full Constellation', type: 'historical', support: 'STRONGLY_SUPPORTED' },
    { year: 2024, label: 'Copernicus V2', type: 'historical', support: 'STRONGLY_SUPPORTED' },
    { year: 2026, label: 'PRESENT OBS.', type: 'current', support: 'STRONGLY_SUPPORTED' },
  ];

  const forecastKeyYears = [
    { year: 2030, label: 'SDG Horizon', type: 'forecast' },
    { year: 2035, label: 'Urban Trend', type: 'forecast' },
    { year: 2040, label: 'Canopy Model', type: 'forecast' },
    { year: 2050, label: 'Century Midpoint', type: 'forecast' },
  ];

  const isFuture = selectedYear > 2026;

  return (
    <div
      className="bg-orbit-carbon border-t border-orbit-border px-6 py-4 relative select-none"
      data-testid="orbit-timeline"
    >
      {/* Upper Timeline Control Header */}
      <div className="flex items-center justify-between gap-4 mb-3">
        {/* Left: Playback Controls & Selected Epoch */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-2 rounded-lg bg-orbit-slate hover:bg-orbit-border text-orbit-text transition flex items-center gap-1.5 text-xs font-mono border border-orbit-border"
            title={isPlaying ? 'Pause timeline playback' : 'Play timeline animation'}
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5 text-orbit-emerald" /> : <Play className="w-3.5 h-3.5 text-orbit-text" />}
            <span>{isPlaying ? 'PAUSE' : 'PLAY'}</span>
          </button>

          <div className="flex items-center gap-1 text-orbit-muted">
            <button
              onClick={() => onYearChange(Math.max(1972, selectedYear - 1))}
              className="p-1 rounded hover:bg-orbit-slate text-orbit-text transition"
              title="Previous Year"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => onYearChange(Math.min(2050, selectedYear + 1))}
              className="p-1 rounded hover:bg-orbit-slate text-orbit-text transition"
              title="Next Year"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <div className="flex items-center gap-2 font-mono">
            <span className="text-xs text-orbit-muted uppercase">SELECTED EPOCH:</span>
            <span className={`text-lg font-bold px-2 py-0.5 rounded border ${
              isFuture
                ? 'text-purple-300 bg-purple-950/40 border-purple-800'
                : 'text-orbit-emerald bg-emerald-950/40 border-orbit-emerald/40'
            }`}>
              {selectedYear}
            </span>
          </div>

          {/* Epistemic Demarcation Indicator */}
          {isFuture ? (
            <div className="flex items-center gap-1.5 text-xs font-mono text-purple-400 bg-purple-500/10 px-2.5 py-1 rounded border border-purple-500/30">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>FUTURE PROJECTION HORIZON (SIMULATED)</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-xs font-mono text-orbit-emerald bg-emerald-500/10 px-2.5 py-1 rounded border border-orbit-emerald/30">
              <Clock className="w-3.5 h-3.5" />
              <span>EMPIRICAL SATELLITE ARCHIVE (1972–PRESENT)</span>
            </div>
          )}
        </div>

        {/* Right: Legend explaining timeline visual rules */}
        <div className="hidden lg:flex items-center gap-4 text-[11px] font-mono text-orbit-muted">
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-orbit-emerald shadow-glow-emerald"></div>
            <span>Observed Satellite Data</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-orbit-sky"></div>
            <span>Multi-Sensor Co-registration</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-purple-400"></div>
            <span>Future Forecast Model</span>
          </div>
        </div>
      </div>

      {/* Scrubbable Multi-Decadal Slider Track */}
      <div className="relative pt-6 pb-2">
        {/* Visual Track split: 1972-2026 (Green/Sky Solid) vs 2026-2050 (Purple Dashed) */}
        <div className="absolute top-8 left-0 right-0 h-1.5 bg-orbit-slate rounded-full overflow-hidden flex">
          {/* 1972 to 2026 (70% of track) */}
          <div className="w-[70%] h-full bg-gradient-to-r from-orbit-sky/50 to-orbit-emerald rounded-l-full"></div>
          {/* 2026 to 2050 (30% of track) */}
          <div className="w-[30%] h-full bg-gradient-to-r from-purple-500/60 to-purple-400 border-l border-orbit-border border-dashed"></div>
        </div>

        {/* Native Interactive Range Input Overlay */}
        <input
          type="range"
          min="1972"
          max="2050"
          value={selectedYear}
          onChange={(e) => onYearChange(parseInt(e.target.value, 10))}
          className="w-full relative z-10 cursor-pointer accent-orbit-emerald opacity-90 h-6 -mt-3"
          aria-label="Orbit Temporal Epoch Selector"
        />

        {/* Key Landmark Markers along the timeline */}
        <div className="flex justify-between items-start mt-2 text-[10px] font-mono">
          {historicalKeyYears.map((k) => (
            <button
              key={k.year}
              onClick={() => onYearChange(k.year)}
              className={`flex flex-col items-center transition hover:text-orbit-emerald ${
                selectedYear === k.year ? 'text-orbit-emerald font-bold scale-110' : 'text-orbit-muted'
              }`}
            >
              <div className={`w-1.5 h-1.5 rounded-full mb-1 ${
                selectedYear === k.year ? 'bg-orbit-emerald ring-2 ring-orbit-emerald/30' : 'bg-orbit-border'
              }`} />
              <span>{k.year}</span>
              <span className="text-[9px] opacity-70 hidden md:block">{k.label}</span>
            </button>
          ))}

          {/* Dividing Vertical Divider */}
          <div className="h-6 w-px bg-purple-500/40 my-auto" />

          {forecastKeyYears.map((k) => (
            <button
              key={k.year}
              onClick={() => onYearChange(k.year)}
              className={`flex flex-col items-center transition hover:text-purple-300 ${
                selectedYear === k.year ? 'text-purple-300 font-bold scale-110' : 'text-purple-400/60'
              }`}
            >
              <div className={`w-1.5 h-1.5 rounded-full mb-1 ${
                selectedYear === k.year ? 'bg-purple-400 ring-2 ring-purple-400/40' : 'bg-purple-900'
              }`} />
              <span>{k.year}</span>
              <span className="text-[9px] opacity-70 hidden md:block">{k.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
