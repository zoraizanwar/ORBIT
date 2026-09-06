import React from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  Loader2,
  AlertCircle,
  X,
  Play,
} from 'lucide-react';

export type StageState = 'PENDING' | 'RUNNING' | 'COMPLETE' | 'FAILED' | 'INSUFFICIENT_DATA' | 'INSUFFICIENT_EVIDENCE';

export interface StageStatus {
  name: string;
  level: string;
  state: StageState;
  details?: string;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  stages: StageStatus[];
  isExecuting: boolean;
  onExecute: () => void;
  onViewResults: () => void;
  isComplete: boolean;
}

export const AnalysisExecutionPanel: React.FC<Props> = ({
  isOpen,
  onClose,
  stages,
  isExecuting,
  onExecute,
  onViewResults,
  isComplete,
}) => {
  if (!isOpen) return null;

  return (
    <div
      className="absolute top-16 right-4 z-30 w-[400px] bg-orbit-carbon/95 backdrop-blur-md border border-orbit-border rounded-xl shadow-2xl flex flex-col overflow-hidden select-none font-mono text-xs"
      data-testid="analysis-execution-panel"
    >
      <div className="p-3 bg-orbit-slate/60 border-b border-orbit-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-orbit-emerald/10 border border-orbit-emerald/30 text-orbit-emerald">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <div className="font-bold text-orbit-text">ANALYTICAL LIFECYCLE</div>
            <p className="text-[10px] text-orbit-muted">8-Tier Epistemic Execution Pipeline</p>
          </div>
        </div>

        <button onClick={onClose} className="p-1 text-orbit-muted hover:text-orbit-text">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Stages List */}
      <div className="p-3 space-y-2 max-h-[420px] overflow-y-auto">
        {stages.map((stage, idx) => {
          let stateColor = 'text-orbit-muted border-orbit-border bg-orbit-slate/20';
          let icon = <span className="text-[10px]">{idx + 1}</span>;

          if (stage.state === 'RUNNING') {
            stateColor = 'text-amber-400 border-amber-500/40 bg-amber-500/10';
            icon = <Loader2 className="w-3.5 h-3.5 animate-spin" />;
          } else if (stage.state === 'COMPLETE') {
            stateColor = 'text-orbit-emerald border-orbit-emerald/40 bg-orbit-emerald/10';
            icon = <CheckCircle2 className="w-3.5 h-3.5" />;
          } else if (stage.state === 'INSUFFICIENT_DATA') {
            stateColor = 'text-cyan-400 border-cyan-500/40 bg-cyan-500/10';
            icon = <span className="text-[9px] font-bold">GUARD</span>;
          } else if (stage.state === 'FAILED') {
            stateColor = 'text-rose-400 border-rose-500/40 bg-rose-500/10';
            icon = <AlertCircle className="w-3.5 h-3.5" />;
          }

          return (
            <div
              key={stage.name}
              className={`p-2 rounded-lg border flex items-center justify-between ${stateColor}`}
            >
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 rounded flex items-center justify-center font-bold">
                  {icon}
                </div>
                <div>
                  <div className="text-[11px] font-bold text-orbit-text">{stage.name}</div>
                  {stage.details && <div className="text-[9px] text-orbit-muted">{stage.details}</div>}
                </div>
              </div>

              <span className="text-[9px] px-1.5 py-0.5 rounded bg-orbit-carbon border border-orbit-border font-bold">
                {stage.level}
              </span>
            </div>
          );
        })}
      </div>

      {/* Action Footer */}
      <div className="p-3 bg-orbit-slate/40 border-t border-orbit-border space-y-2">
        {!isComplete ? (
          <button
            onClick={onExecute}
            disabled={isExecuting}
            className="w-full py-2 bg-orbit-emerald/20 hover:bg-orbit-emerald/30 border border-orbit-emerald/50 text-orbit-emerald rounded-lg font-bold flex items-center justify-center gap-2 transition disabled:opacity-50"
          >
            {isExecuting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            <span>{isExecuting ? 'Executing Verified Pipeline...' : 'Run Operational Pipeline'}</span>
          </button>
        ) : (
          <button
            onClick={onViewResults}
            className="w-full py-2 bg-orbit-emerald text-orbit-carbon font-bold rounded-lg flex items-center justify-center gap-2 transition hover:bg-orbit-emerald/90"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>View Grounded Intelligence Results</span>
          </button>
        )}
      </div>
    </div>
  );
};
