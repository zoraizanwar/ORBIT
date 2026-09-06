import React from 'react';
import { SupportClassification } from '../../types';
import { CheckCircle2, AlertCircle, HelpCircle, Ban } from 'lucide-react';

interface Props {
  classification: SupportClassification;
  year?: number;
  size?: 'sm' | 'md';
}

export const HistoricalSupportBadge: React.FC<Props> = ({
  classification,
  year,
  size = 'md',
}) => {
  const sizeClasses = size === 'sm' ? 'text-[10px] px-2 py-0.5 gap-1' : 'text-xs px-2.5 py-1 gap-1.5';

  const config = {
    STRONGLY_SUPPORTED: {
      label: 'STRONGLY SUPPORTED',
      classes: 'bg-emerald-500/10 text-orbit-emerald border-orbit-emerald/30',
      icon: CheckCircle2,
      desc: 'Multiple cloud-free calibrated scenes available for this annual epoch',
    },
    PARTIALLY_SUPPORTED: {
      label: 'PARTIALLY SUPPORTED',
      classes: 'bg-sky-500/10 text-orbit-sky border-orbit-sky/30',
      icon: AlertCircle,
      desc: 'Limited seasonal passes (e.g. Landsat 4-5); coarse change resolution',
    },
    ESTIMATED: {
      label: 'ESTIMATED (HARMONIC)',
      classes: 'bg-amber-500/10 text-orbit-amber border-orbit-amber/30',
      icon: HelpCircle,
      desc: 'Significant cloud gaps; trend derived via temporal harmonic interpolation',
    },
    UNAVAILABLE: {
      label: 'DATA UNAVAILABLE',
      classes: 'bg-slate-500/10 text-orbit-muted border-orbit-border',
      icon: Ban,
      desc: 'Zero valid telemetry exists for this historical year; zero data fabricated',
    },
  }[classification];

  const IconComponent = config.icon;

  return (
    <div
      className={`inline-flex items-center rounded border font-mono tracking-tight ${config.classes} ${sizeClasses}`}
      title={config.desc}
      data-testid={`historical-support-${classification.toLowerCase()}`}
    >
      <IconComponent className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      {year && <span className="font-bold border-r border-current/30 pr-1 mr-0.5">{year}</span>}
      <span>{config.label}</span>
    </div>
  );
};
