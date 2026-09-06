export type ChangeMetric =
  | 'NDVI'
  | 'NDWI'
  | 'NDBI'
  | 'SAVI'
  | 'SURFACE_WATER_AREA'
  | 'VEGETATED_AREA'
  | 'BUILT_UP_AREA'
  | 'CUSTOM';

export type ChangeClass =
  | 'NO_CHANGE'
  | 'INCREASE'
  | 'DECREASE'
  | 'SIGNIFICANT_INCREASE'
  | 'SIGNIFICANT_DECREASE'
  | 'INVALID'
  | 'INSUFFICIENT_DATA';

export interface ChangeComparisonResult {
  aoi_id?: string | null;
  aoi_name?: string | null;
  metric: ChangeMetric;
  unit: string;
  t1_acquisition: string;
  t2_acquisition: string;
  interval_days: number;
  t1_scene_id: string;
  t2_scene_id: string;
  t1_platform: string;
  t2_platform: string;
  t1_value: number;
  t2_value: number;
  absolute_delta: number;
  relative_change?: number | null;
  percentage_change?: number | null;
  classification: ChangeClass;
  is_significant: boolean;
  threshold_used: Record<string, any>;
  quality_assessment: Record<string, any>;
  provenance: Record<string, any>;
  epistemic_level: 'CALCULATED';
}

export interface SpatialChangeStatistics {
  valid_pixel_count: number;
  nodata_pixel_count: number;
  total_pixel_count: number;
  valid_pixel_percentage: number;

  no_change_pixels: number;
  no_change_percentage: number;
  no_change_area_km2: number;

  increase_pixels: number;
  increase_percentage: number;
  increase_area_km2: number;

  significant_increase_pixels: number;
  significant_increase_percentage: number;
  significant_increase_area_km2: number;

  decrease_pixels: number;
  decrease_percentage: number;
  decrease_area_km2: number;

  significant_decrease_pixels: number;
  significant_decrease_percentage: number;
  significant_decrease_area_km2: number;

  min_delta?: number | null;
  max_delta?: number | null;
  mean_delta?: number | null;
  median_delta?: number | null;
  std_dev_delta?: number | null;

  pixel_area_m2: number;
  total_valid_area_km2: number;
  area_calculation_method: string;
}

export interface SpatialChangeMaskResult {
  metric: ChangeMetric;
  t1_scene_id: string;
  t2_scene_id: string;
  t1_acquisition?: string | null;
  t2_acquisition?: string | null;
  dimensions: number[];
  crs: string;
  statistics: SpatialChangeStatistics;
  threshold_config: Record<string, any>;
  provenance: Record<string, any>;
  epistemic_level: 'CALCULATED';
  calculated_at: string;
}

export interface DetectedChangeEvent {
  id: string;
  analysis_run_id: string;
  change_type: string;
  affected_area_km2: number;
  percentage_change?: number | null;
  confidence: number;
  evidence_strength: 'STRONG' | 'MODERATE' | 'LIMITED' | 'INSUFFICIENT';
  detection_method: string;
  before_date: string;
  after_date: string;
  epistemic_level: 'CALCULATED';
  created_at?: string;
}
