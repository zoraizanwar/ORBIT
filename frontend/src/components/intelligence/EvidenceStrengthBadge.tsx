import React from 'react';
import { EvidenceStrength } from '../../types';
import { ShieldCheck, ShieldAlert, ShieldX, Shield } from 'lucide-react';

interface Props {
  strength: EvidenceStrength;
  showScore?: boolean;
  score?: number;
  size?: 'sm' | 'md' | 'lg';
}

export const EvidenceStrengthBadge: React.FC<Props> = ({
  strength,
  showScore = false,
  score,
  size = 'md',
}) => {
  const sizeClasses = {
    sm: 'text-[10px] px-1.5 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3 py-1.5 gap-2 font-medium',
  }[size];

  const config = {
    STRONG: {
      label: 'Evidence: STRONG',
      classes: 'bg-emerald-500/10 text-orbit-emerald border-orbit-emerald/40',
      icon: ShieldCheck,
      desc: 'Multi-sensor high-resolution telemetry, cloud-free, tight temporal match',
    },
    MODERATE: {
      label: 'Evidence: MODERATE',
      classes: 'bg-sky-500/10 text-orbit-sky border-orbit-sky/40',
      icon: Shield,
      desc: 'Standard multi-spectral resolution with acceptable atmospheric bounds',
    },
    LIMITED: {
      label: 'Evidence: LIMITED',
      classes: 'bg-amber-500/10 text-orbit-amber border-orbit-amber/40',
      icon: ShieldAlert,
      desc: 'Coarse resolution or partial atmospheric interference',
    },
    INSUFFICIENT: {
      label: 'Evidence: INSUFFICIENT',
      classes: 'bg-red-500/10 text-orbit-critical border-orbit-critical/40',
      icon: ShieldX,
      desc: 'Severe cloud obscuration or missing sensor telemetry',
    },
  }[strength];

  const IconComponent = config.icon;

  return (
    <div
      className={`inline-flex items-center rounded-md border font-mono tracking-tight shadow-sm ${config.classes} ${sizeClasses}`}
      title={config.desc}
      data-testid={`evidence-strength-${strength.toLowerCase()}`}
    >
      <IconComponent className={size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'} />
      <span>{config.label}</span>
      {showScore && score !== undefined && (
        <span className="opacity-75 font-sans font-normal border-l border-current/30 pl-1.5 ml-0.5">
          ESI {(score * 100).toFixed(0)}%
        </span>
      )}
    </div>
  );
};
