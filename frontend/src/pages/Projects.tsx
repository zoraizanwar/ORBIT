import React, { useState } from 'react';
import { MOCK_PROJECTS, MOCK_AOI } from '../mock/demoData';
import { Plus, MapPin, Calendar, ArrowUpRight, Globe, X, CheckCircle2 } from 'lucide-react';

interface Props {
  onSelectProject: (projectId: string) => void;
}

export const Projects: React.FC<Props> = ({ onSelectProject }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [notification, setNotification] = useState<string | null>(null);

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setIsModalOpen(false);
    setNotification(`Created new investigation workspace: "${newTitle}"`);
    setTimeout(() => setNotification(null), 4000);
    setNewTitle('');
    setNewDesc('');
  };

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full font-sans" data-testid="projects-page">
      {/* Toast Notification */}
      {notification && (
        <div className="fixed top-4 right-4 z-50 bg-emerald-950 border border-orbit-emerald text-emerald-200 px-4 py-3 rounded-lg shadow-2xl flex items-center gap-2 font-mono text-xs animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-orbit-emerald shrink-0" />
          <span>{notification}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-orbit-border/60 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold tracking-widest text-orbit-emerald bg-emerald-950/60 px-2.5 py-1 rounded border border-orbit-emerald/40 uppercase">
              MONITORED REGIONS & AREAS
            </span>
          </div>
          <h1 className="text-xl font-bold text-orbit-text mt-1">
            Investigation Workspaces & Target Areas
          </h1>
          <p className="text-xs text-orbit-muted mt-0.5 max-w-2xl leading-relaxed">
            Select a monitored project area to explore its live satellite imagery, road networks, forest loss alerts, and water surveys.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 bg-orbit-emerald text-orbit-void font-mono font-bold text-xs rounded-lg flex items-center gap-1.5 shadow-glow-emerald transition hover:bg-emerald-400 shrink-0 cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>NEW TARGET REGION</span>
        </button>
      </div>

      {/* Friendly Guide */}
      <div className="p-4 bg-orbit-carbon border border-orbit-border rounded-xl flex items-start gap-3 shadow-sm">
        <Globe className="w-5 h-5 text-orbit-emerald shrink-0 mt-0.5" />
        <div className="text-xs space-y-1 text-orbit-muted leading-relaxed">
          <span className="font-bold text-orbit-text">What is an Investigation Workspace?</span>
          <p>
            An investigation workspace is a designated zone on Earth (like the Amazon rainforest or Lake Urmia) that ORBIT monitors continuously from space. Clicking on any project card will open its interactive satellite map with all detected alerts.
          </p>
        </div>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {MOCK_PROJECTS.map((project) => (
          <div
            key={project.id}
            onClick={() => onSelectProject(project.id)}
            className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 shadow-sm hover:border-orbit-emerald/50 transition cursor-pointer flex flex-col justify-between group"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold text-orbit-emerald bg-emerald-950/40 px-2 py-0.5 rounded border border-orbit-emerald/30 uppercase">
                  ● ACTIVE MONITORING
                </span>
                <span className="text-[10px] font-mono text-orbit-muted flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {new Date(project.created_at).toLocaleDateString()}
                </span>
              </div>

              <h2 className="text-base font-bold text-orbit-text group-hover:text-orbit-emerald transition">
                {project.name}
              </h2>
              <p className="text-xs text-orbit-muted leading-relaxed font-normal">
                {project.description}
              </p>
            </div>

            <div className="mt-4 pt-4 border-t border-orbit-border/60 flex items-center justify-between text-xs font-mono">
              <div className="flex items-center gap-1 text-orbit-muted">
                <MapPin className="w-3.5 h-3.5 text-orbit-sky shrink-0" />
                <span className="truncate">Area: {MOCK_AOI.name.split('(')[0]}</span>
              </div>
              <span className="flex items-center gap-1 text-orbit-emerald font-bold group-hover:underline text-[11px]">
                <span>OPEN MAP</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Modal: New Investigation */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-orbit-carbon border border-orbit-border rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-orbit-border">
              <div className="flex items-center gap-2">
                <Plus className="w-5 h-5 text-orbit-emerald" />
                <h3 className="font-bold text-sm text-orbit-text">Define New Target Region</h3>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded hover:bg-orbit-slate text-orbit-muted hover:text-orbit-text cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="text-orbit-muted font-bold block">Region Name:</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Congo Basin River Corridor"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full bg-orbit-slate/60 border border-orbit-border rounded-lg p-2.5 text-orbit-text text-xs focus:outline-none focus:border-orbit-emerald"
                />
              </div>

              <div className="space-y-1">
                <label className="text-orbit-muted font-bold block">Description & Objectives:</label>
                <textarea
                  rows={3}
                  placeholder="e.g. Monitoring illegal logging tracks and seasonal wetland flooding."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="w-full bg-orbit-slate/60 border border-orbit-border rounded-lg p-2.5 text-orbit-text text-xs focus:outline-none focus:border-orbit-emerald resize-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-orbit-border">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-lg bg-orbit-slate/60 hover:bg-orbit-slate text-orbit-text text-xs cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-lg bg-orbit-emerald hover:bg-emerald-400 text-orbit-void font-bold text-xs transition shadow-glow-emerald cursor-pointer"
                >
                  Create Region
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
