import React from 'react';
import {
  Compass,
  ZoomIn,
  ZoomOut,
  Maximize,
  Crosshair,
  Box,
} from 'lucide-react';

interface Props {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetNorth: () => void;
  onRecenterAoi: () => void;
  onTogglePitch: () => void;
  onToggleFullscreen: () => void;
  pitch: number;
  bearing: number;
}

export const MapControls: React.FC<Props> = ({
  onZoomIn,
  onZoomOut,
  onResetNorth,
  onRecenterAoi,
  onTogglePitch,
  onToggleFullscreen,
  pitch,
  bearing,
}) => {
  return (
    <div className="flex flex-col gap-2 select-none" data-testid="map-controls">
      {/* North Arrow / Compass Indicator with dynamic rotation */}
      <button
        onClick={onResetNorth}
        className="w-10 h-10 rounded-lg bg-orbit-carbon/90 border border-orbit-border hover:border-orbit-emerald/50 flex flex-col items-center justify-center text-orbit-emerald shadow-lg backdrop-blur-sm transition group"
        title="Reset North Orientation"
        aria-label="Reset North"
      >
        <div
          style={{ transform: `rotate(${-bearing}deg)` }}
          className="transition-transform duration-200"
        >
          <Compass className="w-5 h-5 stroke-[2.2]" />
        </div>
        <span className="text-[8px] font-mono font-bold -mt-0.5 group-hover:text-orbit-text">
          N
        </span>
      </button>

      {/* Primary Zoom & Navigation Controls */}
      <div className="bg-orbit-carbon/90 border border-orbit-border rounded-lg flex flex-col shadow-lg backdrop-blur-sm divide-y divide-orbit-border">
        <button
          onClick={onZoomIn}
          className="p-2 hover:bg-orbit-slate text-orbit-muted hover:text-orbit-text transition"
          title="Zoom In"
          aria-label="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={onZoomOut}
          className="p-2 hover:bg-orbit-slate text-orbit-muted hover:text-orbit-text transition"
          title="Zoom Out"
          aria-label="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={onRecenterAoi}
          className="p-2 hover:bg-orbit-slate text-orbit-muted hover:text-orbit-emerald transition"
          title="Recenter on Target AOI"
          aria-label="Recenter on AOI"
        >
          <Crosshair className="w-4 h-4" />
        </button>
        <button
          onClick={onTogglePitch}
          className={`p-2 hover:bg-orbit-slate transition ${
            pitch > 0 ? 'text-orbit-emerald font-bold' : 'text-orbit-muted hover:text-orbit-text'
          }`}
          title="Toggle 2D / 3D Oblique Perspective"
          aria-label="Toggle 3D Pitch"
        >
          <Box className="w-4 h-4" />
        </button>
        <button
          onClick={onToggleFullscreen}
          className="p-2 hover:bg-orbit-slate text-orbit-muted hover:text-orbit-text transition"
          title="Toggle Fullscreen"
          aria-label="Toggle Fullscreen"
        >
          <Maximize className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
