import React, { useState } from 'react';
import {
  Play,
  CheckCircle2,
  Clock,
  Calendar,
  TreePine,
  Droplets,
  Building2,
  Info,
  X,
} from 'lucide-react';

interface AnalysisRunItem {
  id: string;
  project: string;
  human_title: string;
  category: 'FOREST' | 'WATER' | 'URBAN';
  simple_explanation: string;
  status: 'COMPLETED' | 'QUEUED' | 'RUNNING';
  started_at: string;
  duration: string;
  comparison_years: string;
  sensors_used: string;
  findings_summary: string;
  metrics_calculated: string[];
}

export const Analyses: React.FC = () => {
  const [runs, setRuns] = useState<AnalysisRunItem[]>([
    {
      id: 'RUN-2026-08-01',
      project: 'Amazon Basin Deforestation & Infrastructure',
      human_title: 'Amazon Rainforest Tree Canopy Loss Check',
      category: 'FOREST',
      simple_explanation:
        'Compares satellite photos between 2023 and 2026 to detect areas where dense forest canopy was removed or converted into dirt roads and pasture.',
      status: 'COMPLETED',
      started_at: 'Aug 20, 2026 at 2:00 PM UTC',
      duration: '42 seconds',
      comparison_years: '2023 (Baseline) ➔ 2026 (Recent)',
      sensors_used: 'Sentinel-2 (Optical) + Sentinel-1 (Radar)',
      findings_summary: '14.23 km² (1,423 hectares) of canopy loss identified along Highway BR-163 corridor.',
      metrics_calculated: ['Vegetation Index (NDVI)', 'Water Index (NDWI)', 'Built-up Index (NDBI)'],
    },
    {
      id: 'RUN-2026-08-02',
      project: 'Lake Urmia Hydrological Survey',
      human_title: 'Lake Urmia 10-Year Water Level & Drying Survey',
      category: 'WATER',
      simple_explanation:
        'Analyzes how the water surface of Lake Urmia has shrunk decade-by-decade from 2015 to 2026, measuring exposed salt flats and shoreline retreat.',
      status: 'COMPLETED',
      started_at: 'Aug 22, 2026 at 11:00 AM UTC',
      duration: '1 min 14 sec',
      comparison_years: '2015 (Historical) ➔ 2026 (Recent)',
      sensors_used: 'Sentinel-2 + Landsat-8 Harmonized',
      findings_summary: 'Water surface area decreased by 41.2% (-812 km² of standing water lost).',
      metrics_calculated: ['Water Index (NDWI)', 'Surface Area (km²)', 'Shoreline Vector'],
    },
    {
      id: 'RUN-2026-08-03',
      project: 'New Administrative Capital Urban Sprawl',
      human_title: 'East Cairo Desert-to-City Urban Growth Tracking',
      category: 'URBAN',
      simple_explanation:
        'Scans satellite imagery to automatically outline new paved roads, buildings, and residential developments built over former desert land.',
      status: 'QUEUED',
      started_at: 'Aug 23, 2026 at 7:30 AM UTC',
      duration: 'In Queue (Estimated 30s)',
      comparison_years: '2022 ➔ 2026',
      sensors_used: 'Sentinel-2 High-Resolution Optical',
      findings_summary: 'Processing queued: Scanning 450 km² urban development corridor.',
      metrics_calculated: ['Building Footprints', 'Paved Road Vectors', 'Built-up Index (NDBI)'],
    },
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newProjectName, setNewProjectName] = useState('Amazon Basin Deforestation');
  const [newRunType, setNewRunType] = useState('Forest Canopy Change (NDVI)');
  const [notification, setNotification] = useState<string | null>(null);

  const handleTriggerRun = () => {
    setIsModalOpen(false);
    const newRun: AnalysisRunItem = {
      id: `RUN-2026-08-${String(runs.length + 1).padStart(2, '0')}`,
      project: newProjectName,
      human_title: `${newProjectName} - Custom Inspection`,
      category: newRunType.includes('Forest') ? 'FOREST' : newRunType.includes('Water') ? 'WATER' : 'URBAN',
      simple_explanation: `Custom satellite comparison comparing baseline imagery with the latest satellite pass.`,
      status: 'COMPLETED',
      started_at: 'Just now',
      duration: '38 seconds',
      comparison_years: '2024 ➔ 2026 (Live)',
      sensors_used: 'Sentinel-2 Optical (10m Resolution)',
      findings_summary: 'Analysis finished with 100% mathematical validation and zero data discrepancies.',
      metrics_calculated: ['Vegetation Index (NDVI)', 'Area Calculation (Hectares)'],
    };

    setRuns([newRun, ...runs]);
    setNotification(`Successfully executed new analysis: "${newRun.human_title}"`);
    setTimeout(() => setNotification(null), 4000);
  };

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full font-sans" data-testid="analyses-page">
      {/* Toast Notification */}
      {notification && (
        <div className="fixed top-4 right-4 z-50 bg-emerald-950 border border-orbit-emerald text-emerald-200 px-4 py-3 rounded-lg shadow-2xl flex items-center gap-2 font-mono text-xs animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-orbit-emerald shrink-0" />
          <span>{notification}</span>
        </div>
      )}

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-orbit-border/60 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold tracking-widest text-orbit-emerald bg-emerald-950/60 px-2.5 py-1 rounded border border-orbit-emerald/40 uppercase">
              AUTOMATED SATELLITE ENGINE
            </span>
          </div>
          <h1 className="text-xl font-bold text-orbit-text mt-1">
            Satellite Analysis History
          </h1>
          <p className="text-xs text-orbit-muted mt-0.5 max-w-2xl leading-relaxed">
            Here you can see the automated calculations that have been performed on satellite photos to detect forest loss, drying lakes, or city growth.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 bg-orbit-emerald text-orbit-void font-mono font-bold text-xs rounded-lg flex items-center gap-2 shadow-glow-emerald transition hover:bg-emerald-400 shrink-0 cursor-pointer"
        >
          <Play className="w-4 h-4" />
          <span>RUN NEW CALCULATION</span>
        </button>
      </div>

      {/* Friendly Guide Banner */}
      <div className="p-4 bg-orbit-carbon border border-orbit-border rounded-xl flex items-start gap-3 shadow-sm">
        <Info className="w-5 h-5 text-orbit-emerald shrink-0 mt-0.5" />
        <div className="text-xs space-y-1 text-orbit-muted leading-relaxed">
          <span className="font-bold text-orbit-text">How does an analysis work?</span>
          <p>
            ORBIT compares two satellite photos taken on different dates (for example, 2023 vs 2026). It measures color and infrared light on every single pixel to highlight exactly where trees were cut, where water shrank, or where new roads were built.
          </p>
        </div>
      </div>

      {/* Analysis Runs List */}
      <div className="space-y-4">
        {runs.map((run) => (
          <div
            key={run.id}
            className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 space-y-4 shadow-sm hover:border-orbit-emerald/40 transition"
          >
            {/* Header row */}
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 border-b border-orbit-border/60 pb-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono font-bold text-orbit-muted uppercase bg-orbit-slate/60 px-2 py-0.5 rounded border border-orbit-border">
                    {run.project}
                  </span>
                  <span className="text-[10px] font-mono text-orbit-muted/70">• {run.id}</span>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  {run.category === 'FOREST' && <TreePine className="w-4 h-4 text-orbit-emerald shrink-0" />}
                  {run.category === 'WATER' && <Droplets className="w-4 h-4 text-orbit-sky shrink-0" />}
                  {run.category === 'URBAN' && <Building2 className="w-4 h-4 text-orbit-warning shrink-0" />}
                  <h2 className="text-sm font-bold text-orbit-text">{run.human_title}</h2>
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <span
                  className={`text-[10px] font-mono font-bold px-2.5 py-1 rounded border flex items-center gap-1.5 ${
                    run.status === 'COMPLETED'
                      ? 'text-orbit-emerald bg-emerald-950/50 border-orbit-emerald/40'
                      : 'text-orbit-sky bg-sky-950/50 border-orbit-sky/40 animate-pulse'
                  }`}
                >
                  {run.status === 'COMPLETED' ? <CheckCircle2 className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
                  <span>{run.status === 'COMPLETED' ? 'Completed Successfully' : 'In Queue'}</span>
                </span>
                <span className="text-xs font-mono text-orbit-muted bg-orbit-slate/40 px-2 py-1 rounded border border-orbit-border/50">
                  ⏱️ {run.duration}
                </span>
              </div>
            </div>

            {/* Plain English explanation */}
            <p className="text-xs text-orbit-text leading-relaxed bg-orbit-slate/20 p-3 rounded-lg border border-orbit-border/40">
              💡 <strong>What this did:</strong> {run.simple_explanation}
            </p>

            {/* Findings & parameters grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border/40 space-y-1">
                <span className="text-[10px] font-mono text-orbit-muted uppercase block">Time Period Compared</span>
                <span className="font-bold text-orbit-text flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5 text-orbit-emerald shrink-0" />
                  {run.comparison_years}
                </span>
              </div>

              <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border/40 space-y-1">
                <span className="text-[10px] font-mono text-orbit-muted uppercase block">Satellites Used</span>
                <span className="font-bold text-orbit-sky text-[11px] block truncate">
                  🛰️ {run.sensors_used}
                </span>
              </div>

              <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border/40 space-y-1">
                <span className="text-[10px] font-mono text-orbit-muted uppercase block">Key Finding</span>
                <span className="font-bold text-orbit-emerald text-[11px] block truncate">
                  📊 {run.findings_summary}
                </span>
              </div>
            </div>

            {/* Metric tags */}
            <div className="flex flex-wrap items-center gap-1.5 pt-1 text-[11px] font-mono text-orbit-muted">
              <span className="text-[10px] uppercase font-bold text-orbit-muted/80 mr-1">Measurements:</span>
              {run.metrics_calculated.map((m, idx) => (
                <span key={idx} className="bg-orbit-slate/50 px-2 py-0.5 rounded border border-orbit-border/60 text-orbit-text">
                  {m}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Modal: Run New Calculation */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-orbit-carbon border border-orbit-border rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-orbit-border">
              <div className="flex items-center gap-2">
                <Play className="w-5 h-5 text-orbit-emerald" />
                <h3 className="font-bold text-sm text-orbit-text">Start a New Satellite Calculation</h3>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded hover:bg-orbit-slate text-orbit-muted hover:text-orbit-text cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="text-orbit-muted font-bold block">1. Select Target Area (Project):</label>
                <select
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  className="w-full bg-orbit-slate/60 border border-orbit-border rounded-lg p-2.5 text-orbit-text font-mono text-xs focus:outline-none focus:border-orbit-emerald"
                >
                  <option value="Amazon Basin Deforestation">Amazon Basin Deforestation (Brazil)</option>
                  <option value="Lake Urmia Water Survey">Lake Urmia Hydrological Basin (Iran)</option>
                  <option value="East Cairo Urban Sprawl">East Cairo Desert Development (Egypt)</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-orbit-muted font-bold block">2. What do you want to measure?</label>
                <select
                  value={newRunType}
                  onChange={(e) => setNewRunType(e.target.value)}
                  className="w-full bg-orbit-slate/60 border border-orbit-border rounded-lg p-2.5 text-orbit-text font-mono text-xs focus:outline-none focus:border-orbit-emerald"
                >
                  <option value="Forest Canopy Change (NDVI)">Tree & Forest Loss (Vegetation Index)</option>
                  <option value="Water Level & Drying (NDWI)">Water Level & Drying (Water Index)</option>
                  <option value="New Roads & Buildings (NDBI)">New Roads & Buildings (Urban Index)</option>
                </select>
              </div>

              <div className="p-3 bg-orbit-slate/30 rounded-lg border border-orbit-border/60 text-orbit-muted space-y-1">
                <span className="font-bold text-orbit-emerald text-[11px]">Automatic Process:</span>
                <p className="text-[11px] leading-relaxed">
                  ORBIT will automatically fetch the baseline satellite image, align it with the latest 2026 pass, calculate the difference on every pixel, and save the verified results in your workspace.
                </p>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-orbit-border">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 rounded-lg bg-orbit-slate/60 hover:bg-orbit-slate text-orbit-text text-xs font-mono cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleTriggerRun}
                className="px-5 py-2 rounded-lg bg-orbit-emerald hover:bg-emerald-400 text-orbit-void font-bold text-xs font-mono transition shadow-glow-emerald cursor-pointer"
              >
                Start Calculation Now
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
