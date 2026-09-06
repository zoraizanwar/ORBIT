import React from 'react';
import {
  GitMerge,
  ArrowRight,
} from 'lucide-react';

export interface AlignmentItem {
  source_observation_id: string;
  target_observation_id: string;
  temporal_offset_days: number;
  spatial_overlap_percentage: number;
  resolution_ratio: number;
  status: 'ALIGNED' | 'PARTIALLY_ALIGNED' | 'INCOMPATIBLE';
  reasons: string[];
  resampling_applied?: boolean;
}

interface Props {
  alignments: AlignmentItem[];
}

export const ObservationAlignmentView: React.FC<Props> = ({ alignments }) => {
  return (
    <div
      className="p-3 bg-orbit-carbon/95 border border-orbit-border rounded-xl font-mono text-xs select-none space-y-2.5 shadow-xl"
      data-testid="observation-alignment-view"
    >
      <div className="flex items-center justify-between pb-1.5 border-b border-orbit-border">
        <div className="flex items-center gap-1.5 text-orbit-emerald font-bold text-[11px]">
          <GitMerge className="w-3.5 h-3.5" />
          <span>MULTI-TEMPORAL ALIGNMENT MATRIX</span>
        </div>
        <span className="text-[9px] px-1.5 py-0.5 rounded bg-orbit-slate text-orbit-muted border border-orbit-border">
          {alignments.length} Alignment Pairs
        </span>
      </div>

      <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
        {alignments.map((a, idx) => {
          let statusBadge = (
            <span className="text-[8px] px-1.5 py-0.5 rounded bg-orbit-emerald/20 text-orbit-emerald border border-orbit-emerald/40 font-bold">
              ALIGNED
            </span>
          );

          if (a.status === 'PARTIALLY_ALIGNED') {
            statusBadge = (
              <span className="text-[8px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/40 font-bold">
                PARTIAL
              </span>
            );
          } else if (a.status === 'INCOMPATIBLE') {
            statusBadge = (
              <span className="text-[8px] px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/40 font-bold">
                INCOMPATIBLE
              </span>
            );
          }

          return (
            <div key={idx} className="p-2 rounded-lg bg-orbit-slate/30 border border-orbit-border space-y-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-[10px] font-bold text-orbit-text">
                  <span className="text-orbit-emerald">{a.source_observation_id}</span>
                  <ArrowRight className="w-3 h-3 text-orbit-muted" />
                  <span className="text-orbit-cyan">{a.target_observation_id}</span>
                </div>
                {statusBadge}
              </div>

              <div className="grid grid-cols-3 gap-1 text-[9px] text-orbit-muted">
                <div>Offset: {a.temporal_offset_days.toFixed(1)}d</div>
                <div>Overlap: {a.spatial_overlap_percentage.toFixed(0)}%</div>
                <div>GSD Ratio: {a.resolution_ratio.toFixed(1)}x</div>
              </div>

              {a.reasons.length > 0 && (
                <div className="text-[9px] text-amber-400/90 pt-0.5">
                  {a.reasons.join(', ')}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
