import React from 'react';
import { AlertTriangle, ShieldAlert } from 'lucide-react';

interface ContradictionBannerProps {
  hasContradictions: boolean;
  contradictionStatement?: string;
  contradictionCount?: number;
}

export const ContradictionBanner: React.FC<ContradictionBannerProps> = ({
  hasContradictions,
  contradictionStatement,
  contradictionCount = 1,
}) => {
  if (!hasContradictions && !contradictionStatement) {
    return null;
  }

  return (
    <div className="bg-amber-950/40 border-2 border-amber-600/80 rounded p-3 mb-4 text-amber-200">
      <div className="flex items-center gap-2 mb-1.5 font-mono text-xs uppercase tracking-wider text-amber-400 font-bold">
        <AlertTriangle className="w-4 h-4 text-amber-400 animate-pulse" />
        <span>CONTRADICTORY EVIDENCE DETECTED ({contradictionCount} CONFLICT{contradictionCount > 1 ? 'S' : ''})</span>
      </div>
      <p className="text-xs text-amber-200/90 leading-relaxed font-sans">
        {contradictionStatement ||
          'Cross-sensor discrepancy detected: Optical canopy deficit is not independently corroborated by radar backscatter amplitude. Overall evidence strength is strictly downgraded to INSUFFICIENT.'}
      </p>
      <div className="mt-2 pt-2 border-t border-amber-700/40 flex items-center gap-2 text-[10px] font-mono text-amber-300/80">
        <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
        <span>ORBIT Anti-Fabrication Rule: Conflicting observations must never be reconciled or smoothed by AI.</span>
      </div>
    </div>
  );
};
