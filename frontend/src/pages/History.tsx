import React, { useState } from 'react';
import {
  MOCK_HISTORICAL_SUMMARIES,
  MOCK_GEOLOGICAL_EPOCHS,
  MOCK_ISLAMIC_RECORDS,
} from '../mock/demoData';
import { HistoricalSupportBadge } from '../components/history/HistoricalSupportBadge';
import { IslamicSourceBadge } from '../components/history/IslamicSourceBadge';
import {
  Mountain,
  BookOpen,
  Info,
  Calendar,
} from 'lucide-react';

export const History: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'satellite_archive' | 'deep_geology' | 'islamic_sources'>('satellite_archive');

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full font-sans" data-testid="history-page">
      {/* Header & Sub-Navigation Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-orbit-border/60 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold tracking-widest text-orbit-emerald bg-emerald-950/60 px-2.5 py-1 rounded border border-orbit-emerald/40 uppercase">
              HISTORICAL TIMELINE & ARCHIVES
            </span>
          </div>
          <h1 className="text-xl font-bold text-orbit-text mt-1">
            Historical Satellite Archive & Timeline
          </h1>
          <p className="text-xs text-orbit-muted mt-0.5 max-w-2xl leading-relaxed">
            Look back in time using 50+ years of satellite records to see how forests, water bodies, and settlements evolved across decades.
          </p>
        </div>

        {/* Sub-Tab Navigation */}
        <div className="flex bg-orbit-carbon border border-orbit-border rounded-lg p-1 font-mono text-xs">
          <button
            onClick={() => setActiveSubTab('satellite_archive')}
            className={`px-3 py-1.5 rounded-md transition cursor-pointer ${
              activeSubTab === 'satellite_archive'
                ? 'bg-orbit-emerald text-orbit-void font-bold shadow-sm'
                : 'text-orbit-muted hover:text-orbit-text'
            }`}
          >
            🛰️ Satellite (1972–2026)
          </button>
          <button
            onClick={() => setActiveSubTab('deep_geology')}
            className={`px-3 py-1.5 rounded-md transition cursor-pointer ${
              activeSubTab === 'deep_geology'
                ? 'bg-orbit-emerald text-orbit-void font-bold shadow-sm'
                : 'text-orbit-muted hover:text-orbit-text'
            }`}
          >
            🌍 Geological Time (Ma)
          </button>
          <button
            onClick={() => setActiveSubTab('islamic_sources')}
            className={`px-3 py-1.5 rounded-md transition cursor-pointer ${
              activeSubTab === 'islamic_sources'
                ? 'bg-orbit-emerald text-orbit-void font-bold shadow-sm'
                : 'text-orbit-muted hover:text-orbit-text'
            }`}
          >
            📜 Classical History
          </button>
        </div>
      </div>

      {/* SUB-TAB 1: SATELLITE ARCHIVE */}
      {activeSubTab === 'satellite_archive' && (
        <div className="space-y-6">
          <div className="p-4 bg-orbit-carbon border border-orbit-border rounded-xl flex items-start gap-3 shadow-sm">
            <Info className="w-5 h-5 text-orbit-emerald shrink-0 mt-0.5" />
            <p className="text-xs text-orbit-muted leading-relaxed">
              <strong className="text-orbit-text">How we use historical satellites:</strong> ORBIT references genuine historical passes from NASA Landsat 1–9 (starting in 1972) and ESA Sentinel satellites. This allows us to compare today's deforestation or water levels against pristine baseline records from decades ago.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {MOCK_HISTORICAL_SUMMARIES.map((h) => (
              <div
                key={h.id}
                className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 space-y-3 shadow-sm hover:border-orbit-emerald/40 transition"
              >
                <div className="flex items-center justify-between border-b border-orbit-border/60 pb-2">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-orbit-emerald" />
                    <span className="text-base font-bold text-orbit-text">Year {h.year}</span>
                  </div>
                  <HistoricalSupportBadge classification={h.support_classification} size="sm" />
                </div>

                <div className="space-y-2 text-xs text-orbit-muted">
                  <div className="flex justify-between p-1.5 bg-orbit-slate/30 rounded">
                    <span>Forest & Plant Health (NDVI):</span>
                    <strong className="text-orbit-emerald">{h.summary_data.mean_ndvi ?? 'No Data'}</strong>
                  </div>
                  <div className="flex justify-between p-1.5 bg-orbit-slate/30 rounded">
                    <span>Built-Up Town Area:</span>
                    <strong className="text-orbit-text">{h.summary_data.built_up_km2 ? `${h.summary_data.built_up_km2} km²` : 'N/A'}</strong>
                  </div>
                  <div className="flex justify-between p-1.5 bg-orbit-slate/30 rounded">
                    <span>Archived Passes:</span>
                    <strong className="text-orbit-sky">{h.data_sources.sentinel_scenes_count ?? h.data_sources.landsat_scenes_count ?? 0} photos</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SUB-TAB 2: DEEP GEOLOGY */}
      {activeSubTab === 'deep_geology' && (
        <div className="space-y-6">
          <div className="p-4 bg-orbit-carbon border border-orbit-border rounded-xl flex items-start gap-3 shadow-sm">
            <Mountain className="w-5 h-5 text-orbit-emerald shrink-0 mt-0.5" />
            <p className="text-xs text-orbit-muted leading-relaxed">
              <strong className="text-orbit-text">Geological Earth Time:</strong> Millions of years of natural river basin formation, sediment shifting, and lake cycles that provide natural context for modern changes.
            </p>
          </div>

          <div className="space-y-4">
            {MOCK_GEOLOGICAL_EPOCHS.map((epoch) => (
              <div
                key={epoch.id}
                className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 space-y-3 shadow-sm"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-orbit-border/60 pb-3">
                  <h2 className="text-base font-bold text-orbit-text flex items-center gap-2">
                    <Mountain className="w-4 h-4 text-purple-400 shrink-0" />
                    <span>{epoch.name}</span>
                  </h2>
                  <span className="text-xs font-mono font-bold text-purple-300 bg-purple-950/60 px-2.5 py-1 rounded border border-purple-800">
                    {epoch.start_age} Ma – {epoch.end_age} Ma ({epoch.start_age} Million Years Ago)
                  </span>
                </div>
                <p className="text-xs text-orbit-muted leading-relaxed bg-orbit-slate/20 p-3 rounded-lg border border-orbit-border/40">
                  {epoch.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SUB-TAB 3: ISLAMIC HISTORIOGRAPHY */}
      {activeSubTab === 'islamic_sources' && (
        <div className="space-y-6">
          <div className="p-4 bg-orbit-carbon border border-orbit-border rounded-xl flex items-start gap-3 shadow-sm">
            <BookOpen className="w-5 h-5 text-orbit-emerald shrink-0 mt-0.5" />
            <p className="text-xs text-orbit-muted leading-relaxed">
              <strong className="text-orbit-text">Classical Scholarly Geography:</strong> Historical accounts from renowned classical geographers (e.g. Al-Idrisi, Ibn Battuta) describing watercourses, oasis systems, and trade corridors across centuries.
            </p>
          </div>

          <div className="space-y-4">
            {MOCK_ISLAMIC_RECORDS.map((rec) => (
              <div
                key={rec.id}
                className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 space-y-3 shadow-sm"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-orbit-border/60 pb-3">
                  <div>
                    <span className="text-[10px] font-mono text-orbit-muted uppercase">SCHOLAR / SOURCE: {rec.source}</span>
                    <h2 className="text-base font-bold text-orbit-text mt-0.5">{rec.title}</h2>
                  </div>
                  <IslamicSourceBadge grade={rec.classification} size="sm" />
                </div>
                <p className="text-xs text-orbit-text leading-relaxed bg-orbit-slate/20 p-3 rounded-lg border border-orbit-border/40 italic">
                  "{rec.description}"
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
