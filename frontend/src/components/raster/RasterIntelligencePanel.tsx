import React, { useState } from 'react';
import { IndexCalculationResult, TemporalMeasurementSeries } from '../../types/rasterIntelligence';
import { TimeSeriesChart } from './TimeSeriesChart';
import { DEMO_NDVI_RESULT, DEMO_TIME_SERIES } from '../../services/rasterService';

interface Props {
  result?: IndexCalculationResult;
  timeSeries?: TemporalMeasurementSeries;
}

export const RasterIntelligencePanel: React.FC<Props> = ({
  result = DEMO_NDVI_RESULT,
  timeSeries = DEMO_TIME_SERIES,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'vegetation' | 'water' | 'urban' | 'timeseries' | 'provenance'>('overview');

  const stats = result.statistics;
  const veg = result.vegetation_summary;

  return (
    <div className="flex-1 flex flex-col overflow-hidden font-mono text-xs select-none" data-testid="raster-intelligence-panel">
      {/* 1. Header with Epistemic Classification */}
      <div className="p-3 bg-orbit-slate/40 border-b border-orbit-border flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-orbit-text text-sm">
              {result.index_name} SPECTRAL INTELLIGENCE
            </span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-950/40 text-blue-400 border border-blue-800/40 font-bold">
              CALCULATED
            </span>
          </div>
          <p className="text-[10px] text-orbit-muted truncate mt-0.5">{result.formula}</p>
        </div>
      </div>

      {/* 2. Navigation Tabs */}
      <div className="grid grid-cols-6 border-b border-orbit-border bg-orbit-slate/20 text-[10px]">
        {[
          { key: 'overview', label: 'Stats' },
          { key: 'vegetation', label: 'Vegetation' },
          { key: 'water', label: 'Water' },
          { key: 'urban', label: 'Built-up' },
          { key: 'timeseries', label: 'Timeline' },
          { key: 'provenance', label: 'Trace' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`py-2 text-center font-semibold transition border-b-2 ${
              activeTab === tab.key
                ? 'border-orbit-emerald text-orbit-emerald bg-orbit-emerald/10'
                : 'border-transparent text-orbit-muted hover:text-orbit-text'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 3. Tab Body Content */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {/* TAB 1: OVERVIEW STATISTICS */}
        {activeTab === 'overview' && (
          <div className="space-y-3">
            {/* Primary KPI Grid */}
            <div className="grid grid-cols-3 gap-2">
              <div className="bg-orbit-slate/40 p-2.5 rounded-lg border border-orbit-border">
                <span className="text-[10px] text-orbit-muted uppercase block">Mean Index</span>
                <span className="text-base font-bold text-orbit-emerald">{stats.mean?.toFixed(3)}</span>
              </div>
              <div className="bg-orbit-slate/40 p-2.5 rounded-lg border border-orbit-border">
                <span className="text-[10px] text-orbit-muted uppercase block">Median</span>
                <span className="text-base font-bold text-orbit-cyan">{stats.median?.toFixed(3)}</span>
              </div>
              <div className="bg-orbit-slate/40 p-2.5 rounded-lg border border-orbit-border">
                <span className="text-[10px] text-orbit-muted uppercase block">Std Deviation</span>
                <span className="text-base font-bold text-orbit-text">{stats.std_dev?.toFixed(3)}</span>
              </div>
            </div>

            {/* Range & Percentile Distribution */}
            <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border space-y-2">
              <span className="text-[10px] font-bold text-orbit-muted uppercase tracking-wider block">
                Statistical Distribution
              </span>
              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <div className="flex justify-between border-b border-orbit-border/40 pb-1">
                  <span className="text-orbit-muted">Minimum Value:</span>
                  <span className="font-bold text-orbit-text">{stats.min?.toFixed(3)}</span>
                </div>
                <div className="flex justify-between border-b border-orbit-border/40 pb-1">
                  <span className="text-orbit-muted">Maximum Value:</span>
                  <span className="font-bold text-orbit-text">{stats.max?.toFixed(3)}</span>
                </div>
                <div className="flex justify-between border-b border-orbit-border/40 pb-1">
                  <span className="text-orbit-muted">25th Percentile:</span>
                  <span className="font-bold text-orbit-text">{stats.percentile_25?.toFixed(3)}</span>
                </div>
                <div className="flex justify-between border-b border-orbit-border/40 pb-1">
                  <span className="text-orbit-muted">75th Percentile:</span>
                  <span className="font-bold text-orbit-text">{stats.percentile_75?.toFixed(3)}</span>
                </div>
                <div className="flex justify-between border-b border-orbit-border/40 pb-1">
                  <span className="text-orbit-muted">10th Percentile:</span>
                  <span className="font-bold text-orbit-text">{stats.percentile_10?.toFixed(3)}</span>
                </div>
                <div className="flex justify-between border-b border-orbit-border/40 pb-1">
                  <span className="text-orbit-muted">90th Percentile:</span>
                  <span className="font-bold text-orbit-text">{stats.percentile_90?.toFixed(3)}</span>
                </div>
              </div>
            </div>

            {/* Spatial Extent & Valid Pixel Stats */}
            <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border space-y-1.5 text-[10px]">
              <span className="text-[10px] font-bold text-orbit-muted uppercase tracking-wider block">
                Spatial Surface Metrics
              </span>
              <div className="flex justify-between">
                <span className="text-orbit-muted">Valid Area:</span>
                <span className="font-bold text-orbit-emerald">{stats.total_valid_area_km2.toFixed(2)} km²</span>
              </div>
              <div className="flex justify-between">
                <span className="text-orbit-muted">Valid Pixels:</span>
                <span className="font-bold text-orbit-text">
                  {stats.valid_pixel_count.toLocaleString()} ({stats.valid_pixel_percentage}%)
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-orbit-muted">Pixel Resolution:</span>
                <span className="font-bold text-orbit-text">{stats.pixel_area_m2.toFixed(0)} m² / pixel</span>
              </div>
              <div className="flex justify-between pt-1 border-t border-orbit-border/40 text-[9px]">
                <span className="text-orbit-muted">Geodesic Method:</span>
                <span className="text-orbit-cyan font-bold truncate">{stats.area_calculation_method}</span>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: VEGETATION CANOPY STRATIFICATION */}
        {activeTab === 'vegetation' && veg && (
          <div className="space-y-3">
            <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-orbit-emerald uppercase">Total Vegetated Cover</span>
                <span className="text-sm font-bold text-orbit-emerald">{veg.total_vegetated_percentage}%</span>
              </div>
              <div className="w-full h-2 bg-orbit-slate rounded-full overflow-hidden flex">
                <div style={{ width: `${veg.dense_vegetation_percentage}%` }} className="bg-emerald-600 h-full" title="Dense" />
                <div style={{ width: `${veg.moderate_vegetation_percentage}%` }} className="bg-emerald-500 h-full" title="Moderate" />
                <div style={{ width: `${veg.low_vegetation_percentage}%` }} className="bg-emerald-400 h-full" title="Low" />
                <div style={{ width: `${veg.non_vegetated_percentage}%` }} className="bg-amber-600 h-full" title="Non-vegetated" />
              </div>
            </div>

            <div className="space-y-1.5 text-[10px]">
              {[
                { label: 'Dense Canopy (NDVI ≥ 0.60)', area: veg.dense_vegetation_area_km2, pct: veg.dense_vegetation_percentage, color: 'text-emerald-500' },
                { label: 'Moderate Canopy (0.40 – 0.60)', area: veg.moderate_vegetation_area_km2, pct: veg.moderate_vegetation_percentage, color: 'text-emerald-400' },
                { label: 'Low / Sparse (0.20 – 0.40)', area: veg.low_vegetation_area_km2, pct: veg.low_vegetation_percentage, color: 'text-emerald-300' },
                { label: 'Non-Vegetated / Bare (< 0.20)', area: veg.non_vegetated_area_km2, pct: veg.non_vegetated_percentage, color: 'text-amber-500' },
              ].map((row) => (
                <div key={row.label} className="flex items-center justify-between p-2 rounded bg-orbit-slate/30 border border-orbit-border/40">
                  <span className={row.color}>{row.label}</span>
                  <div className="text-right font-bold">
                    <span className="text-orbit-text mr-2">{row.area.toFixed(2)} km²</span>
                    <span className="text-orbit-cyan">{row.pct}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 3: WATER INTELLIGENCE */}
        {activeTab === 'water' && (
          <div className="space-y-3">
            <div className="p-3 bg-orbit-cyan/10 border border-orbit-cyan/30 rounded-lg space-y-1">
              <div className="flex items-center justify-between font-bold text-orbit-cyan">
                <span>NDWI SURFACE WATER DETECTION</span>
                <span className="text-[9px] px-1 rounded bg-orbit-cyan/20 border border-orbit-cyan/40">CALCULATED</span>
              </div>
              <p className="text-[10px] text-orbit-muted">
                Formula: (GREEN - NIR) / (GREEN + NIR) [McFeeters 1996]. Rule-based thresholding for open surface water bodies.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-orbit-slate/30 border border-orbit-border space-y-2 text-[10px]">
              <div className="flex justify-between">
                <span className="text-orbit-muted">Water Candidate Area:</span>
                <span className="font-bold text-orbit-cyan">4.12 km² (2.77%)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-orbit-muted">Detection Threshold:</span>
                <span className="font-bold text-orbit-text">NDWI ≥ 0.00</span>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: BUILT-UP / URBAN INTELLIGENCE */}
        {activeTab === 'urban' && (
          <div className="space-y-3">
            <div className="p-3 bg-orange-950/20 border border-orange-800/40 rounded-lg space-y-1">
              <div className="flex items-center justify-between font-bold text-orange-400">
                <span>NDBI BUILT-UP / IMPERVIOUS INDEX</span>
                <span className="text-[9px] px-1 rounded bg-orange-950/40 border border-orange-800/40">CALCULATED</span>
              </div>
              <p className="text-[10px] text-orbit-muted">
                Formula: (SWIR - NIR) / (SWIR + NIR) [Zha et al. 2003]. Delineates artificial structures, pavement, and bare soil.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-orbit-slate/30 border border-orbit-border space-y-2 text-[10px]">
              <div className="flex justify-between">
                <span className="text-orbit-muted">Built-up Candidate Area:</span>
                <span className="font-bold text-orange-400">8.65 km² (5.82%)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-orbit-muted">Detection Threshold:</span>
                <span className="font-bold text-orbit-text">{'NDBI > 0.00'}</span>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: MULTI-TEMPORAL TIME SERIES */}
        {activeTab === 'timeseries' && (
          <TimeSeriesChart series={timeSeries} />
        )}

        {/* TAB 6: PROVENANCE */}
        {activeTab === 'provenance' && (
          <div className="space-y-2 text-[10px] bg-orbit-void/80 p-2.5 rounded-lg border border-orbit-border">
            <span className="font-bold text-orbit-emerald block uppercase">Scientific Lineage & Trace</span>
            <div className="space-y-1.5">
              <div>
                <span className="text-orbit-muted block">Source Telemetry:</span>
                <span className="text-orbit-text break-all font-mono">{result.scene_id}</span>
              </div>
              <div>
                <span className="text-orbit-muted block">Algorithm Equation:</span>
                <span className="text-orbit-cyan font-mono">{result.formula}</span>
              </div>
              <div>
                <span className="text-orbit-muted block">Bands Utilized:</span>
                <span className="text-orbit-text font-mono">{JSON.stringify(result.provenance?.bands_used || {})}</span>
              </div>
              <div>
                <span className="text-orbit-muted block">Spatial Projection:</span>
                <span className="text-orbit-text">{result.provenance?.crs || 'EPSG:32621'}</span>
              </div>
              <div>
                <span className="text-orbit-muted block">Processing Software:</span>
                <span className="text-orbit-text">{result.provenance?.software || 'ORBIT Raster Processing Engine v1.0'}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
