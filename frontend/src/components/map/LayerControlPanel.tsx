import React, { useState } from 'react';
import { LayerToggleState } from '../../map/mapTypes';
import { Layers, ChevronDown, ChevronUp } from 'lucide-react';

interface Props {
  layers: LayerToggleState;
  onToggleLayer: (layerKey: keyof LayerToggleState) => void;
}

export const LayerControlPanel: React.FC<Props> = ({ layers, onToggleLayer }) => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div
      className="bg-orbit-carbon/95 border border-orbit-border rounded-xl shadow-xl backdrop-blur-md font-mono text-xs select-none w-72 overflow-hidden"
      data-testid="layer-control-panel"
    >
      {/* Header */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="p-3 border-b border-orbit-border/60 flex items-center justify-between cursor-pointer hover:bg-orbit-slate/40 transition"
      >
        <div className="flex items-center gap-2 text-orbit-text font-bold">
          <Layers className="w-4 h-4 text-orbit-emerald" />
          <span className="tracking-wide uppercase text-[11px]">LAYER CONTROL</span>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4 text-orbit-muted" /> : <ChevronDown className="w-4 h-4 text-orbit-muted" />}
      </div>

      {/* Layer List Categories */}
      {isOpen && (
        <div className="p-3 space-y-4 max-h-[380px] overflow-y-auto scrollbar-thin text-[11px]">
          {/* Section 1: ANALYSIS & AOI */}
          <div className="space-y-1.5">
            <div className="text-[10px] font-bold text-orbit-emerald tracking-wider uppercase">
              ANALYSIS & AOI
            </div>
            <label className="flex items-center justify-between p-1.5 rounded hover:bg-orbit-slate/50 cursor-pointer transition">
              <div className="flex items-center gap-2 text-orbit-text">
                <input
                  type="checkbox"
                  checked={layers.aoiBoundary}
                  onChange={() => onToggleLayer('aoiBoundary')}
                  className="accent-orbit-emerald rounded"
                />
                <span>AOI MultiPolygon Boundary</span>
              </div>
              <span className="w-2.5 h-2.5 rounded-sm bg-orbit-emerald/30 border border-orbit-emerald"></span>
            </label>

            <label className="flex items-center justify-between p-1.5 rounded hover:bg-orbit-slate/50 cursor-pointer transition">
              <div className="flex items-center gap-2 text-orbit-text">
                <input
                  type="checkbox"
                  checked={layers.changeDetectionMask}
                  onChange={() => onToggleLayer('changeDetectionMask')}
                  className="accent-orbit-critical rounded"
                />
                <span>dNDVI Change Detection Mask</span>
              </div>
              <span className="w-2.5 h-2.5 rounded-sm bg-red-500/30 border border-red-500"></span>
            </label>
          </div>

          {/* Section 2: INFRASTRUCTURE (OSM VECTORS) */}
          <div className="space-y-1.5 border-t border-orbit-border/40 pt-2.5">
            <div className="text-[10px] font-bold text-orbit-sky tracking-wider uppercase">
              INFRASTRUCTURE (OSM VECTORS)
            </div>
            <label className="flex items-center justify-between p-1.5 rounded hover:bg-orbit-slate/50 cursor-pointer transition">
              <div className="flex items-center gap-2 text-orbit-text">
                <input
                  type="checkbox"
                  checked={layers.roadsPrimary}
                  onChange={() => onToggleLayer('roadsPrimary')}
                  className="accent-orbit-amber rounded"
                />
                <span>Primary Highways (BR-163)</span>
              </div>
              <span className="w-3 h-0.5 bg-amber-400"></span>
            </label>

            <label className="flex items-center justify-between p-1.5 rounded hover:bg-orbit-slate/50 cursor-pointer transition">
              <div className="flex items-center gap-2 text-orbit-text">
                <input
                  type="checkbox"
                  checked={layers.roadsSecondary}
                  onChange={() => onToggleLayer('roadsSecondary')}
                  className="accent-orbit-sky rounded"
                />
                <span>Secondary & Feeder Tracks</span>
              </div>
              <span className="w-3 h-0.5 bg-sky-400"></span>
            </label>

            <label className="flex items-center justify-between p-1.5 rounded hover:bg-orbit-slate/50 cursor-pointer transition">
              <div className="flex items-center gap-2 text-orbit-text">
                <input
                  type="checkbox"
                  checked={layers.roadsLocal}
                  onChange={() => onToggleLayer('roadsLocal')}
                  className="accent-orange-500 rounded"
                />
                <span>Logging Spurs & Unpaved Tracks</span>
              </div>
              <span className="w-3 h-0.5 border-b border-dashed border-orange-400"></span>
            </label>
          </div>

          {/* Section 3: EARTH OBSERVATION RASTER */}
          <div className="space-y-1.5 border-t border-orbit-border/40 pt-2.5">
            <div className="text-[10px] font-bold text-orbit-muted tracking-wider uppercase flex items-center justify-between">
              <span>EARTH OBSERVATION</span>
              <span className="text-[9px] text-orbit-muted/70">PHASE 6+</span>
            </div>
            <label className="flex items-center justify-between p-1.5 rounded opacity-60 cursor-not-allowed">
              <div className="flex items-center gap-2 text-orbit-muted">
                <input type="checkbox" disabled checked={false} />
                <span>Sentinel-2 L2A (10m Optical)</span>
              </div>
              <span className="text-[9px] bg-orbit-slate px-1 rounded text-orbit-muted">COG</span>
            </label>
            <label className="flex items-center justify-between p-1.5 rounded opacity-60 cursor-not-allowed">
              <div className="flex items-center gap-2 text-orbit-muted">
                <input type="checkbox" disabled checked={false} />
                <span>Sentinel-1 SAR C-Band GRD</span>
              </div>
              <span className="text-[9px] bg-orbit-slate px-1 rounded text-orbit-muted">SAR</span>
            </label>
          </div>
        </div>
      )}
    </div>
  );
};
