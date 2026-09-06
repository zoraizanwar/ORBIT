import React from 'react';
import { SpatialContextResult } from '../../types/intelligence';

interface Props {
  context: SpatialContextResult;
}

export const SpatialContextCard: React.FC<Props> = ({ context }) => {
  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-lg p-3 space-y-2.5">
      <div className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center justify-between">
        <span>Spatial Infrastructure Context</span>
        <span
          className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
            context.intersects_road_corridor
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
              : 'bg-gray-800 text-gray-400'
          }`}
        >
          {context.spatial_relationship}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="p-2 bg-gray-950/40 border border-gray-800/80 rounded">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider">Closest Road Feature</div>
          <div className="font-semibold text-gray-200 mt-0.5">
            {context.closest_road_name || 'No proximate road within buffer'}
          </div>
          {context.closest_road_class && (
            <div className="text-[10px] text-gray-400 font-mono mt-0.5">
              Class: {context.closest_road_class}
            </div>
          )}
        </div>

        <div className="p-2 bg-gray-950/40 border border-gray-800/80 rounded">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider">Distance to Corridor</div>
          <div className="font-mono font-semibold text-gray-200 mt-0.5">
            {context.distance_to_closest_road_m !== null && context.distance_to_closest_road_m !== undefined
              ? `${context.distance_to_closest_road_m.toFixed(1)} m`
              : 'N/A (> 5000m)'}
          </div>
          <div className="text-[10px] text-gray-500 mt-0.5">
            Buffer Limit: {context.road_corridor_buffer_m}m
          </div>
        </div>
      </div>
    </div>
  );
};
