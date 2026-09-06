import React from 'react';
import { TemporalContextResult } from '../../types/intelligence';

interface Props {
  context: TemporalContextResult;
}

export const TemporalContextCard: React.FC<Props> = ({ context }) => {
  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-lg p-3 space-y-2.5">
      <div className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center justify-between">
        <span>Temporal Window Context</span>
        <span className="text-[10px] px-1.5 py-0.5 rounded font-mono bg-blue-500/20 text-blue-300 border border-blue-500/40">
          {context.temporal_alignment}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 text-xs">
        <div className="p-2 bg-gray-950/40 border border-gray-800/80 rounded">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider">Baseline T1</div>
          <div className="font-mono text-gray-200 mt-0.5">{context.start_date.split('T')[0]}</div>
        </div>

        <div className="p-2 bg-gray-950/40 border border-gray-800/80 rounded">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider">Comparison T2</div>
          <div className="font-mono text-gray-200 mt-0.5">{context.end_date.split('T')[0]}</div>
        </div>

        <div className="p-2 bg-gray-950/40 border border-gray-800/80 rounded">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider">Observation Span</div>
          <div className="font-mono text-gray-200 mt-0.5">{context.interval_days} days</div>
        </div>
      </div>
    </div>
  );
};
