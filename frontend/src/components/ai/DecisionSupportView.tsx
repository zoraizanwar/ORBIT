import React from 'react';
import { Recommendation } from '../../types/ai';
import { CheckSquare, Search, Eye, AlertOctagon } from 'lucide-react';

interface DecisionSupportViewProps {
  recommendations: Recommendation[];
}

export const DecisionSupportView: React.FC<DecisionSupportViewProps> = ({ recommendations }) => {
  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'HIGH':
        return 'bg-rose-950/70 border-rose-600/70 text-rose-300';
      case 'MEDIUM':
        return 'bg-amber-950/70 border-amber-600/70 text-amber-300';
      case 'LOW':
      default:
        return 'bg-emerald-950/70 border-emerald-600/70 text-emerald-300';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'REVIEW_CONTRADICTION':
        return <AlertOctagon className="w-4 h-4 text-amber-400" />;
      case 'INVESTIGATE':
      case 'PRIORITIZE_SURVEY':
        return <Search className="w-4 h-4 text-cyan-400" />;
      case 'MONITOR':
      default:
        return <Eye className="w-4 h-4 text-emerald-400" />;
    }
  };

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="p-4 text-center text-xs text-slate-400 font-mono">
        No operational recommendations generated.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {recommendations.map((rec) => (
        <div
          key={rec.recommendation_id}
          className="p-3.5 rounded bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition-colors"
        >
          <div className="flex items-center justify-between gap-2 mb-2">
            <div className="flex items-center gap-2">
              {getCategoryIcon(rec.category)}
              <span className="font-mono text-[11px] font-bold uppercase tracking-wider text-slate-300">
                {rec.category}
              </span>
            </div>
            <span
              className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${getPriorityBadge(
                rec.priority
              )}`}
            >
              {rec.priority} PRIORITY
            </span>
          </div>

          <p className="text-xs font-semibold text-slate-100 leading-snug mb-1.5">
            {rec.recommendation_text}
          </p>

          <p className="text-xs text-slate-400 leading-relaxed mb-2">
            <span className="font-mono text-[10px] text-slate-500 font-bold uppercase">Rationale: </span>
            {rec.reason}
          </p>

          {rec.supporting_evidence_ids && rec.supporting_evidence_ids.length > 0 && (
            <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center gap-1.5">
              <span className="text-[10px] font-mono text-slate-500 flex items-center gap-1">
                <CheckSquare className="w-3 h-3 text-cyan-400" />
                GROUNDED IN:
              </span>
              {rec.supporting_evidence_ids.map((eid) => (
                <span
                  key={eid}
                  className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-cyan-300"
                >
                  {eid}
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
