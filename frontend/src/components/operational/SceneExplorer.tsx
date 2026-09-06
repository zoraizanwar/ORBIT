import React, { useState, useEffect } from 'react';
import {
  Satellite,
  Search,
  X,
} from 'lucide-react';
import {
  RankedImageryScene,
  NormalizedImageryScene,
  STACSearchRequest,
} from '../../types/earthObservation';
import { searchAndRankSatelliteScenesApi } from '../../services/eoService';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSelectScene: (scene: NormalizedImageryScene, role: 'T1' | 'T2' | 'VIEW') => void;
  selectedT1Id?: string | null;
  selectedT2Id?: string | null;
}

export const SceneExplorer: React.FC<Props> = ({
  isOpen,
  onClose,
  onSelectScene,
  selectedT1Id,
  selectedT2Id,
}) => {
  const [cloudMax, setCloudMax] = useState<number>(30);
  const [modality, setModality] = useState<string>('ALL');
  const [dateStart] = useState<string>('2021-01-01');
  const [dateEnd] = useState<string>('2026-08-27');
  const [loading, setLoading] = useState<boolean>(false);
  const [rankedScenes, setRankedScenes] = useState<RankedImageryScene[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const fetchRankedScenes = async () => {
    setLoading(true);
    try {
      const req: STACSearchRequest = {
        cloud_cover_max: cloudMax,
        datetime_start: dateStart,
        datetime_end: dateEnd,
        modality: modality === 'ALL' ? undefined : (modality as any),
        limit: 15,
      };
      const res = await searchAndRankSatelliteScenesApi(req);
      setRankedScenes(res.ranked_scenes || []);
    } catch {
      setRankedScenes([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchRankedScenes();
    }
  }, [isOpen, cloudMax, modality]);

  if (!isOpen) return null;

  const filtered = rankedScenes.filter((r) =>
    r.scene.item_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.scene.platform.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div
      className="absolute top-16 left-4 z-30 w-[420px] max-h-[calc(100vh-120px)] bg-orbit-carbon/95 backdrop-blur-md border border-orbit-border rounded-xl shadow-2xl flex flex-col overflow-hidden select-none font-mono text-xs"
      data-testid="scene-explorer"
    >
      {/* Header */}
      <div className="p-3 bg-orbit-slate/60 border-b border-orbit-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-orbit-emerald/10 border border-orbit-emerald/30 text-orbit-emerald">
            <Satellite className="w-4 h-4" />
          </div>
          <div>
            <div className="font-bold text-orbit-text flex items-center gap-2">
              <span>LIVE SCENE EXPLORER</span>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-orbit-emerald/20 text-orbit-emerald border border-orbit-emerald/40 font-bold">
                REAL STAC
              </span>
            </div>
            <p className="text-[10px] text-orbit-muted">Multi-Criteria Deterministic Ranking</p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-orbit-slate text-orbit-muted hover:text-orbit-text transition"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Filter Bar */}
      <div className="p-2.5 bg-orbit-slate/20 border-b border-orbit-border space-y-2">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-orbit-muted" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search Scene ID or Sensor..."
              className="w-full bg-orbit-carbon border border-orbit-border rounded-lg pl-8 pr-2.5 py-1.5 text-orbit-text text-[11px] placeholder:text-orbit-muted focus:outline-none focus:border-orbit-emerald"
            />
          </div>
          <button
            onClick={fetchRankedScenes}
            disabled={loading}
            className="px-3 bg-orbit-emerald/20 hover:bg-orbit-emerald/30 border border-orbit-emerald/40 text-orbit-emerald rounded-lg font-bold text-[10px] transition"
          >
            {loading ? '...' : 'Query'}
          </button>
        </div>

        <div className="grid grid-cols-2 gap-2 text-[10px]">
          <div>
            <label className="text-orbit-muted block mb-1">Max Cloud Cover: {cloudMax}%</label>
            <input
              type="range"
              min="0"
              max="100"
              value={cloudMax}
              onChange={(e) => setCloudMax(Number(e.target.value))}
              className="w-full accent-orbit-emerald h-1"
            />
          </div>

          <div>
            <label className="text-orbit-muted block mb-1">Sensing Modality</label>
            <select
              value={modality}
              onChange={(e) => setModality(e.target.value)}
              className="w-full bg-orbit-carbon border border-orbit-border rounded p-1 text-orbit-text text-[10px]"
            >
              <option value="ALL">All Modalities</option>
              <option value="OPTICAL_MULTISPECTRAL">Optical (Sentinel-2 MSI)</option>
              <option value="SAR_MICROWAVE">SAR (Sentinel-1 C-SAR)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Scene List */}
      <div className="flex-1 overflow-y-auto p-2.5 space-y-2.5">
        {filtered.map((item, idx) => {
          const s = item.scene;
          const isT1 = selectedT1Id === s.item_id;
          const isT2 = selectedT2Id === s.item_id;

          return (
            <div
              key={s.item_id}
              className={`p-2.5 rounded-lg border transition space-y-2 ${
                isT1 || isT2
                  ? 'bg-orbit-emerald/10 border-orbit-emerald/50'
                  : 'bg-orbit-slate/30 border-orbit-border hover:bg-orbit-slate/50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <span className="font-bold text-orbit-emerald text-[11px]">
                    #{idx + 1}
                  </span>
                  <span className="font-bold text-orbit-text text-[11px] truncate max-w-[210px]">
                    {s.platform} ({s.sensor})
                  </span>
                </div>

                <div className="flex items-center gap-1">
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-orbit-emerald/20 text-orbit-emerald font-bold border border-orbit-emerald/40">
                    {(item.rank_score * 100).toFixed(0)}% Match
                  </span>
                  <span className="text-[8px] px-1 rounded bg-orbit-slate text-orbit-muted border border-orbit-border">
                    {item.is_test_fixture ? '[SIMULATED]' : 'REAL DATA'}
                  </span>
                </div>
              </div>

              <div className="text-[9px] text-orbit-muted space-y-0.5">
                <div className="truncate font-mono">{s.item_id}</div>
                <div className="flex justify-between text-orbit-text">
                  <span>Acquired: {s.acquisition_datetime.split('T')[0]}</span>
                  <span>Cloud: {s.cloud_cover !== null ? `${s.cloud_cover}%` : 'N/A (SAR)'}</span>
                  <span>GSD: {s.spatial_resolution}m</span>
                </div>
                <div className="text-[9px] text-orbit-muted truncate">
                  {item.ranking_explanation}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-1.5 pt-1.5 border-t border-orbit-border/60">
                <button
                  onClick={() => onSelectScene(s, 'T1')}
                  className={`flex-1 py-1 rounded text-[10px] font-bold transition border ${
                    isT1
                      ? 'bg-orbit-emerald text-orbit-carbon border-orbit-emerald'
                      : 'bg-orbit-slate/50 text-orbit-text hover:bg-orbit-slate border-orbit-border'
                  }`}
                >
                  {isT1 ? '✓ Selected as T1' : 'Set Baseline (T1)'}
                </button>

                <button
                  onClick={() => onSelectScene(s, 'T2')}
                  className={`flex-1 py-1 rounded text-[10px] font-bold transition border ${
                    isT2
                      ? 'bg-orbit-emerald text-orbit-carbon border-orbit-emerald'
                      : 'bg-orbit-slate/50 text-orbit-text hover:bg-orbit-slate border-orbit-border'
                  }`}
                >
                  {isT2 ? '✓ Selected as T2' : 'Set Current (T2)'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
