import React from 'react';
import { EpistemicLevel } from '../../types';
import { Radio, Calculator, Scan, Sparkles, TrendingUp, Cpu } from 'lucide-react';

interface Props {
  level: EpistemicLevel;
  size?: 'sm' | 'md';
}

export const EpistemicBadge: React.FC<Props> = ({ level, size = 'md' }) => {
  const sizeClasses = size === 'sm' ? 'text-[10px] px-1.5 py-0.5 gap-1' : 'text-xs px-2 py-0.5 gap-1.5';

  const config = {
    OBSERVED: {
      label: 'OBSERVED',
      classes: 'bg-emerald-500/10 text-orbit-emerald border-orbit-emerald/30',
      icon: Radio,
      desc: 'Level 0/1: Raw or calibrated physical sensor telemetry',
    },
    CALCULATED: {
      label: 'CALCULATED',
      classes: 'bg-sky-500/10 text-orbit-sky border-orbit-sky/30',
      icon: Calculator,
      desc: 'Level 1: Deterministic radiometric or geodesic mathematical computation',
    },
    DETECTED: {
      label: 'DETECTED',
      classes: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
      icon: Scan,
      desc: 'Level 2/4: Algorithmic spatial/temporal segmentation or cluster entity',
    },
    ESTIMATED: {
      label: 'ESTIMATED',
      classes: 'bg-amber-500/10 text-orbit-amber border-orbit-amber/30',
      icon: Sparkles,
      desc: 'Statistical approximation or spatial interpolation',
    },
    PREDICTED: {
      label: 'PROJECTED (FORECAST)',
      classes: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
      icon: TrendingUp,
      desc: 'Future time-series or cellular automata simulation; not an observation',
    },
    AI_INTERPRETATION: {
      label: 'AI INTERPRETATION',
      classes: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
      icon: Cpu,
      desc: 'Level 5: Generative LLM narrative briefing strictly grounded in Level 0-4 facts',
    },
  }[level];

  const IconComponent = config.icon;

  return (
    <span
      className={`inline-flex items-center rounded border font-mono font-semibold tracking-wider uppercase ${config.classes} ${sizeClasses}`}
      title={config.desc}
      data-testid={`epistemic-badge-${level.toLowerCase()}`}
    >
      <IconComponent className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      {config.label}
    </span>
  );
};
