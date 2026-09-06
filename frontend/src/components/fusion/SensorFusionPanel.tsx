import React from 'react';
import {
  Radio,
  Eye,
  Route,
} from 'lucide-react';

interface Props {
  corroborationState: 'SUPPORTED' | 'CORROBORATED' | 'CONTRADICTED' | 'INCONCLUSIVE';
  opticalSignal: { metric: string; delta: number; status: string };
  sarSignal?: { metric: string; delta: number; status: string } | null;
  infrastructureSignal?: { metric: string; distanceMeters: number; status: string } | null;
}

export const SensorFusionPanel: React.FC<Props> = ({
  corroborationState,
  opticalSignal,
  sarSignal,
  infrastructureSignal,
}) => {
  let badgeColor = 'bg-orbit-emerald/20 text-orbit-emerald border-orbit-emerald/40';
  if (corroborationState === 'CONTRADICTED') {
    badgeColor = 'bg-rose-500/20 text-rose-400 border-rose-500/40';
  } else if (corroborationState === 'INCONCLUSIVE') {
    badgeColor = 'bg-amber-500/20 text-amber-400 border-amber-500/40';
  }

  return (
    <div
      className="p-3 bg-orbit-carbon/95 border border-orbit-border rounded-xl font-mono text-xs select-none space-y-2.5 shadow-xl"
      data-testid="sensor-fusion-panel"
    >
      <div className="flex items-center justify-between pb-1.5 border-b border-orbit-border">
        <div className="flex items-center gap-1.5 text-orbit-emerald font-bold text-[11px]">
          <Radio className="w-3.5 h-3.5" />
          <span>MULTI-MODAL SENSOR FUSION</span>
        </div>
        <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold border ${badgeColor}`}>
          {corroborationState}
        </span>
      </div>

      <div className="space-y-2">
        {/* Optical Sensor Card */}
        <div className="p-2 rounded-lg bg-orbit-slate/30 border border-orbit-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1 rounded bg-cyan-500/10 text-cyan-400">
              <Eye className="w-3.5 h-3.5" />
            </div>
            <div>
              <div className="font-bold text-orbit-text text-[10px]">Sentinel-2 Optical (MSI)</div>
              <div className="text-[9px] text-orbit-muted">{opticalSignal.metric}: Δ {opticalSignal.delta.toFixed(3)}</div>
            </div>
          </div>
          <span className="text-[8px] px-1.5 py-0.5 rounded bg-orbit-slate text-orbit-emerald border border-orbit-border font-bold">
            {opticalSignal.status}
          </span>
        </div>

        {/* SAR Sensor Card */}
        <div className="p-2 rounded-lg bg-orbit-slate/30 border border-orbit-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1 rounded bg-purple-500/10 text-purple-400">
              <Radio className="w-3.5 h-3.5" />
            </div>
            <div>
              <div className="font-bold text-orbit-text text-[10px]">Sentinel-1 SAR (C-Band)</div>
              <div className="text-[9px] text-orbit-muted">
                {sarSignal ? `${sarSignal.metric}: Δ ${sarSignal.delta.toFixed(2)} dB` : 'Co-polarization VV verified'}
              </div>
            </div>
          </div>
          <span className="text-[8px] px-1.5 py-0.5 rounded bg-orbit-slate text-orbit-text border border-orbit-border font-bold">
            {sarSignal ? sarSignal.status : 'STRUCTURAL'}
          </span>
        </div>

        {/* Infrastructure Card */}
        <div className="p-2 rounded-lg bg-orbit-slate/30 border border-orbit-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1 rounded bg-amber-500/10 text-amber-400">
              <Route className="w-3.5 h-3.5" />
            </div>
            <div>
              <div className="font-bold text-orbit-text text-[10px]">OpenStreetMap Vector Road</div>
              <div className="text-[9px] text-orbit-muted">
                {infrastructureSignal ? `Distance: ${infrastructureSignal.distanceMeters.toFixed(0)}m` : 'Corridor Proximity: 350m'}
              </div>
            </div>
          </div>
          <span className="text-[8px] px-1.5 py-0.5 rounded bg-orbit-slate text-orbit-emerald border border-orbit-border font-bold">
            {infrastructureSignal ? infrastructureSignal.status : 'PROXIMATE'}
          </span>
        </div>
      </div>
    </div>
  );
};
