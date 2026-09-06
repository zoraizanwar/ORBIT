import { EpistemicLevel, EvidenceStrength } from './index';

export type ForecastMetric =
  | 'NDVI'
  | 'NDWI'
  | 'NDBI'
  | 'SAVI'
  | 'VEGETATED_AREA'
  | 'SURFACE_WATER_AREA'
  | 'BUILT_UP_AREA'
  | 'CUSTOM';

export type TemporalResolution = 'MONTHLY' | 'QUARTERLY' | 'ANNUAL';
export type AggregationMethod = 'MEAN' | 'MEDIAN' | 'SUM';
export type ForecastScenarioType =
  | 'BASELINE_TREND'
  | 'SSP2-4.5_BUSINESS_AS_USUAL'
  | 'CONSERVATION_POLICY'
  | 'USER_DEFINED';

export type ForecastStatus = 'COMPLETED' | 'INSUFFICIENT_DATA' | 'FAILED';

export interface HistoricalObservation {
  id: string;
  aoi_id: string;
  metric: ForecastMetric;
  value: number;
  unit?: string;
  acquisition_datetime: string;
  sensor?: string;
  scene_id?: string;
  valid_pixel_pct?: number;
  cloud_cover?: number | null;
  epistemic_level?: EpistemicLevel;
  provenance?: Record<string, any>;
}

export interface QualityFilterReport {
  total_raw_observations: number;
  accepted_count: number;
  rejected_count: number;
  rejection_reasons: Record<string, number>;
  validity_status: string;
}

export interface AggregatedObservation {
  period_key: string;
  year: number;
  month?: number | null;
  quarter?: number | null;
  value: number;
  observation_count: number;
  aggregation_method: AggregationMethod;
  date_start: string;
  date_end: string;
  epistemic_level: EpistemicLevel;
  source_observation_ids: string[];
}

export interface ForecastPredictionPoint {
  target_year: number;
  target_date: string;
  predicted_value: number;
  lower_bound: number | null;
  upper_bound: number | null;
  confidence_level: number;
  epistemic_level: EpistemicLevel; // Strictly PREDICTED
  uncertainty_status: string;
}

export interface ModelEvaluationMetrics {
  mae: number;
  rmse: number;
  r_squared: number;
  sample_size: number;
}

export interface BacktestSplitResult {
  train_start_year: number;
  train_end_year: number;
  val_year: number;
  actual_value: number;
  predicted_value: number;
  error: number;
  absolute_error: number;
}

export interface BacktestReport {
  status: string;
  splits_count: number;
  splits: BacktestSplitResult[];
  overall_metrics: ModelEvaluationMetrics | null;
  model_name: string;
  model_version: string;
}

export interface ForecastRunResult {
  run_id: string;
  aoi_id: string;
  metric: ForecastMetric;
  unit: string;
  model_name: string;
  model_version: string;
  scenario: ForecastScenarioType;
  training_start_year: int_or_number;
  training_end_year: int_or_number;
  training_observation_count: int_or_number;
  forecast_horizon_years: int_or_number;
  predictions: ForecastPredictionPoint[];
  backtest: BacktestReport;
  quality_filter_report: QualityFilterReport;
  provenance: Record<string, any>;
  epistemic_level: EpistemicLevel; // Strictly PREDICTED
  evidence_strength: EvidenceStrength;
  status: ForecastStatus;
  created_at: string;
}

type int_or_number = number;
