import {
  EvidencePackage,
  AIInterpretationResult,
  ReportResult,
} from '../types/ai';

const API_BASE = '/api/v1/ai';

export const DEMO_EVIDENCE_PACKAGE: EvidencePackage = {
  package_id: 'pkg-demo-sinop-001',
  aoi_id: 'aoi-sinop-mato-grosso',
  aoi_name: 'Sinop Deforestation Frontier (Mato Grosso)',
  analysis_run_id: 'run-demo-001',
  date_range_start: '2023-07-15T00:00:00Z',
  date_range_end: '2026-07-18T00:00:00Z',
  evidence_items: [
    {
      id: 'ev-scene-t1',
      type: 'SCENE',
      epistemic_level: 'OBSERVED',
      source_id: 'S2A_MSIL2A_20230715T135121',
      source_type: 'Sentinel-2 L2A',
      timestamp: '2023-07-15T00:00:00Z',
      quality_score: 0.98,
      evidence_strength: 'STRONG',
      description: 'Optical multispectral scene acquisition (Cloud Cover: 1.2%)',
      provenance: {},
    },
    {
      id: 'ev-scene-t2',
      type: 'SCENE',
      epistemic_level: 'OBSERVED',
      source_id: 'S2A_MSIL2A_20260718T135121',
      source_type: 'Sentinel-2 L2A',
      timestamp: '2026-07-18T00:00:00Z',
      quality_score: 0.99,
      evidence_strength: 'STRONG',
      description: 'Optical multispectral scene acquisition (Cloud Cover: 0.8%)',
      provenance: {},
    },
    {
      id: 'ev-ndvi-delta',
      type: 'INDEX_MEASUREMENT',
      epistemic_level: 'CALCULATED',
      source_id: 'dNDVI_Sinop_Sector_A',
      source_type: 'Spectral Delta Calculation',
      value: -0.24,
      unit: 'index_delta',
      timestamp: '2026-07-18T00:00:00Z',
      quality_score: 0.96,
      evidence_strength: 'STRONG',
      description: 'Canopy vegetation deficit (dNDVI = -0.24)',
      provenance: {},
    },
    {
      id: 'ev-ndbi-delta',
      type: 'INDEX_MEASUREMENT',
      epistemic_level: 'CALCULATED',
      source_id: 'dNDBI_Sinop_Sector_A',
      source_type: 'Spectral Delta Calculation',
      value: 0.18,
      unit: 'index_delta',
      timestamp: '2026-07-18T00:00:00Z',
      quality_score: 0.95,
      evidence_strength: 'STRONG',
      description: 'Impervious surface / built-up expansion (dNDBI = +0.18)',
      provenance: {},
    },
    {
      id: 'ev-road-corridor',
      type: 'ROAD_CORRIDOR',
      epistemic_level: 'OBSERVED',
      source_id: 'OSM_Way_BR163',
      source_type: 'OpenStreetMap Vector Registry',
      value: 85.0,
      unit: 'meters',
      quality_score: 1.0,
      evidence_strength: 'STRONG',
      description: 'Highway BR-163 primary road corridor (85m proximity)',
      provenance: {},
    },
    {
      id: 'ev-change-mask',
      type: 'CHANGE_MASK',
      epistemic_level: 'CALCULATED',
      source_id: 'mask_sinop_2023_2026',
      source_type: 'Spatial Difference Engine',
      value: 6.85,
      unit: 'km2',
      quality_score: 0.97,
      evidence_strength: 'STRONG',
      description: 'Contiguous vegetation clearance area: 6.85 km²',
      provenance: {},
    },
    {
      id: 'ev-forecast-2030',
      type: 'FORECAST_PROJECTION',
      epistemic_level: 'PREDICTED',
      source_id: 'fc-run-sinop-lt-v1',
      source_type: 'Linear Trend Model (ORBIT-LT-v1)',
      value: 0.528,
      unit: 'index_value',
      timestamp: '2030-07-01T00:00:00Z',
      quality_score: 0.90,
      evidence_strength: 'MODERATE',
      description: 'Projected NDVI in 2030 (95% CI: 0.479 – 0.577)',
      provenance: {},
    },
  ],
  relationships: [
    {
      id: 'rel-1',
      source_id: 'ev-scene-t1',
      target_id: 'ev-ndvi-delta',
      relationship_type: 'DERIVED_FROM',
      weight: 1.0,
    },
    {
      id: 'rel-2',
      source_id: 'ev-scene-t2',
      target_id: 'ev-ndvi-delta',
      relationship_type: 'DERIVED_FROM',
      weight: 1.0,
    },
    {
      id: 'rel-3',
      source_id: 'ev-ndvi-delta',
      target_id: 'ev-change-mask',
      relationship_type: 'SUPPORTS',
      weight: 1.0,
    },
    {
      id: 'rel-4',
      source_id: 'ev-ndbi-delta',
      target_id: 'ev-change-mask',
      relationship_type: 'CORROBORATES',
      weight: 1.0,
    },
    {
      id: 'rel-5',
      source_id: 'ev-road-corridor',
      target_id: 'ev-change-mask',
      relationship_type: 'LOCATED_IN',
      weight: 0.9,
    },
  ],
  has_contradictions: false,
  contradiction_count: 0,
  package_hash_sha256: '9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e',
  created_at: '2026-08-24T03:30:00Z',
};

export const DEMO_AI_INTERPRETATION: AIInterpretationResult = {
  id: 'ai-interp-sinop-001',
  aoi_id: 'aoi-sinop-mato-grosso',
  analysis_run_id: 'run-demo-001',
  title: 'Grounded Intelligence Synthesis: Sinop Deforestation Frontier',
  interpretation_type: 'URBAN_EXPANSION_SYNTHESIS',
  executive_summary:
    'Multi-temporal intelligence synthesis for Sinop Deforestation Frontier (Mato Grosso). Analysis of 7 grounded evidence items confirms consistent multi-indicator clearance activity aligned with transport infrastructure.',
  claims: [
    {
      claim_id: 'clm-obs-1',
      claim_text:
        'Telemetry observation confirmed from source S2A_MSIL2A_20230715T135121 (Optical multispectral scene acquisition).',
      claim_type: 'OBSERVATION',
      epistemic_level: 'AI_INTERPRETED',
      evidence_ids: ['ev-scene-t1'],
      support_status: 'SUPPORTED',
      confidence: 0.98,
      validation_details: { is_valid: true },
    },
    {
      claim_id: 'clm-change-multi',
      claim_text:
        'Canopy vegetation deficit (dNDVI = -0.24) coincides with built-up surface influx (dNDBI = 0.18) across the inspected sector.',
      claim_type: 'CHANGE',
      epistemic_level: 'AI_INTERPRETED',
      evidence_ids: ['ev-ndvi-delta', 'ev-ndbi-delta'],
      support_status: 'SUPPORTED',
      confidence: 0.95,
      validation_details: { is_valid: true },
    },
    {
      claim_id: 'clm-mask-area',
      claim_text:
        'Contiguous spatial difference analysis delineates an affected clearance perimeter of 6.85 km².',
      claim_type: 'MEASUREMENT',
      epistemic_level: 'AI_INTERPRETED',
      evidence_ids: ['ev-change-mask'],
      support_status: 'SUPPORTED',
      confidence: 0.96,
      validation_details: { is_valid: true },
    },
    {
      claim_id: 'clm-road-proximity',
      claim_text:
        'Change area is situated within the right-of-way corridor of Highway BR-163 primary road corridor (85.0 meters proximity).',
      claim_type: 'CORRELATION',
      epistemic_level: 'AI_INTERPRETED',
      evidence_ids: ['ev-road-corridor'],
      support_status: 'SUPPORTED',
      confidence: 0.92,
      validation_details: { is_valid: true },
    },
    {
      claim_id: 'clm-forecast-proj',
      claim_text:
        'Calibrated baseline model projects metric value to reach 0.528 by target year 2030.',
      claim_type: 'FORECAST',
      epistemic_level: 'AI_INTERPRETED',
      evidence_ids: ['ev-forecast-2030'],
      support_status: 'SUPPORTED',
      confidence: 0.88,
      validation_details: { is_valid: true },
    },
  ],
  recommendations: [
    {
      recommendation_id: 'rec-001',
      category: 'MONITOR',
      recommendation_text:
        'Maintain scheduled satellite surveillance pass over active BR-163 perimeter.',
      reason:
        'High evidence strength confirms active infrastructure corridor clearance expanding outward.',
      priority: 'HIGH',
      supporting_evidence_ids: ['ev-ndvi-delta', 'ev-road-corridor'],
    },
    {
      recommendation_id: 'rec-002',
      category: 'INVESTIGATE',
      recommendation_text:
        'Perform high-resolution cadastral boundary overlay to verify deforestation concession permits.',
      reason:
        'Clearance perimeter exceeds 6.85 km² within protected ecological buffer zone.',
      priority: 'MEDIUM',
      supporting_evidence_ids: ['ev-change-mask'],
    },
  ],
  uncertainty_statement:
    'Analytical conclusions are strictly grounded in satellite scenes and vector registries. Unpredicted operational variances or cloud obscuration may affect ground-truth timing.',
  temporal_interpretation:
    'Observation span: 2023-07-15T00:00:00Z to 2026-07-18T00:00:00Z.',
  spatial_interpretation:
    'Spatial buffering confirms direct alignment with Highway BR-163 at 85m.',
  forecast_interpretation:
    'Extrapolation under Linear Trend Model (ORBIT-LT-v1) projects continuous trajectory reaching 0.528 [Epistemic: PREDICTED].',
  evidence_package_hash:
    '9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e',
  provider_info: {
    provider: 'ORBIT-LocalReasoner',
    model: 'DeterministicGroundedSynthesizer',
    version: '1.0.0',
    local_first: true,
  },
  provenance: {
    evidence_items_count: 7,
    relationships_count: 5,
    deterministic_synthesis: true,
    prompt_version: 'ORBIT-AI-Prompt-v1',
    provenance_hash_sha256:
      'c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3',
  },
  epistemic_level: 'AI_INTERPRETED',
  created_at: '2026-08-24T03:30:00Z',
};

export const aiService = {
  async getEvidencePackage(aoiId: string, includeContradiction: boolean = false): Promise<EvidencePackage> {
    try {
      const resp = await fetch(`${API_BASE}/evidence/package`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ aoi_id: aoiId, include_contradiction: includeContradiction }),
      });
      if (!resp.ok) throw new Error(`HTTP error ${resp.status}`);
      return await resp.json();
    } catch {
      return {
        ...DEMO_EVIDENCE_PACKAGE,
        aoi_id: aoiId,
        has_contradictions: includeContradiction,
      };
    }
  },

  async generateInterpretation(
    aoiId: string,
    interpretationType: string = 'GENERAL_EVALUATION',
    userPrompt?: string
  ): Promise<AIInterpretationResult> {
    try {
      const resp = await fetch(`${API_BASE}/interpret`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          aoi_id: aoiId,
          interpretation_type: interpretationType,
          user_prompt: userPrompt,
        }),
      });
      if (!resp.ok) throw new Error(`HTTP error ${resp.status}`);
      return await resp.json();
    } catch {
      return {
        ...DEMO_AI_INTERPRETATION,
        aoi_id: aoiId,
      };
    }
  },

  async generateReport(
    aoiId: string,
    title: string = 'ORBIT Grounded Intelligence Report',
    reportFormat: 'MARKDOWN' | 'JSON' = 'MARKDOWN'
  ): Promise<ReportResult> {
    try {
      const resp = await fetch(`${API_BASE}/reports/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          aoi_id: aoiId,
          title: title,
          report_format: reportFormat,
        }),
      });
      if (!resp.ok) throw new Error(`HTTP error ${resp.status}`);
      return await resp.json();
    } catch {
      return {
        report_id: 'rpt-demo-001',
        aoi_id: aoiId,
        title: title,
        report_type: 'EXECUTIVE_BRIEF',
        report_format: reportFormat,
        content_text: `# ORBIT GEOSPATIAL INTELLIGENCE REPORT\n**Title:** ${title}\n**AOI ID:** ${aoiId}\n\n## 1. Executive Summary\n${DEMO_AI_INTERPRETATION.executive_summary}\n\n## 2. Grounded Claims\n- Canopy deficit calculated at -0.24 (ev-ndvi-delta)\n- Road proximity at 85m (ev-road-corridor)\n\n*(TEST FIXTURE - SIMULATED FOR DEVELOPMENT VERIFICATION)*`,
        provenance_hash_sha256: 'a1b2c3d4e5f60718293a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e',
        created_at: new Date().toISOString(),
      };
    }
  },
};
