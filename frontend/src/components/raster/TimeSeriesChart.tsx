import React from 'react';
import { Calendar, TrendingDown, TrendingUp, AlertTriangle } from 'lucide-react';
import { TemporalMeasurementSeries } from '../../types/rasterIntelligence';

interface Props {
  series: TemporalMeasurementSeries;
  metricLabel?: string;
  futureForecastPoints?: Array<{
    target_year: number;
    value: number;
    scenario: string;
  }>;
}

export const TimeSeriesChart: React.FC<Props> = ({
  series,
  metricLabel: _metricLabel = 'NDVI Mean',
  futureForecastPoints = [],
}) => {
  const points = series.data_points || [];

  if (points.length === 0) {
    return (
      <div className="p-6 text-center text-orbit-muted border border-orbit-border/50 rounded-lg bg-orbit-slate/20 font-mono text-xs">
        No empirical time series observations recorded for this Area of Interest.
      </div>
    );
  }

  // Calculate SVG chart scales
  const values = points.map((p) => p.value);
  const minVal = Math.min(...values, 0.0);
  const maxVal = Math.max(...values, 1.0);
  const valRange = maxVal - minVal || 1.0;

  const chartWidth = 320;
  const chartHeight = 110;
  const padding = 20;

  const getX = (idx: number, total: number) => {
    return padding + (idx / Math.max(1, total - 1)) * (chartWidth - padding * 2);
  };

  const getY = (val: number) => {
    const norm = (val - minVal) / valRange;
    return chartHeight - padding - norm * (chartHeight - padding * 2);
  };

  const polylinePoints = points
    .map((p, idx) => `${getX(idx, points.length)},${getY(p.value)}`)
    .join(' ');

  const isDecreasing = series.trend_slope_per_year !== null && (series.trend_slope_per_year || 0) < 0;

  return (
    <div className="space-y-3 font-mono text-xs" data-testid="time-series-chart">
      {/* 1. Header Metrics */}
      <div className="flex items-center justify-between bg-orbit-slate/40 p-2.5 rounded-lg border border-orbit-border">
        <div>
          <span className="text-[10px] text-orbit-muted uppercase tracking-wider block">
            Temporal Trend ({points.length} Observations)
          </span>
          <div className="flex items-center gap-1.5 font-bold text-orbit-text mt-0.5">
            {series.trend_slope_per_year !== null && series.trend_slope_per_year !== undefined ? (
              <>
                {isDecreasing ? (
                  <TrendingDown className="w-3.5 h-3.5 text-orbit-crimson" />
                ) : (
                  <TrendingUp className="w-3.5 h-3.5 text-orbit-emerald" />
                )}
                <span className={isDecreasing ? 'text-orbit-crimson' : 'text-orbit-emerald'}>
                  {series.trend_slope_per_year > 0 ? '+' : ''}
                  {series.trend_slope_per_year.toFixed(3)} / yr
                </span>
              </>
            ) : (
              <span>Baseline Series</span>
            )}
          </div>
        </div>

        <div className="text-right">
          <span className="text-[10px] text-orbit-muted block">Coverage Span</span>
          <span className="text-[11px] text-orbit-cyan font-bold">
            {new Date(points[0].acquisition_datetime).getFullYear()} –{' '}
            {new Date(points[points.length - 1].acquisition_datetime).getFullYear()}
          </span>
        </div>
      </div>

      {/* 2. SVG Line Chart Canvas */}
      <div className="relative bg-orbit-void/80 p-2 rounded-lg border border-orbit-border overflow-hidden">
        <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-28 overflow-visible">
          {/* Grid lines */}
          <line
            x1={padding}
            y1={padding}
            x2={chartWidth - padding}
            y2={padding}
            stroke="#262626"
            strokeDasharray="2,2"
          />
          <line
            x1={padding}
            y1={chartHeight / 2}
            x2={chartWidth - padding}
            y2={chartHeight / 2}
            stroke="#262626"
            strokeDasharray="2,2"
          />
          <line
            x1={padding}
            y1={chartHeight - padding}
            x2={chartWidth - padding}
            y2={chartHeight - padding}
            stroke="#333333"
          />

          {/* Area fill */}
          <polygon
            points={`${padding},${chartHeight - padding} ${polylinePoints} ${chartWidth - padding},${chartHeight - padding}`}
            fill="rgba(25, 195, 125, 0.12)"
          />

          {/* Observation line */}
          <polyline
            points={polylinePoints}
            fill="none"
            stroke="#19C37D"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Observation data point dots */}
          {points.map((p, idx) => (
            <circle
              key={p.source_scene_id}
              cx={getX(idx, points.length)}
              cy={getY(p.value)}
              r="3.5"
              className="fill-orbit-emerald stroke-orbit-void stroke-2 cursor-pointer hover:r-5 transition-all"
            >
              <title>{`${new Date(p.acquisition_datetime).toLocaleDateString()}: ${p.value.toFixed(3)} (${p.platform})`}</title>
            </circle>
          ))}
        </svg>

        {/* X-Axis Labels */}
        <div className="flex justify-between text-[9px] text-orbit-muted px-2 mt-1 border-t border-orbit-border/40 pt-1">
          <span>{new Date(points[0].acquisition_datetime).toLocaleDateString()}</span>
          <span className="text-orbit-emerald font-semibold">OBSERVED TELEMETRY</span>
          <span>{new Date(points[points.length - 1].acquisition_datetime).toLocaleDateString()}</span>
        </div>
      </div>

      {/* 3. Observation Data Points Table */}
      <div className="space-y-1 max-h-36 overflow-y-auto pr-1 divide-y divide-orbit-border/30">
        {points.map((pt) => (
          <div key={pt.source_scene_id} className="flex items-center justify-between py-1 text-[10px]">
            <div className="flex items-center gap-1.5">
              <Calendar className="w-3 h-3 text-orbit-muted" />
              <span className="text-orbit-text">{new Date(pt.acquisition_datetime).toLocaleDateString()}</span>
              <span className="text-[9px] px-1 rounded bg-orbit-slate text-orbit-muted">
                {pt.platform}
              </span>
            </div>
            <div className="flex items-center gap-2 font-bold">
              <span className="text-orbit-cyan">{pt.value.toFixed(3)}</span>
              <span className="text-[8px] px-1 rounded bg-orbit-emerald/20 text-orbit-emerald border border-orbit-emerald/30">
                CALCULATED
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* 4. Strict Future Prediction Horizon Boundary */}
      {futureForecastPoints.length > 0 && (
        <div className="p-2.5 bg-orbit-amber/10 border border-orbit-amber/30 rounded-lg space-y-1">
          <div className="flex items-center justify-between text-[10px] text-orbit-amber font-bold">
            <span className="flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>FORECAST HORIZON (2027–2050)</span>
            </span>
            <span className="text-[9px] px-1 rounded bg-orbit-amber/20 border border-orbit-amber/40">
              PREDICTED
            </span>
          </div>
          <p className="text-[9px] text-orbit-muted">
            Future model projections require validated historical calibration series and explicit scenario modeling.
          </p>
        </div>
      )}
    </div>
  );
};
