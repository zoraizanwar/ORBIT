import { EpistemicLevel, EvidenceStrength } from './index';

export type IntelligenceType =
  | 'VEGETATION_CHANGE'
  | 'WATER_CHANGE'
  | 'URBAN_EXPANSION'
  | 'URBAN_REDUCTION'
  | 'INFRASTRUCTURE_CHANGE'
  | 'ROAD_CHANGE'
  | 'LAND_USE_CHANGE'
  | 'ENVIRONMENTAL_CHANGE'
  | 'SPATIAL_ANOMALY'
  | 'MULTI_INDICATOR_EVENT';

export type EvidenceType =
  | 'RAW_SCENE'
  | 'RASTER_ASSET'
  | 'MEASUREMENT'
  | 'CHANGE_EVENT'
  | 'SPATIAL_MASK'
  | 'ROAD_DATA'
  | 'INFRASTRUCTURE_DATA'
  | 'HISTORICAL_SOURCE'
  | 'DERIVED_STATISTIC'
  | 'ANALYSIS_RESULT';

export type EvidenceRelationshipType =
  | 'DERIVED_FROM'
  | 'SUPPORTS'
  | 'CORROBORATES'
  | 'CONTRADICTS'
  | 'LOCATED_IN'
  | 'TEMPORALLY_ALIGNS'
  | 'SPATIALLY_OVERLAPS'
  | 'SOURCE_OF';

export interface EvidenceNode {
  id: string;
  node_type: EvidenceType;
  label: string;
  source_identifier: string;
  epistemic_level: EpistemicLevel;
  evidence_strength: EvidenceStrength;
  acquisition_datetime?: string;
  properties: Record<string, any>;
}

export interface EvidenceEdge {
  id: string;
  source_node_id: string;
  target_node_id: string;
  relationship_type: EvidenceRelationshipType;
  weight: number;
  metadata_payload: Record<string, any>;
  provenance: Record<string, any>;
}

export interface EvidenceGraphResult {
  nodes: EvidenceNode[];
  edges: EvidenceEdge[];
  has_contradictions: boolean;
  contradiction_count: number;
}

export interface SpatialContextResult {
  nearby_roads_count: number;
  closest_road_name?: string | null;
  closest_road_class?: string | null;
  distance_to_closest_road_m?: number | null;
  intersects_road_corridor: boolean;
  road_corridor_buffer_m: number;
  spatial_relationship: string;
}

export interface TemporalContextResult {
  start_date: string;
  end_date: string;
  interval_days: number;
  temporal_alignment: string;
  temporal_tolerance_days: number;
}

export interface IntelligenceObjectResult {
  id: string;
  analysis_run_id: string;
  area_of_interest_id?: string | null;
  intelligence_type: IntelligenceType;
  title: string;
  affected_area_km2: number;
  start_date: string;
  end_date: string;
  evidence_strength: EvidenceStrength;
  epistemic_level: EpistemicLevel;
  confidence: number;
  rule_id: string;
  rule_version: string;
  algorithm_version: string;
  spatial_context: SpatialContextResult;
  temporal_context: TemporalContextResult;
  quality_metadata: Record<string, any>;
  provenance: Record<string, any>;
  evidence_graph: EvidenceGraphResult;
  status: string;
  created_at: string;
}

export interface AnalyzePayload {
  project_id?: string;
  area_of_interest_id?: string;
  aoi_geometry: Record<string, any>;
  target_start_date: string;
  target_end_date: string;
  ndvi_delta?: number;
  ndwi_delta?: number;
  ndbi_delta?: number;
  affected_area_km2?: number;
  primary_sensor?: string;
  secondary_sensor?: string;
  secondary_sensor_signal_delta?: number;
  road_features?: Array<Record<string, any>>;
}
