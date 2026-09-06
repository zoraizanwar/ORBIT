import React from 'react';
import {
  Globe,
  Bell,
  Sun,
  Moon,
  Database,
  ShieldCheck,
} from 'lucide-react';
import { SearchResultItem } from '../../types/gazetteer';
import { CommandSearch } from '../search/CommandSearch';

interface Props {
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
  onSelectLocation?: (result: SearchResultItem) => void;
}

export const TopCommandBar: React.FC<Props> = ({
  theme,
  onToggleTheme,
  onSelectLocation,
}) => {
  const handleSelect = (item: SearchResultItem) => {
    if (onSelectLocation) {
      onSelectLocation(item);
    }
  };

  return (
    <header
      className="h-14 bg-orbit-carbon border-b border-orbit-border px-4 flex items-center justify-between select-none z-30 relative"
      data-testid="top-command-bar"
    >
      {/* Left: Brand Wordmark & Technical Subtitle */}
      <div className="flex items-center gap-3 shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orbit-emerald to-orbit-sky flex items-center justify-center shadow-glow-emerald">
            <Globe className="w-5 h-5 text-orbit-void stroke-[2.2]" />
          </div>
          <div>
            <div className="flex items-center gap-1.5 leading-none">
              <span className="font-mono font-black text-lg tracking-wider text-orbit-text">
                ORBIT
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-orbit-emerald/10 text-orbit-emerald border border-orbit-emerald/30 font-bold">
                v0.1.0
              </span>
            </div>
            <p className="text-[9px] font-mono tracking-widest text-orbit-muted uppercase mt-0.5">
              GEOSPATIAL INTELLIGENCE
            </p>
          </div>
        </div>

        <div className="h-5 w-px bg-orbit-border mx-2 hidden sm:block" />

        {/* Telemetry Stream Badge */}
        <div className="hidden xl:flex items-center gap-1.5 text-[11px] font-mono text-orbit-muted bg-orbit-slate/50 px-2.5 py-1 rounded border border-orbit-border">
          <span className="w-2 h-2 rounded-full bg-orbit-emerald animate-pulse"></span>
          <span>GAZETTEER: ONLINE</span>
        </div>
      </div>

      {/* Center: Global Command & Gazetteer Search Bar */}
      <div className="flex-1 max-w-xl mx-4">
        <CommandSearch onSelectResult={handleSelect} />
      </div>

      {/* Right: Operational Status, Theme Toggle, User Profile */}
      <div className="flex items-center gap-2 shrink-0">
        {/* PostGIS & Database Status Pill */}
        <div className="hidden md:flex items-center gap-1.5 text-xs font-mono text-orbit-emerald bg-emerald-950/40 border border-orbit-emerald/30 px-2.5 py-1 rounded">
          <Database className="w-3.5 h-3.5" />
          <span>POSTGIS ACTIVE</span>
        </div>

        {/* AI Grounding Status */}
        <div className="hidden lg:flex items-center gap-1.5 text-xs font-mono text-orbit-cyan bg-cyan-950/40 border border-orbit-cyan/30 px-2.5 py-1 rounded">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>AI GROUNDED</span>
        </div>

        {/* Theme Toggle Button */}
        <button
          onClick={onToggleTheme}
          className="p-2 rounded-lg bg-orbit-slate hover:bg-orbit-border text-orbit-muted hover:text-orbit-text border border-orbit-border transition"
          title={`Switch to ${theme === 'dark' ? 'Scientific Light Mode' : 'Tactical Dark Mode'}`}
          aria-label="Toggle Theme"
          data-testid="theme-toggle-btn"
        >
          {theme === 'dark' ? (
            <Sun className="w-4 h-4 text-amber-400" />
          ) : (
            <Moon className="w-4 h-4 text-orbit-sky" />
          )}
        </button>

        {/* Notifications */}
        <button
          className="p-2 rounded-lg bg-orbit-slate hover:bg-orbit-border text-orbit-muted hover:text-orbit-text border border-orbit-border transition relative"
          title="Notifications & Alerts"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-orbit-emerald ring-2 ring-orbit-carbon"></span>
        </button>

        {/* User Account Avatar */}
        <div className="flex items-center gap-2 pl-2 border-l border-orbit-border">
          <div className="w-8 h-8 rounded-lg bg-orbit-slate border border-orbit-emerald/40 flex items-center justify-center text-xs font-mono font-bold text-orbit-emerald">
            ZM
          </div>
          <div className="hidden xl:block text-left">
            <div className="text-xs font-semibold text-orbit-text leading-tight">Zuraiz Malik</div>
            <div className="text-[10px] font-mono text-orbit-muted leading-tight">CHIEF ANALYST</div>
          </div>
        </div>
      </div>
    </header>
  );
};
