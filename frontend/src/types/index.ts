// ==============================================================================
// ORBIT Geospatial Intelligence: Frontend Domain Type Definitions
// Synchronized with Phase 3 PostgreSQL/PostGIS Schemas
// ==============================================================================

export type UserRole = 'ANALYST' | 'RESEARCHER' | 'ADMIN' | 'VIEWER';
export type ProjectStatus = 'ACTIVE' | 'ARCHIVED' | 'COMPLETED';
export type SensingModality = 'OPTICAL' | 'SAR' | 'DEM' | 'VECTOR' | 'MULTISPECTRAL';
export type AnalysisStatus = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
export type EpistemicLevel = 'OBSERVED' | 'CALCULATED' | 'DETECTED' | 'ESTIMATED' | 'PREDICTED' | 'AI_INTERPRETATION';
export type EvidenceStrength = 'STRONG' | 'MODERATE' | 'LIMITED' | 'INSUFFICIENT';
export type SupportClassification = 'STRONGLY_SUPPORTED' | 'PARTIALLY_SUPPORTED' | 'ESTIMATED' | 'UNAVAILABLE';
export type FuturePredictionType = 'URBAN_EXPANSION' | 'VEGETATION_TREND' | 'WATER_COVERAGE' | 'ROAD_DEVELOPMENT' | 'LAND_USE_CHANGE';
export type IslamicSourceGrade = 'QURAN' | 'MUTAWATIR_HADITH' | 'AHAD_SAHIH' | 'SCHOLARLY_IJMA' | 'HISTORICAL_TARIKH' | 'UNVERIFIED_ISRAILIYYAT';
export type ReportStatus = 'PENDING' | 'GENERATING' | 'COMPLETED' | 'FAILED';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface Project {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
}

export interface AreaOfInterest {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  surface_area_km2: number;
  centroid_lat?: number;
  centroid_lon?: number;
  bounding_box?: [number, number, number, number];
  created_at: string;
}

export interface RoadFeature {
  id: string;
  osm_id: number;
  highway_class: string;
  name?: string;
  ref?: string;
  surface?: string;
  lanes?: number;
  length_m: number;
  oneway: boolean;
  bridge: boolean;
  tunnel: boolean;
}

export interface DatasetRegistry {
  id: string;
  provider: string;
  dataset_name: string;
  dataset_version?: string;
  modality: SensingModality;
  description?: string;
  license: string;
  attribution: string;
  terms_url?: string;
  redistribution_allowed: boolean;
  commercial_use_allowed: boolean;
  active: boolean;
}

export interface ImageryScene {
  id: string;
  dataset_id: string;
  provider_scene_id: string;
  acquisition_datetime: string;
  platform: string;
  sensor: string;
  modality: SensingModality;
  cloud_cover?: number;
  processing_level: string;
  spatial_resolution: number;
  thumbnail_url?: string;
  asset_url?: string;
}

export interface AnalysisRun {
  id: string;
  project_id: string;
  area_of_interest_id: string;
  status: AnalysisStatus;
  analysis_type: string;
  start_date: string;
  end_date: string;
  parameters: Record<string, unknown>;
  pipeline_version: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface Measurement {
  id: string;
  analysis_run_id: string;
  measurement_type: string;
  value: number;
  unit: string;
  uncertainty?: number;
  epistemic_level: EpistemicLevel;
  methodology: string;
  source: string;
  created_at: string;
}

export interface DetectedChange {
  id: string;
  analysis_run_id: string;
  change_type: string;
  affected_area: number;
  percentage_change?: number;
  confidence: number;
  evidence_strength: EvidenceStrength;
  detection_method: string;
  before_date: string;
  after_date: string;
}

export interface GeographicEvent {
  id: string;
  analysis_run_id: string;
  event_type: string;
  severity?: string;
  confidence: number;
  evidence_strength: EvidenceStrength;
  start_date: string;
  end_date: string;
  description?: string;
  affected_area_km2?: number;
}

export interface EvidenceRecord {
  id: string;
  analysis_run_id: string;
  source_type: string;
  source_id: string;
  claim_type: string;
  claim_reference: string;
  input_checksum: string;
  processing_version: string;
  algorithm: string;
  evidence_strength: EvidenceStrength;
  created_at: string;
}

export interface HistoricalAnnualSummary {
  id: string;
  area_of_interest_id: string;
  year: number;
  support_classification: SupportClassification;
  summary_data: {
    mean_ndvi?: number;
    mean_ndwi?: number;
    mean_ndbi?: number;
    built_up_km2?: number;
    vegetation_km2?: number;
    water_km2?: number;
    new_roads_km?: number;
    discrete_events_count?: number;
  };
  data_sources: {
    sentinel_scenes_count?: number;
    landsat_scenes_count?: number;
    cloud_mean_percent?: number;
  };
}

export interface FuturePrediction {
  id: string;
  area_of_interest_id: string;
  prediction_type: FuturePredictionType;
  target_year: number;
  prediction_value: number;
  lower_bound?: number;
  upper_bound?: number;
  unit: string;
  model_name: string;
  model_version: string;
  training_start_year: number;
  training_end_year: number;
  confidence: number;
  evidence_strength: EvidenceStrength;
  scenario: string;
  assumptions: Record<string, string>;
  limitations: Record<string, string>;
}

export interface GeologicalEpoch {
  id: string;
  name: string;
  start_age: number; // Millions of years ago (Ma)
  end_age: number;
  description: string;
  evidence_type: string;
  source: string;
  confidence: number;
}

export interface IslamicGeographicRecord {
  id: string;
  title: string;
  source_type: string;
  classification: IslamicSourceGrade;
  description: string;
  date_reference?: string;
  geographic_reference: string;
  source: string;
  source_url?: string;
  scholarly_notes?: string;
  confidence: number;
}

export interface Report {
  id: string;
  analysis_run_id: string;
  title: string;
  report_type: string;
  status: ReportStatus;
  executive_summary?: string;
  file_path?: string;
  generated_at?: string;
  created_at: string;
}

export type NavigationSection =
  | 'overview'
  | 'map'
  | 'projects'
  | 'analyses'
  | 'changes'
  | 'infrastructure'
  | 'environment'
  | 'events'
  | 'evidence'
  | 'timeline'
  | 'history'
  | 'deep_history'
  | 'islamic_sources'
  | 'predictions'
  | 'scenarios'
  | 'reports'
  | 'exports'
  | 'datasets'
  | 'health'
  | 'settings';
