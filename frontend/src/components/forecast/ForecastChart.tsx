import React from 'react';
import { ForecastPredictionPoint, HistoricalObservation } from '../../types/forecasting';

interface ForecastChartProps {
  historical: HistoricalObservation[];
  predictions: ForecastPredictionPoint[];
  metric: string;
}

export const ForecastChart: React.FC<ForecastChartProps> = ({
  historical,
  predictions,
  metric,
}) => {
  // Compute chart coordinates
  const allPoints = [
    ...historical.map((h) => ({
      year: new Date(h.acquisition_datetime).getFullYear(),
      val: h.value,
      type: 'HISTORICAL' as const,
      lower: null as number | null,
      upper: null as number | null,
    })),
    ...predictions.map((p) => ({
      year: p.target_year,
      val: p.predicted_value,
      type: 'PREDICTED' as const,
      lower: p.lower_bound,
      upper: p.upper_bound,
    })),
  ].sort((a, b) => a.year - b.year);

  if (allPoints.length === 0) {
    return <div className="text-gray-500 text-xs p-4">No series data available.</div>;
  }

  const minYear = allPoints[0].year;
  const maxYear = allPoints[allPoints.length - 1].year;
  const minVal = 0.35;
  const maxVal = 0.85;

  const width = 640;
  const height = 220;
  const padLeft = 45;
  const padRight = 30;
  const padTop = 20;
  const padBottom = 30;

  const getX = (year: number) => {
    return padLeft + ((year - minYear) / Math.max(1, maxYear - minYear)) * (width - padLeft - padRight);
  };

  const getY = (val: number) => {
    return height - padBottom - ((val - minVal) / Math.max(0.01, maxVal - minVal)) * (height - padTop - padBottom);
  };

  const historicalPoints = allPoints.filter((p) => p.type === 'HISTORICAL');
  const predictedPoints = allPoints.filter((p) => p.type === 'PREDICTED');

  const histPath = historicalPoints.reduce((acc, p, i) => {
    return `${acc} ${i === 0 ? 'M' : 'L'} ${getX(p.year)} ${getY(p.val)}`;
  }, '');

  // Connect last historical point to first prediction for dashed projection line
  const lastHist = historicalPoints[historicalPoints.length - 1];
  const predPath = [lastHist, ...predictedPoints].filter(Boolean).reduce((acc, p, i) => {
    return `${acc} ${i === 0 ? 'M' : 'L'} ${getX(p.year)} ${getY(p.val)}`;
  }, '');

  // Shaded uncertainty polygon for predictions
  const upperPath = predictedPoints.map((p) => `${getX(p.year)},${getY(p.upper ?? p.val)}`).join(' ');
  const lowerPath = [...predictedPoints].reverse().map((p) => `${getX(p.year)},${getY(p.lower ?? p.val)}`).join(' ');
  const polygonPoints = `${upperPath} ${lowerPath}`;

  const lastHistYear = lastHist ? lastHist.year : minYear;
  const dividerX = getX(lastHistYear + 0.5);

  return (
    <div className="bg-gray-950 border border-gray-800 rounded-lg p-3 space-y-2">
      <div className="flex items-center justify-between text-xs font-bold text-gray-300">
        <div className="flex items-center space-x-2">
          <span>{metric} Trajectory Analysis</span>
          <span className="text-[10px] text-gray-500 font-mono">
            {minYear} – {maxYear}
          </span>
        </div>
        <div className="flex items-center space-x-4 text-[11px]">
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block" />
            <span className="text-gray-400">Historical [CALCULATED]</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-400 inline-block" />
            <span className="text-purple-300">Forecast [PREDICTED]</span>
          </div>
        </div>
      </div>

      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} className="overflow-visible">
        {/* Grid lines */}
        {[0.4, 0.5, 0.6, 0.7, 0.8].map((v) => (
          <g key={v}>
            <line
              x1={padLeft}
              y1={getY(v)}
              x2={width - padRight}
              y2={getY(v)}
              stroke="#1f2937"
              strokeDasharray="2,2"
            />
            <text x={padLeft - 6} y={getY(v) + 3} textAnchor="end" fontSize="9" fill="#6b7280" className="font-mono">
              {v.toFixed(2)}
            </text>
          </g>
        ))}

        {/* Demarcation Divider */}
        <line
          x1={dividerX}
          y1={padTop}
          x2={dividerX}
          y2={height - padBottom}
          stroke="#4b5563"
          strokeDasharray="4,4"
          strokeWidth="1.5"
        />
        <text x={dividerX - 6} y={padTop + 10} textAnchor="end" fontSize="9" fill="#9ca3af" className="font-mono">
          HISTORICAL
        </text>
        <text x={dividerX + 6} y={padTop + 10} textAnchor="start" fontSize="9" fill="#c084fc" className="font-mono">
          FORECAST
        </text>

        {/* Shaded 95% Confidence Interval Envelope */}
        {predictedPoints.length > 0 && (
          <polygon points={polygonPoints} fill="#a855f7" fillOpacity="0.15" />
        )}

        {/* Historical Line (Solid Cyan) */}
        <path d={histPath} fill="none" stroke="#22d3ee" strokeWidth="2.5" />

        {/* Forecast Line (Dashed Purple) */}
        <path d={predPath} fill="none" stroke="#c084fc" strokeWidth="2" strokeDasharray="5,4" />

        {/* Historical Data Points */}
        {historicalPoints.map((p) => (
          <circle
            key={p.year}
            cx={getX(p.year)}
            cy={getY(p.val)}
            r="4"
            fill="#22d3ee"
            stroke="#083344"
            strokeWidth="1.5"
          />
        ))}

        {/* Predicted Data Points */}
        {predictedPoints.map((p) => (
          <circle
            key={p.year}
            cx={getX(p.year)}
            cy={getY(p.val)}
            r="4"
            fill="#c084fc"
            stroke="#3b0764"
            strokeWidth="1.5"
          />
        ))}

        {/* X-axis labels */}
        {allPoints.map((p) => (
          <text
            key={p.year}
            x={getX(p.year)}
            y={height - padBottom + 16}
            textAnchor="middle"
            fontSize="9"
            fill={p.type === 'HISTORICAL' ? '#9ca3af' : '#c084fc'}
            className="font-mono"
          >
            {p.year}
          </text>
        ))}
      </svg>
    </div>
  );
};
