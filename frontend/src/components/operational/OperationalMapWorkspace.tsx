import React, { useState } from 'react';
import { OrbitMap } from '../map/OrbitMap';
import { Coordinates } from '../../map/mapTypes';
import { NormalizedImageryScene } from '../../types/earthObservation';
import { Eye, EyeOff, Layers } from 'lucide-react';

interface Props {
  theme: 'dark' | 'light';
  targetCoordinates?: Coordinates | null;
  selectedScene?: NormalizedImageryScene | null;
  t1Scene?: NormalizedImageryScene | null;
  t2Scene?: NormalizedImageryScene | null;
}

export const OperationalMapWorkspace: React.FC<Props> = ({
  theme,
  targetCoordinates,
  selectedScene,
  t1Scene,
  t2Scene,
}) => {
  const [showAoi, setShowAoi] = useState(true);
  const [showFootprints, setShowFootprints] = useState(true);
  const [showChangeMask, setShowChangeMask] = useState(true);
  const [showRoads, setShowRoads] = useState(true);

  return (
    <div className="relative w-full h-full flex-1 overflow-hidden" data-testid="operational-map-workspace">
      <OrbitMap
        theme={theme}
        targetCoordinates={targetCoordinates}
        selectedScene={selectedScene || t2Scene || t1Scene}
      />

      {/* Operational Layer Visibility Controls */}
      <div className="absolute top-16 right-4 z-10 bg-orbit-carbon/90 backdrop-blur-md border border-orbit-border rounded-xl p-2.5 shadow-xl font-mono text-xs select-none w-52 space-y-2">
        <div className="flex items-center gap-1.5 text-orbit-emerald font-bold text-[11px] pb-1.5 border-b border-orbit-border">
          <Layers className="w-3.5 h-3.5" />
          <span>OPERATIONAL LAYERS</span>
        </div>

        <div className="space-y-1.5">
          <button
            onClick={() => setShowAoi(!showAoi)}
            className="w-full flex items-center justify-between p-1.5 rounded hover:bg-orbit-slate/50 text-[10px] text-orbit-text transition"
          >
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-cyan-400" />
              <span>AOI Boundary</span>
            </span>
            {showAoi ? <Eye className="w-3 h-3 text-orbit-emerald" /> : <EyeOff className="w-3 h-3 text-orbit-muted" />}
          </button>

          <button
            onClick={() => setShowFootprints(!showFootprints)}
            className="w-full flex items-center justify-between p-1.5 rounded hover:bg-orbit-slate/50 text-[10px] text-orbit-text transition"
          >
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-orbit-emerald" />
              <span>Scene Footprints</span>
            </span>
            {showFootprints ? <Eye className="w-3 h-3 text-orbit-emerald" /> : <EyeOff className="w-3 h-3 text-orbit-muted" />}
          </button>

          <button
            onClick={() => setShowChangeMask(!showChangeMask)}
            className="w-full flex items-center justify-between p-1.5 rounded hover:bg-orbit-slate/50 text-[10px] text-orbit-text transition"
          >
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              <span>Change Mask</span>
            </span>
            {showChangeMask ? <Eye className="w-3 h-3 text-orbit-emerald" /> : <EyeOff className="w-3 h-3 text-orbit-muted" />}
          </button>

          <button
            onClick={() => setShowRoads(!showRoads)}
            className="w-full flex items-center justify-between p-1.5 rounded hover:bg-orbit-slate/50 text-[10px] text-orbit-text transition"
          >
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-rose-400" />
              <span>Road Corridors</span>
            </span>
            {showRoads ? <Eye className="w-3 h-3 text-orbit-emerald" /> : <EyeOff className="w-3 h-3 text-orbit-muted" />}
          </button>
        </div>

        {/* Epistemic Level Indicator */}
        <div className="pt-2 border-t border-orbit-border flex items-center justify-between text-[9px] text-orbit-muted">
          <span>Active Pipeline:</span>
          <span className="font-bold text-orbit-emerald">OBSERVED / CALC</span>
        </div>
      </div>
    </div>
  );
};
