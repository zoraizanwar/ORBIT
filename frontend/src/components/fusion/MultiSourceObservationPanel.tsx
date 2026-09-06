import React from 'react';
import {
  Layers,
} from 'lucide-react';

export interface ObservationSourceItem {
  id: string;
  scene_id: string;
  platform: string;
  sensor: string;
  modality: string;
  acquisition_datetime: string;
  gsd_meters: number;
  cloud_cover?: number | null;
  crs: string;
  is_test_fixture?: boolean;
}

interface Props {
  observations: ObservationSourceItem[];
  selectedObservationId?: string | null;
  onSelectObservation?: (obs: ObservationSourceItem) => void;
}

export const MultiSourceObservationPanel: React.FC<Props> = ({
  observations,
  selectedObservationId,
  onSelectObservation,
}) => {
  return (
    <div
      className="p-3 bg-orbit-carbon/95 border border-orbit-border rounded-xl font-mono text-xs select-none space-y-2.5 shadow-xl"
      data-testid="multi-source-observation-panel"
    >
      <div className="flex items-center justify-between pb-1.5 border-b border-orbit-border">
        <div className="flex items-center gap-1.5 text-orbit-emerald font-bold text-[11px]">
          <Layers className="w-3.5 h-3.5" />
          <span>MULTI-SOURCE OBSERVATION REGISTRY</span>
        </div>
        <span className="text-[9px] px-1.5 py-0.5 rounded bg-orbit-slate text-orbit-muted border border-orbit-border font-bold">
          {observations.length} Epochs Loaded
        </span>
      </div>

      <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
        {observations.map((obs, idx) => {
          const isSelected = selectedObservationId === obs.id;
          const isOptical = obs.modality.includes('OPTICAL');

          return (
            <div
              key={obs.id}
              onClick={() => onSelectObservation?.(obs)}
              className={`p-2 rounded-lg border transition cursor-pointer space-y-1 ${
                isSelected
                  ? 'bg-orbit-emerald/10 border-orbit-emerald/60'
                  : 'bg-orbit-slate/30 border-orbit-border hover:bg-orbit-slate/50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <span className="text-orbit-emerald font-bold text-[10px]">T{idx + 1}</span>
                  <span className="font-bold text-orbit-text text-[11px] truncate max-w-[180px]">
                    {obs.platform} ({obs.sensor})
                  </span>
                </div>
                <span className={`text-[8px] px-1 rounded font-bold border ${
                  isOptical ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/40' : 'bg-purple-500/20 text-purple-400 border-purple-500/40'
                }`}>
                  {isOptical ? 'OPTICAL' : 'SAR'}
                </span>
              </div>

              <div className="text-[9px] text-orbit-muted flex justify-between">
                <span>Date: {obs.acquisition_datetime.split('T')[0]}</span>
                <span>GSD: {obs.gsd_meters}m</span>
                <span>Cloud: {obs.cloud_cover !== null && obs.cloud_cover !== undefined ? `${obs.cloud_cover}%` : 'N/A'}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
