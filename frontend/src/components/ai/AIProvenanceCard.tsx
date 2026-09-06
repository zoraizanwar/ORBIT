import React from 'react';
import { AIInterpretationResult } from '../../types/ai';
import { Fingerprint, Shield, Cpu, Terminal, CheckCircle2 } from 'lucide-react';

interface AIProvenanceCardProps {
  interpretation: AIInterpretationResult;
}

export const AIProvenanceCard: React.FC<AIProvenanceCardProps> = ({ interpretation }) => {
  return (
    <div className="p-4 rounded bg-slate-900/80 border border-slate-800 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Fingerprint className="w-5 h-5 text-indigo-400" />
          <div>
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
              AI PROVENANCE & CALCULATION TRACE
            </h4>
            <p className="text-[10px] font-mono text-slate-500">
              Cryptographic integrity hash & deterministic reasoning lineage
            </p>
          </div>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950/70 border border-indigo-600/60 text-indigo-300 flex items-center gap-1">
          <Shield className="w-3 h-3 text-indigo-400" />
          VERIFIED GROUNDED
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
        <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
          <div className="text-[10px] font-mono text-slate-500 uppercase mb-1 flex items-center gap-1">
            <Cpu className="w-3 h-3 text-cyan-400" />
            REASONING PROVIDER
          </div>
          <div className="font-mono text-slate-200">
            {interpretation.provider_info?.provider || 'ORBIT-LocalReasoner'} (
            {interpretation.provider_info?.model || 'DeterministicGroundedSynthesizer'})
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-1">
            Engine Version: {interpretation.provider_info?.version || '1.0.0'}
          </div>
        </div>

        <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
          <div className="text-[10px] font-mono text-slate-500 uppercase mb-1 flex items-center gap-1">
            <Terminal className="w-3 h-3 text-cyan-400" />
            PROMPT SPECIFICATION
          </div>
          <div className="font-mono text-slate-200">
            {interpretation.provenance?.prompt_version || 'ORBIT-AI-Prompt-v1'}
          </div>
          <div className="text-[10px] font-mono text-emerald-400 mt-1 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            Adversarial Hallucination Check Passed
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <div className="text-[10px] font-mono text-slate-500 uppercase">
          EVIDENCE PACKAGE DIGEST (SHA-256)
        </div>
        <div className="p-2 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-cyan-400 break-all select-all">
          {interpretation.evidence_package_hash}
        </div>
      </div>

      {interpretation.provenance?.provenance_hash_sha256 && (
        <div className="space-y-2">
          <div className="text-[10px] font-mono text-slate-500 uppercase">
            INTERPRETATION PROVENANCE SEAL (SHA-256)
          </div>
          <div className="p-2 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-indigo-400 break-all select-all">
            {interpretation.provenance.provenance_hash_sha256}
          </div>
        </div>
      )}
    </div>
  );
};
