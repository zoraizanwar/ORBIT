import React from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
} from 'lucide-react';

export interface ContradictionFindingItem {
  finding_id: string;
  relationship: 'SUPPORTED' | 'CORROBORATED' | 'CONTRADICTED' | 'INCONCLUSIVE';
  primary_sensor: string;
  primary_metric: string;
  primary_value: number;
  secondary_sensor: string;
  secondary_metric: string;
  secondary_value: number;
  explanation: string;
  evidence_ids: string[];
}

interface Props {
  findings: ContradictionFindingItem[];
}

export const ContradictionInspector: React.FC<Props> = ({ findings }) => {
  return (
    <div
      className="p-3 bg-orbit-carbon/95 border border-orbit-border rounded-xl font-mono text-xs select-none space-y-2.5 shadow-xl"
      data-testid="contradiction-inspector"
    >
      <div className="flex items-center justify-between pb-1.5 border-b border-orbit-border">
        <div className="flex items-center gap-1.5 text-orbit-emerald font-bold text-[11px]">
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>CROSS-SENSOR CONTRADICTION INSPECTOR</span>
        </div>
        <span className="text-[9px] px-1.5 py-0.5 rounded bg-orbit-slate text-orbit-muted border border-orbit-border font-bold">
          {findings.length} Evaluated Findings
        </span>
      </div>

      {findings.length === 0 ? (
        <div className="p-3 text-center text-[10px] text-orbit-muted italic bg-orbit-slate/20 rounded-lg">
          No conflicting multi-sensor signals detected across current observations.
        </div>
      ) : (
        <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
          {findings.map((f) => {
            const isContradiction = f.relationship === 'CONTRADICTED';

            return (
              <div
                key={f.finding_id}
                className={`p-2.5 rounded-lg border space-y-1.5 ${
                  isContradiction
                    ? 'bg-rose-500/10 border-rose-500/30'
                    : 'bg-orbit-emerald/10 border-orbit-emerald/30'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    {isContradiction ? (
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                    ) : (
                      <CheckCircle2 className="w-3.5 h-3.5 text-orbit-emerald" />
                    )}
                    <span className={`text-[10px] font-bold ${isContradiction ? 'text-rose-400' : 'text-orbit-emerald'}`}>
                      {f.relationship}
                    </span>
                  </div>
                  <span className="text-[8px] text-orbit-muted font-mono">{f.finding_id}</span>
                </div>

                <div className="grid grid-cols-2 gap-1 text-[9px] p-1.5 bg-orbit-carbon/60 rounded">
                  <div>
                    <span className="text-orbit-muted block">{f.primary_sensor}:</span>
                    <span className="text-orbit-text font-bold">{f.primary_metric} = {f.primary_value.toFixed(3)}</span>
                  </div>
                  <div>
                    <span className="text-orbit-muted block">{f.secondary_sensor}:</span>
                    <span className="text-orbit-text font-bold">{f.secondary_metric} = {f.secondary_value.toFixed(3)}</span>
                  </div>
                </div>

                <p className="text-[9px] text-orbit-text leading-relaxed">
                  {f.explanation}
                </p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
