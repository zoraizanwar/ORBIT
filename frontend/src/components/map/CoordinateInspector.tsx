import React from 'react';
import { Coordinates } from '../../map/mapTypes';
import { MAP_CONFIG } from '../../map/mapConfig';
import { formatCoordinates } from '../../map/mapUtils';
import { Crosshair, Globe } from 'lucide-react';

interface Props {
  coordinates: Coordinates;
  zoom: number;
}

export const CoordinateInspector: React.FC<Props> = ({ coordinates, zoom }) => {
  const precision = MAP_CONFIG.getCoordinatePrecision(zoom);
  const { latFormatted, lngFormatted } = formatCoordinates(coordinates, precision);

  return (
    <div
      className="bg-orbit-carbon/90 border border-orbit-border px-3.5 py-1.5 rounded-full font-mono text-xs text-orbit-muted shadow-lg backdrop-blur-sm flex items-center gap-3 select-none"
      data-testid="coordinate-inspector"
    >
      <div className="flex items-center gap-1.5 text-orbit-emerald font-bold">
        <Crosshair className="w-3.5 h-3.5 animate-pulse" />
        <span>{latFormatted}</span>
      </div>
      <span className="text-orbit-border">|</span>
      <div className="flex items-center gap-1.5 text-orbit-emerald font-bold">
        <span>{lngFormatted}</span>
      </div>
      <span className="text-orbit-border">|</span>
      <div className="flex items-center gap-1 text-orbit-sky text-[11px]">
        <span>Z{zoom.toFixed(1)}</span>
      </div>
      <span className="text-orbit-border">|</span>
      <div className="flex items-center gap-1 text-[10px] text-orbit-muted uppercase">
        <Globe className="w-3 h-3" />
        <span>{MAP_CONFIG.CRS.STORAGE}</span>
      </div>
    </div>
  );
};
