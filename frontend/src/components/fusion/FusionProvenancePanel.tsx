import React from 'react';
import {
  Lock,
} from 'lucide-react';

interface Props {
  fusionId: string;
  provenanceHash: string;
  isTestFixture: boolean;
  timestamp: string;
  supportingObservations: string[];
  contradictoryFindings: string[];
}

export const FusionProvenancePanel: React.FC<Props> = ({
  fusionId,
  provenanceHash,
  isTestFixture,
  timestamp,
  supportingObservations,
  contradictoryFindings,
}) => {
  return (
    <div
      className="p-3 bg-orbit-carbon/95 border border-orbit-border rounded-xl font-mono text-xs select-none space-y-2.5 shadow-xl"
      data-testid="fusion-provenance-panel"
    >
      <div className="flex items-center justify-between pb-1.5 border-b border-orbit-border">
        <div className="flex items-center gap-1.5 text-orbit-emerald font-bold text-[11px]">
          <Lock className="w-3.5 h-3.5" />
          <span>CRYPTOGRAPHIC LINEAGE & PROVENANCE</span>
        </div>
        <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold border ${
          isTestFixture
            ? 'bg-amber-500/20 text-amber-400 border-amber-500/40'
            : 'bg-orbit-emerald/20 text-orbit-emerald border-orbit-emerald/40'
        }`}>
          {isTestFixture ? '[SIMULATED]' : 'REAL DATA'}
        </span>
      </div>

      <div className="space-y-1 text-[9px] text-orbit-muted">
        <div>Fusion ID: <span className="text-orbit-text font-mono">{fusionId}</span></div>
        <div>Timestamp: <span className="text-orbit-text">{timestamp}</span></div>
        <div className="truncate">
          SHA-256 Digest: <span className="text-orbit-emerald font-mono font-bold">{provenanceHash}</span>
        </div>
        <div>
          Supporting Observations: <span className="text-orbit-text">{supportingObservations.join(', ') || 'None'}</span>
        </div>
        <div>
          Contradictions Flagged: <span className="text-rose-400">{contradictoryFindings.length}</span>
        </div>
      </div>
    </div>
  );
};
