import React from 'react';
import { NavigationSection } from '../../types';
import {
  LayoutDashboard,
  Map as MapIcon,
  FolderKanban,
  Activity,
  Layers,
  Milestone,
  Trees,
  AlertOctagon,
  ShieldAlert,
  Clock,
  History as HistoryIcon,
  Mountain,
  BookOpen,
  TrendingUp,
  Sliders,
  FileText,
  Download,
  Database,
  HeartPulse,
  Settings,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

interface Props {
  activeSection: NavigationSection;
  onSelectSection: (section: NavigationSection) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<Props> = ({
  activeSection,
  onSelectSection,
  isCollapsed,
  onToggleCollapse,
}) => {
  const navGroups = [
    {
      group: 'MISSION',
      items: [
        { id: 'overview' as NavigationSection, label: 'Overview', icon: LayoutDashboard },
        { id: 'map' as NavigationSection, label: 'Map Workspace', icon: MapIcon },
        { id: 'projects' as NavigationSection, label: 'Projects', icon: FolderKanban },
        { id: 'analyses' as NavigationSection, label: 'Analyses', icon: Activity },
      ],
    },
    {
      group: 'INTELLIGENCE',
      items: [
        { id: 'changes' as NavigationSection, label: 'Changes', icon: Layers },
        { id: 'infrastructure' as NavigationSection, label: 'Infrastructure', icon: Milestone },
        { id: 'environment' as NavigationSection, label: 'Environment', icon: Trees },
        { id: 'events' as NavigationSection, label: 'Events', icon: AlertOctagon },
        { id: 'evidence' as NavigationSection, label: 'Evidence DAG', icon: ShieldAlert },
      ],
    },
    {
      group: 'HISTORY',
      items: [
        { id: 'timeline' as NavigationSection, label: 'Timeline', icon: Clock },
        { id: 'history' as NavigationSection, label: 'Historical Data', icon: HistoryIcon },
        { id: 'deep_history' as NavigationSection, label: 'Deep History', icon: Mountain },
        { id: 'islamic_sources' as NavigationSection, label: 'Islamic Sources', icon: BookOpen },
      ],
    },
    {
      group: 'FORECAST',
      items: [
        { id: 'predictions' as NavigationSection, label: 'Predictions', icon: TrendingUp },
        { id: 'scenarios' as NavigationSection, label: 'Scenarios', icon: Sliders },
      ],
    },
    {
      group: 'REPORTING',
      items: [
        { id: 'reports' as NavigationSection, label: 'Reports', icon: FileText },
        { id: 'exports' as NavigationSection, label: 'Exports', icon: Download },
      ],
    },
    {
      group: 'SYSTEM',
      items: [
        { id: 'datasets' as NavigationSection, label: 'Datasets Registry', icon: Database },
        { id: 'health' as NavigationSection, label: 'System Health', icon: HeartPulse },
        { id: 'settings' as NavigationSection, label: 'Settings', icon: Settings },
      ],
    },
  ];

  return (
    <aside
      className={`bg-orbit-carbon border-r border-orbit-border flex flex-col justify-between transition-all duration-200 select-none z-20 shrink-0 ${
        isCollapsed ? 'w-16' : 'w-60'
      }`}
      data-testid="orbit-sidebar"
    >
      {/* Scrollable Navigation Items */}
      <div className="flex-1 overflow-y-auto py-3 px-2 space-y-4 scrollbar-thin">
        {navGroups.map((g) => (
          <div key={g.group} className="space-y-1">
            {!isCollapsed && (
              <div className="text-[10px] font-mono font-bold tracking-widest text-orbit-muted/70 px-2.5 py-1 uppercase">
                {g.group}
              </div>
            )}
            {g.items.map((item) => {
              const Icon = item.icon;
              const isActive = activeSection === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectSection(item.id)}
                  title={isCollapsed ? item.label : undefined}
                  data-testid={`nav-item-${item.id}`}
                  className={`w-full flex items-center gap-3 px-2.5 py-2 rounded-lg text-xs font-mono transition group ${
                    isActive
                      ? 'bg-orbit-emerald/15 text-orbit-emerald font-semibold border border-orbit-emerald/30 shadow-sm'
                      : 'text-orbit-muted hover:text-orbit-text hover:bg-orbit-slate/60'
                  } ${isCollapsed ? 'justify-center' : ''}`}
                >
                  <Icon
                    className={`w-4 h-4 shrink-0 transition ${
                      isActive ? 'text-orbit-emerald' : 'text-orbit-muted group-hover:text-orbit-text'
                    }`}
                  />
                  {!isCollapsed && <span className="truncate">{item.label}</span>}
                </button>
              );
            })}
          </div>
        ))}
      </div>

      {/* Sidebar Footer / Collapse Toggle Button */}
      <div className="p-2 border-t border-orbit-border bg-orbit-slate/30">
        <button
          onClick={onToggleCollapse}
          className="w-full flex items-center justify-center p-2 rounded-lg text-orbit-muted hover:text-orbit-text hover:bg-orbit-slate transition text-xs font-mono border border-orbit-border/40"
          title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          data-testid="sidebar-toggle-btn"
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          {!isCollapsed && <span className="ml-2">COLLAPSE</span>}
        </button>
      </div>
    </aside>
  );
};
