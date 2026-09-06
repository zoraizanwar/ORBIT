import React, { useState } from 'react';
import { EpistemicBadge } from './EpistemicBadge';
import { EvidenceStrengthBadge } from './EvidenceStrengthBadge';
import { EpistemicLevel, EvidenceStrength } from '../../types/index';

interface EvidenceItem {
  id: string;
  source_type: string;
  source_id: string;
  claim_type: string;
  claim_reference: string;
  input_checksum: string;
  evidence_strength: EvidenceStrength;
  epistemic_level: EpistemicLevel;
  algorithm: string;
  parameters: Record<string, any>;
  created_at: string;
}

const DEMO_EVIDENCE_RECORDS: EvidenceItem[] = [
  {
    id: 'ev-rec-001',
    source_type: 'SATELLITE_TELEMETRY',
    source_id: 'S2A_MSIL2A_20260718T135121_N0510_R024_T21LUJ_20260718T182010',
    claim_type: 'CANOPY_DEFICIT_INDEX',
    claim_reference: 'dNDVI_Sinop_Sector_A',
    input_checksum: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    evidence_strength: 'STRONG',
    epistemic_level: 'CALCULATED',
    algorithm: 'Deterministic_Normalized_Difference_B8_B4',
    parameters: { nir_band: 'B08', red_band: 'B04', delta_threshold: -0.15 },
    created_at: '2026-08-24T02:00:00Z',
  },
  {
    id: 'ev-rec-002',
    source_type: 'ROAD_VECTOR_REGISTRY',
    source_id: 'OSM_Way_1289412_BR163',
    claim_type: 'INFRASTRUCTURE_CORRIDOR_PROXIMITY',
    claim_reference: 'Highway BR-163 Right-of-Way',
    input_checksum: '8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4',
    evidence_strength: 'STRONG',
    epistemic_level: 'OBSERVED',
    algorithm: 'PostGIS_ST_DWithin_Spheroid_500m',
    parameters: { buffer_meters: 500.0, highway_class: 'primary' },
    created_at: '2026-08-24T02:00:00Z',
  },
  {
    id: 'ev-rec-003',
    source_type: 'SATELLITE_TELEMETRY',
    source_id: 'S1A_IW_GRDH_1SDV_20260715T221430',
    claim_type: 'SAR_AMPLITUDE_BACKSCATTER',
    claim_reference: 'VH_Polarization_Amplitude_Grid',
    input_checksum: 'c2b451296cfbf989504c5e5c709e0839e14a22904c602aa49c6563604f86d649',
    evidence_strength: 'MODERATE',
    epistemic_level: 'OBSERVED',
    algorithm: 'SAR_Sigma0_Radiometric_Calibration',
    parameters: { polarization: 'VH', orbit: 'DESCENDING' },
    created_at: '2026-08-24T02:00:00Z',
  },
];

export const EvidencePanel: React.FC = () => {
  const [filterType, setFilterType] = useState<string>('ALL');

  const filtered = DEMO_EVIDENCE_RECORDS.filter(
    (item) => filterType === 'ALL' || item.source_type === filterType
  );

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center justify-between">
        <div className="text-xs font-bold uppercase tracking-wider text-gray-400">
          Grounded Evidence Records ({filtered.length})
        </div>
        <div className="flex items-center space-x-2">
          <label className="text-[11px] text-gray-500">Source Type:</label>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded px-2 py-1 focus:ring-1 focus:ring-blue-500"
          >
            <option value="ALL">All Sources</option>
            <option value="SATELLITE_TELEMETRY">Satellite Telemetry</option>
            <option value="ROAD_VECTOR_REGISTRY">Road Vector Registry</option>
          </select>
        </div>
      </div>

      {/* Record Cards */}
      <div className="space-y-2.5">
        {filtered.map((item) => (
          <div
            key={item.id}
            className="p-3 bg-gray-900/60 border border-gray-800 rounded-lg hover:border-gray-700 transition-all space-y-2"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold text-gray-200">{item.claim_reference}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">
                  {item.claim_type}
                </span>
              </div>
              <div className="flex items-center space-x-1.5">
                <EpistemicBadge level={item.epistemic_level} />
                <EvidenceStrengthBadge strength={item.evidence_strength} />
              </div>
            </div>

            <div className="text-xs font-mono text-gray-400 truncate">
              Source: <span className="text-gray-300">{item.source_id}</span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[11px] pt-1 text-gray-400">
              <div>
                <span className="text-gray-500">Algorithm: </span>
                <span className="font-mono text-gray-300">{item.algorithm}</span>
              </div>
              <div className="truncate">
                <span className="text-gray-500">SHA-256: </span>
                <span className="font-mono text-gray-400">{item.input_checksum.slice(0, 16)}...</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
