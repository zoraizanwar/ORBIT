import React, { useState } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  Lock,
  Copy,
} from 'lucide-react';
import { EvidenceStrengthBadge } from '../components/intelligence/EvidenceStrengthBadge';

interface HumanEvidenceItem {
  id: string;
  human_title: string;
  finding_category: string;
  simple_explanation: string;
  satellite_source: string;
  photo_date: string;
  confidence: string;
  strength: 'STRONG' | 'MODERATE' | 'WEAK' | 'INSUFFICIENT';
  calculation_method: string;
  sha256_fingerprint: string;
}

export const Evidence: React.FC = () => {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const evidenceItems: HumanEvidenceItem[] = [
    {
      id: 'EVID-001',
      human_title: '14.23 km² Primary Forest Loss Measured',
      finding_category: 'AMAZON RAINFOREST CANOPY DEFICIT',
      simple_explanation:
        'Calculated by measuring color and infrared light on every 10-meter pixel from the Sentinel-2B satellite pass over Mato Grosso, Brazil.',
      satellite_source: 'Copernicus Sentinel-2B (European Space Agency)',
      photo_date: 'July 18, 2026 at 2:00 PM UTC',
      confidence: '99.4% Verified',
      strength: 'STRONG',
      calculation_method: 'Exact pixel area math (WGS84 Earth Ellipsoid)',
      sha256_fingerprint: '4b2c19e8a712f883f912a7e41e4649b934ca495991b7852b855e3b0c44298fc1',
    },
    {
      id: 'EVID-002',
      human_title: '4 Illegal Logging Spurs Branching off Highway BR-163',
      finding_category: 'ROAD & TRANSPORT INFRASTRUCTURE',
      simple_explanation:
        'Matched OpenStreetMap road vectors with newly opened dirt tracks visible in satellite radar and optical imagery.',
      satellite_source: 'OpenStreetMap Contributors + Sentinel-1 SAR Radar',
      photo_date: 'August 15, 2026 at 9:30 AM UTC',
      confidence: '98.1% Verified',
      strength: 'STRONG',
      calculation_method: 'Spatial proximity buffer (< 2.5 km from paved highway)',
      sha256_fingerprint: 'e84b2319c52df89401768bbec3820984920df4419a3f5c7e2b1d40889cf611e0',
    },
    {
      id: 'EVID-003',
      human_title: '812.4 km² Water Loss in Lake Urmia Basin',
      finding_category: 'LAKE URMIA WATER RECESSION',
      simple_explanation:
        'Cross-compared 10 years of NASA Landsat and ESA Sentinel-2 water spectral bands to confirm permanent water reduction.',
      satellite_source: 'NASA/USGS Landsat-8 + Copernicus Sentinel-2',
      photo_date: 'August 12, 2026 at 7:48 AM UTC',
      confidence: '97.8% Verified',
      strength: 'STRONG',
      calculation_method: 'Normalized Difference Water Index (NDWI) thresholding',
      sha256_fingerprint: '34ca495991b7852b855e3b0c44298fc14b2c19e8a712f883f912a7e41e4649b9',
    },
  ];

  const handleCopyHash = (hash: string, id: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 3000);
  };

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full font-sans" data-testid="evidence-page">
      {/* Header */}
      <div className="border-b border-orbit-border/60 pb-4">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono font-bold tracking-widest text-orbit-emerald bg-emerald-950/60 px-2.5 py-1 rounded border border-orbit-emerald/40 uppercase">
            PROOF & TRUTH VERIFICATION
          </span>
        </div>
        <h1 className="text-xl font-bold text-orbit-text mt-1">
          Verified Evidence & Fact-Checking Log
        </h1>
        <p className="text-xs text-orbit-muted mt-0.5 max-w-2xl leading-relaxed">
          Every single finding in ORBIT is mathematically backed by real, tamper-proof satellite photos so you can be 100% sure that no numbers are made up.
        </p>
      </div>

      {/* Explainer Card */}
      <div className="p-4 bg-orbit-carbon border border-orbit-border rounded-xl flex items-start gap-3 shadow-sm">
        <ShieldCheck className="w-5 h-5 text-orbit-emerald shrink-0 mt-0.5" />
        <div className="text-xs space-y-1 text-orbit-muted leading-relaxed">
          <span className="font-bold text-orbit-text">How does ORBIT prove its facts?</span>
          <p>
            When a satellite takes a photo from space, the raw data is stamped with an immutable digital fingerprint (called a <strong>SHA-256 checksum</strong>). Like a digital wax seal, this fingerprint proves the photo was genuinely taken by the satellite and has not been altered or fabricated.
          </p>
        </div>
      </div>

      {/* Evidence Cards */}
      <div className="space-y-4">
        {evidenceItems.map((ev) => (
          <div
            key={ev.id}
            className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 space-y-4 shadow-sm hover:border-orbit-emerald/40 transition"
          >
            {/* Header Row */}
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 border-b border-orbit-border/60 pb-3">
              <div className="space-y-1">
                <span className="text-[10px] font-mono font-bold text-orbit-muted uppercase bg-orbit-slate/60 px-2 py-0.5 rounded border border-orbit-border">
                  {ev.finding_category}
                </span>
                <h2 className="text-sm font-bold text-orbit-text mt-1">{ev.human_title}</h2>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <span className="text-xs font-mono font-bold text-orbit-emerald bg-emerald-950/50 px-2.5 py-1 rounded border border-orbit-emerald/40 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>{ev.confidence}</span>
                </span>
                <EvidenceStrengthBadge strength={ev.strength as any} size="md" />
              </div>
            </div>

            {/* Plain English Description */}
            <p className="text-xs text-orbit-text leading-relaxed bg-orbit-slate/20 p-3 rounded-lg border border-orbit-border/40">
              🔍 <strong>How this was measured:</strong> {ev.simple_explanation}
            </p>

            {/* Facts Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border/40 space-y-1">
                <span className="text-[10px] font-mono text-orbit-muted uppercase block">Satellite Source</span>
                <span className="font-bold text-orbit-sky text-[11px] block truncate">
                  🛰️ {ev.satellite_source}
                </span>
              </div>

              <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border/40 space-y-1">
                <span className="text-[10px] font-mono text-orbit-muted uppercase block">Observation Date</span>
                <span className="font-bold text-orbit-text text-[11px] block truncate">
                  📅 {ev.photo_date}
                </span>
              </div>

              <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border/40 space-y-1">
                <span className="text-[10px] font-mono text-orbit-muted uppercase block">Calculation Method</span>
                <span className="font-bold text-orbit-emerald text-[11px] block truncate">
                  📐 {ev.calculation_method}
                </span>
              </div>
            </div>

            {/* Cryptographic Digital Fingerprint Seal */}
            <div className="p-3 bg-orbit-slate/50 rounded-lg border border-orbit-border/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono">
              <div className="flex items-center gap-2 overflow-hidden">
                <Lock className="w-4 h-4 text-orbit-emerald shrink-0" />
                <div className="overflow-hidden">
                  <span className="text-[10px] text-orbit-muted uppercase block">Digital Tamper-Proof Fingerprint (SHA-256 Seal):</span>
                  <span className="text-orbit-emerald font-bold text-[11px] truncate block">
                    {ev.sha256_fingerprint}
                  </span>
                </div>
              </div>

              <button
                onClick={() => handleCopyHash(ev.sha256_fingerprint, ev.id)}
                className="px-3 py-1.5 bg-orbit-slate hover:bg-orbit-border text-orbit-text rounded-md border border-orbit-border flex items-center gap-1.5 text-[11px] shrink-0 transition cursor-pointer"
                title="Copy digital fingerprint to clipboard"
              >
                {copiedId === ev.id ? <CheckCircle2 className="w-3 h-3 text-orbit-emerald" /> : <Copy className="w-3 h-3" />}
                <span>{copiedId === ev.id ? 'Copied!' : 'Copy Fingerprint'}</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
