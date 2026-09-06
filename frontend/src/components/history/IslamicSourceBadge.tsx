import React from 'react';
import { IslamicSourceGrade } from '../../types';
import { BookOpen, Scroll, Award, Bookmark, BookText, AlertTriangle } from 'lucide-react';

interface Props {
  grade: IslamicSourceGrade;
  size?: 'sm' | 'md';
}

export const IslamicSourceBadge: React.FC<Props> = ({
  grade,
  size = 'md',
}) => {
  const sizeClasses = size === 'sm' ? 'text-[10px] px-1.5 py-0.5 gap-1' : 'text-xs px-2.5 py-1 gap-1.5';

  const config = {
    QURAN: {
      label: 'QURAN (MUTAWATIR QAT\'I)',
      classes: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40',
      icon: BookOpen,
      desc: 'Canonical Quranic revelation; absolute textual certainty',
    },
    MUTAWATIR_HADITH: {
      label: 'MUTAWATIR HADITH',
      classes: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      icon: Award,
      desc: 'Mass-transmitted prophetic tradition across uninterrupted independent chains',
    },
    AHAD_SAHIH: {
      label: 'AHAD SAHIH',
      classes: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30',
      icon: Scroll,
      desc: 'Rigorously authenticated Hadith with sound unbroken chain (Isnad)',
    },
    SCHOLARLY_IJMA: {
      label: 'SCHOLARLY GEOGRAPHY',
      classes: 'bg-sky-500/10 text-sky-300 border-sky-500/30',
      icon: Bookmark,
      desc: 'Documented consensus & geographic treatise of classical Muslim scholars',
    },
    HISTORICAL_TARIKH: {
      label: 'HISTORICAL CHRONICLE (TARIKH)',
      classes: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
      icon: BookText,
      desc: 'Early Islamic historical chronicles (Al-Tabari, Ibn Kathir, Al-Baladhuri)',
    },
    UNVERIFIED_ISRAILIYYAT: {
      label: 'UNVERIFIED / ISRAILIYYAT',
      classes: 'bg-red-500/10 text-red-300 border-red-500/30',
      icon: AlertTriangle,
      desc: 'Folkloric or unverified addition; explicitly non-authoritative',
    },
  }[grade];

  const IconComponent = config.icon;

  return (
    <div
      className={`inline-flex items-center rounded-md border font-mono tracking-tight font-medium ${config.classes} ${sizeClasses}`}
      title={config.desc}
      data-testid={`islamic-badge-${grade.toLowerCase()}`}
    >
      <IconComponent className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      <span>{config.label}</span>
    </div>
  );
};
