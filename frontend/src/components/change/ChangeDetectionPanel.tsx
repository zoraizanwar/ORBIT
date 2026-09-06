import React, { useState } from 'react';
import {
  TrendingDown,
  TrendingUp,
  Calendar,
} from 'lucide-react';
import {
  ChangeComparisonResult,
  SpatialChangeMaskResult,
  DetectedChangeEvent,
} from '../../types/changeDetection';
import {
  DEMO_CHANGE_COMPARISON,
  DEMO_SPATIAL_CHANGE_MASK,
  DEMO_DETECTED_CHANGE_EVENTS,
} from '../../services/changeService';
import { EvidenceStrengthBadge } from '../intelligence/EvidenceStrengthBadge';

interface Props {
  comparison?: ChangeComparisonResult;
  spatialMask?: SpatialChangeMaskResult;
  events?: DetectedChangeEvent[];
}

export const ChangeDetectionPanel: React.FC<Props> = ({
  comparison = DEMO_CHANGE_COMPARISON,
  spatialMask = DEMO_SPATIAL_CHANGE_MASK,
  events = DEMO_DETECTED_CHANGE_EVENTS,
}) => {
  const [activeTab, setActiveTab] = useState<'compare' | 'spatial' | 'events' | 'provenance'>('compare');

  const stats = spatialMask.statistics;
  const isLoss = comparison.absolute_delta < 0;

  return (
    <div className="flex-1 flex flex-col overflow-hidden font-mono text-xs select-none" data-testid="change-detection-panel">
      {/* 1. Header with Epistemic Badge */}
      <div className="p-3 bg-orbit-slate/40 border-b border-orbit-border flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-orbit-text text-sm">
              MULTI-TEMPORAL CHANGE DETECTION
            </span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-950/40 text-blue-400 border border-blue-800/40 font-bold">
              CALCULATED
            </span>
          </div>
          <p className="text-[10px] text-orbit-muted truncate mt-0.5">
            Pairwise Differential Telemetry Analysis ({comparison.metric})
          </p>
        </div>
      </div>

      {/* 2. Navigation Tabs */}
      <div className="grid grid-cols-4 border-b border-orbit-border bg-orbit-slate/20 text-[10px]">
        {[
          { key: 'compare', label: 'T1 / T2 Delta' },
          { key: 'spatial', label: 'Spatial Mask' },
          { key: 'events', label: 'Events' },
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
        {/* TAB 1: PAIRWISE COMPARISON */}
        {activeTab === 'compare' && (
          <div className="space-y-3">
            {/* T1 vs T2 Side-by-Side Card */}
            <div className="grid grid-cols-2 gap-2">
              {/* T1 Baseline */}
              <div className="bg-orbit-slate/40 p-2.5 rounded-lg border border-orbit-border space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-orbit-cyan">T1 BASELINE</span>
                  <span className="text-[9px] text-orbit-muted">{comparison.t1_platform}</span>
                </div>
                <div className="flex items-center gap-1 text-orbit-text text-[11px]">
                  <Calendar className="w-3 h-3 text-orbit-muted" />
                  <span>{new Date(comparison.t1_acquisition).toLocaleDateString()}</span>
                </div>
                <div className="text-base font-bold text-orbit-text pt-1 border-t border-orbit-border/40">
                  {comparison.t1_value.toFixed(3)}
                </div>
              </div>

              {/* T2 Target */}
              <div className="bg-orbit-slate/40 p-2.5 rounded-lg border border-orbit-border space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-orbit-emerald">T2 RE-OBSERVED</span>
                  <span className="text-[9px] text-orbit-muted">{comparison.t2_platform}</span>
                </div>
                <div className="flex items-center gap-1 text-orbit-text text-[11px]">
                  <Calendar className="w-3 h-3 text-orbit-muted" />
                  <span>{new Date(comparison.t2_acquisition).toLocaleDateString()}</span>
                </div>
                <div className="text-base font-bold text-orbit-text pt-1 border-t border-orbit-border/40">
                  {comparison.t2_value.toFixed(3)}
                </div>
              </div>
            </div>

            {/* Differential Change Summary Banner */}
            <div className="bg-orbit-slate/30 p-3 rounded-lg border border-orbit-border space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-orbit-muted uppercase tracking-wider">
                  Differential Transition
                </span>
                <span
                  className={`text-[9px] px-2 py-0.5 rounded font-bold border ${
                    comparison.classification.includes('DECREASE')
                      ? 'bg-amber-950/40 text-amber-400 border-amber-800/40'
                      : comparison.classification.includes('INCREASE')
                      ? 'bg-emerald-950/40 text-emerald-400 border-emerald-800/40'
                      : 'bg-orbit-slate text-orbit-muted border-orbit-border'
                  }`}
                >
                  {comparison.classification.replace('_', ' ')}
                </span>
              </div>

              <div className="flex items-center justify-between pt-1">
                <div>
                  <span className="text-[10px] text-orbit-muted block">Absolute Delta (Δ)</span>
                  <div className="flex items-center gap-1 text-base font-bold">
                    {isLoss ? (
                      <TrendingDown className="w-4 h-4 text-orbit-crimson" />
                    ) : (
                      <TrendingUp className="w-4 h-4 text-orbit-emerald" />
                    )}
                    <span className={isLoss ? 'text-orbit-crimson' : 'text-orbit-emerald'}>
                      {comparison.absolute_delta > 0 ? '+' : ''}
                      {comparison.absolute_delta.toFixed(3)}
                    </span>
                  </div>
                </div>

                {comparison.percentage_change !== null && comparison.percentage_change !== undefined && (
                  <div className="text-right">
                    <span className="text-[10px] text-orbit-muted block">Relative Magnitude</span>
                    <span className={`text-base font-bold ${isLoss ? 'text-orbit-crimson' : 'text-orbit-emerald'}`}>
                      {comparison.percentage_change > 0 ? '+' : ''}
                      {comparison.percentage_change.toFixed(1)}%
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Quality & Observation Assurance */}
            <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border text-[10px] space-y-1.5">
              <span className="font-bold text-orbit-muted uppercase tracking-wider block">
                Telemetry Assurance
              </span>
              <div className="flex justify-between">
                <span className="text-orbit-muted">Observation Interval:</span>
                <span className="font-bold text-orbit-text">{comparison.interval_days} days</span>
              </div>
              <div className="flex justify-between">
                <span className="text-orbit-muted">T1 Valid Pixels / Cloud:</span>
                <span className="font-bold text-orbit-text">
                  {comparison.quality_assessment?.t1_valid_pixel_pct}% /{' '}
                  {comparison.quality_assessment?.t1_cloud_cover}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-orbit-muted">T2 Valid Pixels / Cloud:</span>
                <span className="font-bold text-orbit-text">
                  {comparison.quality_assessment?.t2_valid_pixel_pct}% /{' '}
                  {comparison.quality_assessment?.t2_cloud_cover}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: SPATIAL DIFFERENCE MASK */}
        {activeTab === 'spatial' && (
          <div className="space-y-3">
            <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border space-y-2">
              <span className="text-[10px] font-bold text-orbit-muted uppercase tracking-wider block">
                Spatial Differential Breakdown
              </span>
              <div className="space-y-1.5 text-[10px]">
                {[
                  {
                    label: 'Significant Increase (Δ ≥ +0.15)',
                    area: stats.significant_increase_area_km2,
                    pct: stats.significant_increase_percentage,
                    color: 'text-emerald-500',
                  },
                  {
                    label: 'Moderate Increase (+0.05 to +0.15)',
                    area: stats.increase_area_km2,
                    pct: stats.increase_percentage,
                    color: 'text-emerald-400',
                  },
                  {
                    label: 'Stable / No Change (-0.05 to +0.05)',
                    area: stats.no_change_area_km2,
                    pct: stats.no_change_percentage,
                    color: 'text-orbit-muted',
                  },
                  {
                    label: 'Moderate Decrease (-0.15 to -0.05)',
                    area: stats.decrease_area_km2,
                    pct: stats.decrease_percentage,
                    color: 'text-amber-400',
                  },
                  {
                    label: 'Significant Decrease (Δ ≤ -0.15)',
                    area: stats.significant_decrease_area_km2,
                    pct: stats.significant_decrease_percentage,
                    color: 'text-orbit-crimson',
                  },
                ].map((row) => (
                  <div
                    key={row.label}
                    className="flex items-center justify-between p-1.5 rounded bg-orbit-slate/40 border border-orbit-border/40"
                  >
                    <span className={row.color}>{row.label}</span>
                    <div className="text-right font-bold">
                      <span className="text-orbit-text mr-2">{row.area.toFixed(2)} km²</span>
                      <span className="text-orbit-cyan">{row.pct}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Spatial Delta Statistics */}
            <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border space-y-1.5 text-[10px]">
              <span className="font-bold text-orbit-muted uppercase tracking-wider block">
                Spatial Delta Metrics
              </span>
              <div className="grid grid-cols-2 gap-2">
                <div className="flex justify-between border-b border-orbit-border/40 pb-1">
                  <span className="text-orbit-muted">Min Delta:</span>
                  <span className="font-bold text-orbit-text">{stats.min_delta?.toFixed(3)}</span>
                </div>
                <div className="flex justify-between border-b border-orbit-border/40 pb-1">
                  <span className="text-orbit-muted">Max Delta:</span>
                  <span className="font-bold text-orbit-text">{stats.max_delta?.toFixed(3)}</span>
                </div>
                <div className="flex justify-between border-b border-orbit-border/40 pb-1">
                  <span className="text-orbit-muted">Mean Delta:</span>
                  <span className="font-bold text-orbit-text">{stats.mean_delta?.toFixed(3)}</span>
                </div>
                <div className="flex justify-between border-b border-orbit-border/40 pb-1">
                  <span className="text-orbit-muted">Std Deviation:</span>
                  <span className="font-bold text-orbit-text">{stats.std_dev_delta?.toFixed(3)}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: DETECTED CHANGE EVENTS */}
        {activeTab === 'events' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-[10px] font-bold text-orbit-muted uppercase">
              <span>TIER 2 PERSISTED CHANGE EVENTS</span>
              <span>{events.length} RECORDED</span>
            </div>
            {events.map((evt) => (
              <div
                key={evt.id}
                className="p-3 bg-orbit-slate/30 rounded-lg border border-orbit-border space-y-2 text-[10px]"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-orbit-amber">{evt.change_type}</span>
                  <EvidenceStrengthBadge strength={evt.evidence_strength} size="sm" />
                </div>
                <div className="flex justify-between">
                  <span className="text-orbit-muted">Affected Area:</span>
                  <span className="font-bold text-orbit-emerald">{evt.affected_area_km2} km²</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-orbit-muted">Methodology:</span>
                  <span className="text-orbit-text truncate">{evt.detection_method}</span>
                </div>
                <div className="flex justify-between pt-1 border-t border-orbit-border/40 text-[9px] text-orbit-muted">
                  <span>Confidence: {(evt.confidence * 100).toFixed(0)}%</span>
                  <span>Shift: {evt.percentage_change}%</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* TAB 4: PROVENANCE TRACE */}
        {activeTab === 'provenance' && (
          <div className="space-y-2 text-[10px] bg-orbit-void/80 p-2.5 rounded-lg border border-orbit-border">
            <span className="font-bold text-orbit-emerald block uppercase">Differential Provenance Trace</span>
            <div className="space-y-1.5">
              <div>
                <span className="text-orbit-muted block">T1 Source Scene:</span>
                <span className="text-orbit-text break-all font-mono">{comparison.t1_scene_id}</span>
              </div>
              <div>
                <span className="text-orbit-muted block">T2 Source Scene:</span>
                <span className="text-orbit-text break-all font-mono">{comparison.t2_scene_id}</span>
              </div>
              <div>
                <span className="text-orbit-muted block">Mathematical Equation:</span>
                <span className="text-orbit-cyan font-mono">
                  {comparison.provenance?.calculation_formula || 'delta = V_t2 - V_t1'}
                </span>
              </div>
              <div>
                <span className="text-orbit-muted block">Processing Engine:</span>
                <span className="text-orbit-text">
                  {comparison.provenance?.algorithm || 'ORBIT Multi-Temporal Comparison Engine v1.0'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
