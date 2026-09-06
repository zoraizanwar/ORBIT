import {
  IntelligenceObjectResult,
  AnalyzePayload,
} from '../types/intelligence';

const API_BASE = '/api/v1/intelligence';

export const DEMO_INTELLIGENCE_FIXTURES: IntelligenceObjectResult[] = [
  {
    id: 'intel-demo-001',
    analysis_run_id: 'run-demo-001',
    area_of_interest_id: 'aoi-sinop-mato-grosso',
    intelligence_type: 'URBAN_EXPANSION',
    title: 'Multi-Indicator Urban Expansion Candidate (Sinop Periphery)',
    affected_area_km2: 6.85,
    start_date: '2023-07-15T00:00:00Z',
    end_date: '2026-07-18T00:00:00Z',
    evidence_strength: 'STRONG',
    epistemic_level: 'CALCULATED',
    confidence: 0.94,
    rule_id: 'RULE_MULTI_URBAN_EXPANSION_v1',
    rule_version: '1.0.0',
    algorithm_version: 'ORBIT-Intelligence-v1.0',
    spatial_context: {
      nearby_roads_count: 3,
      closest_road_name: 'Highway BR-163',
      closest_road_class: 'primary',
      distance_to_closest_road_m: 85.0,
      intersects_road_corridor: true,
      road_corridor_buffer_m: 500.0,
      spatial_relationship: 'INTERSECTS_CORRIDOR',
    },
    temporal_context: {
      start_date: '2023-07-15T00:00:00Z',
      end_date: '2026-07-18T00:00:00Z',
      interval_days: 1099,
      temporal_alignment: 'AUTHORITATIVE_INTERVAL',
      temporal_tolerance_days: 45,
    },
    quality_metadata: {
      evidence_sources_count: 3,
      supporting_edges_count: 2,
      contradiction_edges_count: 0,
      data_completeness_pct: 99.1,
      fixture_notice: 'TEST FIXTURE - SIMULATED FOR DEVELOPMENT VERIFICATION',
    },
    provenance: {
      rule_id: 'RULE_MULTI_URBAN_EXPANSION_v1',
      rule_version: '1.0.0',
      algorithm_version: 'ORBIT-Intelligence-v1.0',
      epistemic_level: 'CALCULATED',
      deterministic_pipeline: true,
      ai_interpretation_invoked: false,
    },
    evidence_graph: {
      nodes: [
        {
          id: 'intel-demo-001',
          node_type: 'ANALYSIS_RESULT',
          label: 'Root Intelligence Object',
          source_identifier: 'analysis_run:run-demo-001',
          epistemic_level: 'CALCULATED',
          evidence_strength: 'STRONG',
          acquisition_datetime: '2026-07-18T00:00:00Z',
          properties: { metric: 'Multi-Indicator Synthesis' },
        },
        {
          id: 'ev-ndvi-001',
          node_type: 'CHANGE_EVENT',
          label: 'dNDVI Canopy Deficit (-0.24)',
          source_identifier: 'Sentinel-2 L2A',
          epistemic_level: 'CALCULATED',
          evidence_strength: 'STRONG',
          properties: { delta: -0.24, metric: 'NDVI' },
        },
        {
          id: 'ev-ndbi-001',
          node_type: 'CHANGE_EVENT',
          label: 'dNDBI Built-Up Influx (+0.18)',
          source_identifier: 'Sentinel-2 L2A',
          epistemic_level: 'CALCULATED',
          evidence_strength: 'STRONG',
          properties: { delta: 0.18, metric: 'NDBI' },
        },
        {
          id: 'ev-road-001',
          node_type: 'ROAD_DATA',
          label: 'Corridor: Highway BR-163',
          source_identifier: 'OpenStreetMap (ODbL)',
          epistemic_level: 'OBSERVED',
          evidence_strength: 'STRONG',
          properties: { distance_m: 85.0, highway_class: 'primary' },
        },
      ],
      edges: [
        {
          id: 'edge-001',
          source_node_id: 'ev-ndvi-001',
          target_node_id: 'intel-demo-001',
          relationship_type: 'SUPPORTS',
          weight: 1.0,
          metadata_payload: { indicator: 'Vegetation Loss' },
          provenance: { formula: 'NDVI_T2 - NDVI_T1' },
        },
        {
          id: 'edge-002',
          source_node_id: 'ev-ndbi-001',
          target_node_id: 'intel-demo-001',
          relationship_type: 'CORROBORATES',
          weight: 1.0,
          metadata_payload: { indicator: 'Impervious Surface' },
          provenance: { formula: 'NDBI_T2 - NDBI_T1' },
        },
        {
          id: 'edge-003',
          source_node_id: 'ev-road-001',
          target_node_id: 'intel-demo-001',
          relationship_type: 'LOCATED_IN',
          weight: 0.9,
          metadata_payload: { buffer_dist_m: 85.0 },
          provenance: { algorithm: 'PostGIS ST_DWithin' },
        },
      ],
      has_contradictions: false,
      contradiction_count: 0,
    },
    status: 'ACTIVE',
    created_at: '2026-08-24T02:00:00Z',
  },
  {
    id: 'intel-demo-002',
    analysis_run_id: 'run-demo-002',
    area_of_interest_id: 'aoi-lake-mead',
    intelligence_type: 'WATER_CHANGE',
    title: 'Surface Water Recession Event (Lake Mead Basin)',
    affected_area_km2: 14.30,
    start_date: '2022-06-10T00:00:00Z',
    end_date: '2025-06-12T00:00:00Z',
    evidence_strength: 'STRONG',
    epistemic_level: 'CALCULATED',
    confidence: 0.96,
    rule_id: 'RULE_WATER_CHANGE_v1',
    rule_version: '1.0.0',
    algorithm_version: 'ORBIT-Intelligence-v1.0',
    spatial_context: {
      nearby_roads_count: 0,
      closest_road_name: null,
      closest_road_class: null,
      distance_to_closest_road_m: null,
      intersects_road_corridor: false,
      road_corridor_buffer_m: 500.0,
      spatial_relationship: 'DISJOINT',
    },
    temporal_context: {
      start_date: '2022-06-10T00:00:00Z',
      end_date: '2025-06-12T00:00:00Z',
      interval_days: 1098,
      temporal_alignment: 'AUTHORITATIVE_INTERVAL',
      temporal_tolerance_days: 45,
    },
    quality_metadata: {
      evidence_sources_count: 2,
      supporting_edges_count: 2,
      contradiction_edges_count: 0,
      data_completeness_pct: 98.4,
      fixture_notice: 'TEST FIXTURE - SIMULATED FOR DEVELOPMENT VERIFICATION',
    },
    provenance: {
      rule_id: 'RULE_WATER_CHANGE_v1',
      rule_version: '1.0.0',
      algorithm_version: 'ORBIT-Intelligence-v1.0',
      epistemic_level: 'CALCULATED',
      deterministic_pipeline: true,
      ai_interpretation_invoked: false,
    },
    evidence_graph: {
      nodes: [
        {
          id: 'intel-demo-002',
          node_type: 'ANALYSIS_RESULT',
          label: 'Water Contraction Analysis',
          source_identifier: 'analysis_run:run-demo-002',
          epistemic_level: 'CALCULATED',
          evidence_strength: 'STRONG',
          acquisition_datetime: '2025-06-12T00:00:00Z',
          properties: { metric: 'Hydrological Contraction' },
        },
        {
          id: 'ev-ndwi-002',
          node_type: 'CHANGE_EVENT',
          label: 'dNDWI Water Contraction (-0.31)',
          source_identifier: 'Landsat-8/9 OLI',
          epistemic_level: 'CALCULATED',
          evidence_strength: 'STRONG',
          properties: { delta: -0.31, metric: 'NDWI' },
        },
      ],
      edges: [
        {
          id: 'edge-004',
          source_node_id: 'ev-ndwi-002',
          target_node_id: 'intel-demo-002',
          relationship_type: 'SUPPORTS',
          weight: 1.0,
          metadata_payload: { indicator: 'Surface Water Desiccation' },
          provenance: { formula: 'NDWI_T2 - NDWI_T1' },
        },
      ],
      has_contradictions: false,
      contradiction_count: 0,
    },
    status: 'ACTIVE',
    created_at: '2026-08-24T02:05:00Z',
  },
  {
    id: 'intel-demo-003',
    analysis_run_id: 'run-demo-003',
    area_of_interest_id: 'aoi-amazon-canopy',
    intelligence_type: 'VEGETATION_CHANGE',
    title: 'Disputed Canopy Dynamics (Optical Deficit vs SAR Stable)',
    affected_area_km2: 3.20,
    start_date: '2024-01-10T00:00:00Z',
    end_date: '2025-01-15T00:00:00Z',
    evidence_strength: 'INSUFFICIENT',
    epistemic_level: 'CALCULATED',
    confidence: 0.50,
    rule_id: 'RULE_VEGETATION_CHANGE_v1',
    rule_version: '1.0.0',
    algorithm_version: 'ORBIT-Intelligence-v1.0',
    spatial_context: {
      nearby_roads_count: 0,
      closest_road_name: null,
      closest_road_class: null,
      distance_to_closest_road_m: null,
      intersects_road_corridor: false,
      road_corridor_buffer_m: 500.0,
      spatial_relationship: 'DISJOINT',
    },
    temporal_context: {
      start_date: '2024-01-10T00:00:00Z',
      end_date: '2025-01-15T00:00:00Z',
      interval_days: 371,
      temporal_alignment: 'AUTHORITATIVE_INTERVAL',
      temporal_tolerance_days: 45,
    },
    quality_metadata: {
      evidence_sources_count: 2,
      supporting_edges_count: 1,
      contradiction_edges_count: 1,
      data_completeness_pct: 95.0,
      fixture_notice: 'TEST FIXTURE - SIMULATED CONTRADICTION CASE',
    },
    provenance: {
      rule_id: 'RULE_VEGETATION_CHANGE_v1',
      rule_version: '1.0.0',
      algorithm_version: 'ORBIT-Intelligence-v1.0',
      epistemic_level: 'CALCULATED',
      deterministic_pipeline: true,
      ai_interpretation_invoked: false,
    },
    evidence_graph: {
      nodes: [
        {
          id: 'intel-demo-003',
          node_type: 'ANALYSIS_RESULT',
          label: 'Disputed Canopy Analysis',
          source_identifier: 'analysis_run:run-demo-003',
          epistemic_level: 'CALCULATED',
          evidence_strength: 'INSUFFICIENT',
          acquisition_datetime: '2025-01-15T00:00:00Z',
          properties: { status: 'CONTRADICTED' },
        },
        {
          id: 'ev-opt-003',
          node_type: 'CHANGE_EVENT',
          label: 'Optical dNDVI Loss (-0.22)',
          source_identifier: 'Sentinel-2 L2A',
          epistemic_level: 'CALCULATED',
          evidence_strength: 'STRONG',
          properties: { delta: -0.22 },
        },
        {
          id: 'ev-sar-003',
          node_type: 'MEASUREMENT',
          label: 'SAR VH Backscatter Invariant (+0.01 dB)',
          source_identifier: 'Sentinel-1 C-Band SAR',
          epistemic_level: 'OBSERVED',
          evidence_strength: 'MODERATE',
          properties: { delta: 0.01 },
        },
      ],
      edges: [
        {
          id: 'edge-005',
          source_node_id: 'ev-opt-003',
          target_node_id: 'intel-demo-003',
          relationship_type: 'SUPPORTS',
          weight: 1.0,
          metadata_payload: { sensor: 'Optical' },
          provenance: { method: 'Spectral dNDVI' },
        },
        {
          id: 'edge-006',
          source_node_id: 'ev-sar-003',
          target_node_id: 'intel-demo-003',
          relationship_type: 'CONTRADICTS',
          weight: 1.0,
          metadata_payload: { conflict: 'No canopy structure loss in radar amplitude' },
          provenance: { method: 'SAR Intensity Tracking' },
        },
      ],
      has_contradictions: true,
      contradiction_count: 1,
    },
    status: 'CONTRADICTED',
    created_at: '2026-08-24T02:10:00Z',
  },
];

export const analyzeIntelligence = async (
  payload: AnalyzePayload
): Promise<IntelligenceObjectResult> => {
  try {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      throw new Error(`Intelligence analysis failed with HTTP ${res.status}`);
    }
    return await res.json();
  } catch {
    // Fallback to primary fixture for local UI workstation preview
    return DEMO_INTELLIGENCE_FIXTURES[0];
  }
};

export const getIntelligenceEvents = async (): Promise<IntelligenceObjectResult[]> => {
  try {
    const res = await fetch(`${API_BASE}/events?limit=20`);
    if (!res.ok) {
      throw new Error(`Failed to list events: HTTP ${res.status}`);
    }
    const data = await res.json();
    if (data.items && data.items.length > 0) {
      return data.items;
    }
    return DEMO_INTELLIGENCE_FIXTURES;
  } catch {
    return DEMO_INTELLIGENCE_FIXTURES;
  }
};
