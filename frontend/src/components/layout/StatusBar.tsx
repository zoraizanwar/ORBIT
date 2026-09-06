import React from 'react';
import { Database, Activity, Globe, Server, CheckCircle2, ShieldCheck } from 'lucide-react';

export const StatusBar: React.FC = () => {
  return (
    <footer
      className="h-7 bg-orbit-carbon border-t border-orbit-border px-4 flex items-center justify-between text-[11px] font-mono select-none z-30 shrink-0 text-orbit-muted overflow-x-auto scrollbar-none"
      data-testid="orbit-status-bar"
    >
      {/* Left: Engine & Storage Nodes */}
      <div className="flex items-center gap-4 shrink-0">
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-orbit-emerald animate-pulse"></span>
          <span className="text-orbit-text font-medium">SYSTEM: READY</span>
        </div>

        <div className="flex items-center gap-1.5 text-orbit-muted">
          <Database className="w-3 h-3 text-orbit-emerald" />
          <span>DB: CONNECTED</span>
        </div>

        <div className="flex items-center gap-1.5 text-orbit-muted">
          <Globe className="w-3 h-3 text-orbit-emerald" />
          <span>POSTGIS 3.4: ACTIVE</span>
        </div>

        <div className="flex items-center gap-1.5 text-orbit-muted">
          <Server className="w-3 h-3 text-orbit-sky" />
          <span>REDIS: CONNECTED</span>
        </div>

        <div className="flex items-center gap-1.5 text-orbit-muted">
          <Activity className="w-3 h-3 text-orbit-emerald" />
          <span>ANALYSIS ENGINE: READY</span>
        </div>
      </div>

      {/* Right: Telemetry & AI Grounding state */}
      <div className="flex items-center gap-4 shrink-0 ml-4">
        <div className="flex items-center gap-1.5 text-orbit-muted">
          <CheckCircle2 className="w-3 h-3 text-orbit-emerald" />
          <span>EO DATA: AVAILABLE</span>
        </div>

        <div className="flex items-center gap-1.5 text-orbit-muted">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
          <span>MAP ENGINE: STANDBY (PHASE 5)</span>
        </div>

        <div className="flex items-center gap-1.5 text-orbit-cyan font-medium">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>AI: GROUNDED</span>
        </div>
      </div>
    </footer>
  );
};
