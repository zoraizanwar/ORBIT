import React from 'react';
import { Claim, SupportStatus } from '../../types/ai';
import { CheckCircle2, AlertCircle, XCircle, Link as LinkIcon, ShieldCheck } from 'lucide-react';

interface ClaimListProps {
  claims: Claim[];
  onSelectEvidenceId?: (evidenceId: string) => void;
}

export const ClaimList: React.FC<ClaimListProps> = ({ claims, onSelectEvidenceId }) => {
  const getStatusIcon = (status: SupportStatus) => {
    switch (status) {
      case 'SUPPORTED':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      case 'CONTRADICTED':
        return <AlertCircle className="w-4 h-4 text-amber-400" />;
      case 'UNSUPPORTED':
      case 'PARTIALLY_SUPPORTED':
      default:
        return <XCircle className="w-4 h-4 text-rose-400" />;
    }
  };

  const getStatusBadge = (status: SupportStatus) => {
    switch (status) {
      case 'SUPPORTED':
        return 'bg-emerald-950/60 border-emerald-600/60 text-emerald-300';
      case 'CONTRADICTED':
        return 'bg-amber-950/60 border-amber-600/60 text-amber-300';
      case 'UNSUPPORTED':
      case 'PARTIALLY_SUPPORTED':
      default:
        return 'bg-rose-950/60 border-rose-600/60 text-rose-300';
    }
  };

  if (!claims || claims.length === 0) {
    return (
      <div className="p-4 text-center text-xs text-slate-400 font-mono">
        No claims available.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {claims.map((claim) => (
        <div
          key={claim.claim_id}
          className="p-3.5 rounded bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition-colors"
        >
          {/* Header */}
          <div className="flex items-center justify-between gap-2 mb-2">
            <div className="flex items-center gap-2">
              {getStatusIcon(claim.support_status)}
              <span className="font-mono text-[11px] font-bold uppercase tracking-wider text-slate-300">
                {claim.claim_type}
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-950/70 border border-indigo-600/50 text-indigo-300">
                AI_INTERPRETED
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span
                className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${getStatusBadge(
                  claim.support_status
                )}`}
              >
                {claim.support_status}
              </span>
              <span className="text-[10px] font-mono text-slate-400">
                {Math.round(claim.confidence * 100)}% Conf
              </span>
            </div>
          </div>

          {/* Claim Text */}
          <p className="text-xs text-slate-200 leading-relaxed mb-3">
            {claim.claim_text}
          </p>

          {/* Evidence Citations */}
          {claim.evidence_ids && claim.evidence_ids.length > 0 && (
            <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center gap-1.5">
              <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1 mr-1">
                <LinkIcon className="w-3 h-3 text-cyan-400" />
                CITED EVIDENCE:
              </span>
              {claim.evidence_ids.map((eid) => (
                <button
                  key={eid}
                  onClick={() => onSelectEvidenceId && onSelectEvidenceId(eid)}
                  className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950/40 border border-cyan-700/50 text-cyan-300 hover:bg-cyan-900/50 transition-colors flex items-center gap-1"
                >
                  <ShieldCheck className="w-2.5 h-2.5 text-cyan-400" />
                  {eid}
                </button>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
