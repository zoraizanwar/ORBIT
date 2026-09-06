import React, { useState, useEffect } from 'react';
import {
  Satellite,
  Cloud,
  Calendar,
  Loader2,
  CheckCircle2,
  X,
} from 'lucide-react';
import { NormalizedImageryScene, SensingModality } from '../../types/earthObservation';
import { searchSatelliteScenesApi } from '../../services/eoService';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSelectScene: (scene: NormalizedImageryScene) => void;
  selectedSceneId?: string | null;
}

export const ImageryDiscoveryPanel: React.FC<Props> = ({
  isOpen,
  onClose,
  onSelectScene,
  selectedSceneId,
}) => {
  const [modality, setModality] = useState<string>('ALL');
  const [cloudCoverMax, setCloudCoverMax] = useState<number>(30);
  const [loading, setLoading] = useState<boolean>(false);
  const [scenes, setScenes] = useState<NormalizedImageryScene[]>([]);
  const [totalMatched, setTotalMatched] = useState<number>(0);

  const fetchScenes = async () => {
    setLoading(true);
    try {
      const resp = await searchSatelliteScenesApi({
        modality: modality === 'ALL' ? undefined : (modality as SensingModality),
        cloud_cover_max: modality === 'SAR_MICROWAVE' ? undefined : cloudCoverMax,
        limit: 10,
      });
      setScenes(resp.scenes || []);
      setTotalMatched(resp.total_matched || 0);
    } catch {
      setScenes([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchScenes();
    }
  }, [isOpen, modality, cloudCoverMax]);

  if (!isOpen) return null;

  return (
    <div
      className="absolute top-16 left-4 z-20 w-96 max-h-[calc(100vh-140px)] bg-orbit-carbon/95 backdrop-blur-md border border-orbit-border rounded-xl shadow-2xl flex flex-col overflow-hidden select-none font-mono text-xs"
      data-testid="imagery-discovery-panel"
    >
      {/* 1. Header */}
      <div className="p-3 bg-orbit-slate/60 border-b border-orbit-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-orbit-emerald/10 border border-orbit-emerald/30 text-orbit-emerald">
            <Satellite className="w-4 h-4" />
          </div>
          <div>
            <div className="font-bold text-orbit-text flex items-center gap-1.5">
              <span>EARTH OBSERVATION STAC</span>
              <span className="text-[9px] px-1 rounded bg-orbit-emerald/20 text-orbit-emerald border border-orbit-emerald/40 font-bold">
                OBSERVED
              </span>
            </div>
            <p className="text-[10px] text-orbit-muted">Telemetry & Scene Discovery</p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-orbit-slate text-orbit-muted hover:text-orbit-text transition"
          title="Close Panel"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* 2. Filters & Controls */}
      <div className="p-3 border-b border-orbit-border space-y-3 bg-orbit-slate/20">
        {/* Modality Selector */}
        <div>
          <label className="text-[10px] font-bold text-orbit-muted uppercase tracking-wider block mb-1.5">
            Sensing Modality
          </label>
          <div className="grid grid-cols-3 gap-1 bg-orbit-slate/80 p-1 rounded-lg border border-orbit-border">
            {[
              { key: 'ALL', label: 'All Sensors' },
              { key: 'OPTICAL_MULTISPECTRAL', label: 'Optical (MSI)' },
              { key: 'SAR_MICROWAVE', label: 'SAR (C-Band)' },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setModality(tab.key)}
                className={`py-1 px-1.5 text-[10px] rounded font-medium transition ${
                  modality === tab.key
                    ? 'bg-orbit-emerald text-orbit-void font-bold shadow'
                    : 'text-orbit-muted hover:text-orbit-text'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Cloud Cover Slider (Optical only) */}
        {modality !== 'SAR_MICROWAVE' && (
          <div>
            <div className="flex items-center justify-between text-[10px] text-orbit-muted mb-1">
              <span className="flex items-center gap-1">
                <Cloud className="w-3 h-3 text-orbit-cyan" />
                <span>Max Cloud Cover:</span>
              </span>
              <span className="font-bold text-orbit-cyan">{cloudCoverMax}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={cloudCoverMax}
              onChange={(e) => setCloudCoverMax(Number(e.target.value))}
              className="w-full h-1 bg-orbit-slate rounded-lg appearance-none cursor-pointer accent-orbit-cyan"
            />
          </div>
        )}
      </div>

      {/* 3. Discovered Scenes List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2 divide-y divide-orbit-border/30">
        {loading ? (
          <div className="p-8 text-center text-orbit-muted space-y-2">
            <Loader2 className="w-6 h-6 animate-spin text-orbit-emerald mx-auto" />
            <p className="text-xs">Querying Open STAC Catalogs...</p>
          </div>
        ) : scenes.length === 0 ? (
          <div className="p-6 text-center text-orbit-muted space-y-1">
            <p className="font-semibold text-orbit-text">No satellite scenes match criteria</p>
            <p className="text-[10px]">Try expanding the temporal range or increasing max cloud cover.</p>
          </div>
        ) : (
          scenes.map((scene) => {
            const isSelected = selectedSceneId === scene.item_id;
            const isSAR = scene.modality === 'SAR_MICROWAVE';

            return (
              <div
                key={scene.item_id}
                onClick={() => onSelectScene(scene)}
                className={`p-2.5 rounded-lg border transition cursor-pointer pt-3 ${
                  isSelected
                    ? 'bg-orbit-emerald/15 border-orbit-emerald shadow-glow-emerald'
                    : 'bg-orbit-slate/40 hover:bg-orbit-slate/80 border-orbit-border hover:border-orbit-emerald/40'
                }`}
              >
                {/* Top Row: Sensor Badge + Modality */}
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-1.5">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-bold border ${
                        isSAR
                          ? 'bg-purple-950/40 text-purple-400 border-purple-800/40'
                          : 'bg-emerald-950/40 text-orbit-emerald border-orbit-emerald/40'
                      }`}
                    >
                      {scene.platform} ({scene.sensor})
                    </span>
                    <span className="text-[10px] text-orbit-muted font-semibold">
                      {scene.spatial_resolution}m GSD
                    </span>
                  </div>

                  {scene.cloud_cover !== null && scene.cloud_cover !== undefined ? (
                    <span className="text-[10px] text-orbit-cyan font-bold flex items-center gap-0.5">
                      <Cloud className="w-2.5 h-2.5" />
                      {scene.cloud_cover.toFixed(1)}%
                    </span>
                  ) : (
                    <span className="text-[9px] text-purple-400 font-bold">ALL-WEATHER SAR</span>
                  )}
                </div>

                {/* Date & Processing Level */}
                <div className="text-[11px] text-orbit-text font-bold leading-tight mb-1 truncate">
                  {scene.item_id}
                </div>
                <div className="flex items-center justify-between text-[10px] text-orbit-muted mb-2">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3 text-orbit-muted" />
                    {new Date(scene.acquisition_datetime).toLocaleDateString()}
                  </span>
                  <span>{scene.processing_level}</span>
                </div>

                {/* Footer Attribution Notice */}
                <div className="text-[9px] text-orbit-muted/80 truncate border-t border-orbit-border/40 pt-1.5 flex items-center justify-between">
                  <span>{scene.attribution}</span>
                  {isSelected && (
                    <span className="text-orbit-emerald font-bold flex items-center gap-0.5 shrink-0">
                      <CheckCircle2 className="w-3 h-3" /> ACTIVE
                    </span>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* 4. Footer Status */}
      <div className="p-2.5 bg-orbit-slate/60 border-t border-orbit-border flex items-center justify-between text-[10px] text-orbit-muted">
        <span>{totalMatched} Scenes Discovered</span>
        <span>EPSG:4326 Footprints</span>
      </div>
    </div>
  );
};
