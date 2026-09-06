import React from 'react';
import { calculateGeodesicScale } from '../../map/mapUtils';

interface Props {
  latitude: number;
  zoom: number;
}

export const MapScaleDisplay: React.FC<Props> = ({ latitude, zoom }) => {
  const scale = calculateGeodesicScale(latitude, zoom);

  return (
    <div
      className="bg-orbit-carbon/90 border border-orbit-border px-3 py-1 rounded-md font-mono text-[11px] text-orbit-muted shadow-lg backdrop-blur-sm flex flex-col items-center select-none"
      data-testid="map-scale-display"
      title="Dynamic WGS84 Geodesic Cartographic Scale"
    >
      <div className="font-semibold text-orbit-text text-[10px] mb-0.5">
        {scale.distanceText}
      </div>
      <div
        className="h-1.5 bg-orbit-slate border border-orbit-text flex"
        style={{ width: `${scale.pixelWidth}px` }}
      >
        <div className="w-1/2 h-full bg-orbit-emerald"></div>
        <div className="w-1/2 h-full bg-transparent"></div>
      </div>
    </div>
  );
};
