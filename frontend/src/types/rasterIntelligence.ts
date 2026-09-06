export type EpistemicClassification = 'OBSERVED' | 'CALCULATED' | 'DETECTED' | 'PREDICTED' | 'AI_INTERPRETATION';

export interface RasterDistributionStatistics {
  min: number | null;
  max: number | null;
  mean: number | null;
  median: number | null;
  std_dev: number | null;
  percentile_10: number | null;
  percentile_25: number | null;
  percentile_50: number | null;
  percentile_75: number | null;
  percentile_90: number | null;
  valid_pixel_count: number;
  nodata_pixel_count: number;
  total_pixel_count: number;
  valid_pixel_percentage: number;
  pixel_area_m2: number;
  total_valid_area_km2: number;
  area_calculation_method: string;
}

export interface VegetationIntelligenceSummary {
  index_name: string;
  distribution: RasterDistributionStatistics;
  non_vegetated_area_km2: number;
  non_vegetated_percentage: number;
  low_vegetation_area_km2: number;
  low_vegetation_percentage: number;
  moderate_vegetation_area_km2: number;
  moderate_vegetation_percentage: number;
  dense_vegetation_area_km2: number;
  dense_vegetation_percentage: number;
  total_vegetated_area_km2: number;
  total_vegetated_percentage: number;
  epistemic_level: 'CALCULATED';
}

export interface WaterIntelligenceSummary {
  index_name: string;
  distribution: RasterDistributionStatistics;
  water_candidate_pixel_count: number;
  water_candidate_area_km2: number;
  water_candidate_percentage: number;
  non_water_area_km2: number;
  non_water_percentage: number;
  epistemic_level: 'CALCULATED';
}

export interface UrbanIntelligenceSummary {
  index_name: string;
  distribution: RasterDistributionStatistics;
  built_up_candidate_pixel_count: number;
  built_up_candidate_area_km2: number;
  built_up_candidate_percentage: number;
  non_built_up_area_km2: number;
  non_built_up_percentage: number;
  epistemic_level: 'CALCULATED';
}

export interface IndexCalculationResult {
  index_name: string;
  formula: string;
  scene_id: string;
  platform: string;
  sensor: string;
  acquisition_datetime?: string | null;
  aoi_bounds_wgs84: number[];
  window_dimensions: number[];
  statistics: RasterDistributionStatistics;
  vegetation_summary?: VegetationIntelligenceSummary | null;
  water_summary?: WaterIntelligenceSummary | null;
  urban_summary?: UrbanIntelligenceSummary | null;
  provenance: Record<string, any>;
  epistemic_level: 'CALCULATED';
  calculated_at: string;
}

export interface TimePointMeasurement {
  acquisition_datetime: string;
  metric_name: string;
  value: number;
  unit: string;
  source_scene_id: string;
  platform: string;
  sensor: string;
  cloud_cover?: number | null;
  valid_pixel_percentage: number;
  epistemic_level: 'CALCULATED';
}

export interface TemporalMeasurementSeries {
  aoi_id?: string | null;
  aoi_name?: string | null;
  metric_name: string;
  unit: string;
  data_points: TimePointMeasurement[];
  total_observations: number;
  temporal_coverage_start?: string | null;
  temporal_coverage_end?: string | null;
  trend_slope_per_year?: number | null;
  observation_gaps: Array<{
    gap_start: string;
    gap_end: string;
    duration_days: number;
    reason: string;
  }>;
  quality_summary: Record<string, any>;
  epistemic_level: 'CALCULATED';
}
