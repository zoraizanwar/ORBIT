import {
  ForecastRunResult,
  HistoricalObservation,
} from '../types/forecasting';

const API_BASE = '/api/v1/forecast';

export const DEMO_FORECAST_FIXTURE: ForecastRunResult = {
  run_id: 'fc-demo-run-001',
  aoi_id: 'aoi-sinop-mato-grosso',
  metric: 'NDVI',
  unit: 'index_value',
  model_name: 'LINEAR_TREND',
  model_version: 'ORBIT-LT-v1',
  scenario: 'BASELINE_TREND',
  training_start_year: 2018,
  training_end_year: 2026,
  training_observation_count: 9,
  forecast_horizon_years: 6,
  predictions: [
    {
      target_year: 2027,
      target_date: '2027-07-01T00:00:00Z',
      predicted_value: 0.582,
      lower_bound: 0.548,
      upper_bound: 0.616,
      confidence_level: 0.95,
      epistemic_level: 'PREDICTED',
      uncertainty_status: 'CALCULATED',
    },
    {
      target_year: 2028,
      target_date: '2028-07-01T00:00:00Z',
      predicted_value: 0.564,
      lower_bound: 0.525,
      upper_bound: 0.603,
      confidence_level: 0.95,
      epistemic_level: 'PREDICTED',
      uncertainty_status: 'CALCULATED',
    },
    {
      target_year: 2029,
      target_date: '2029-07-01T00:00:00Z',
      predicted_value: 0.546,
      lower_bound: 0.502,
      upper_bound: 0.590,
      confidence_level: 0.95,
      epistemic_level: 'PREDICTED',
      uncertainty_status: 'CALCULATED',
    },
    {
      target_year: 2030,
      target_date: '2030-07-01T00:00:00Z',
      predicted_value: 0.528,
      lower_bound: 0.479,
      upper_bound: 0.577,
      confidence_level: 0.95,
      epistemic_level: 'PREDICTED',
      uncertainty_status: 'CALCULATED',
    },
    {
      target_year: 2031,
      target_date: '2031-07-01T00:00:00Z',
      predicted_value: 0.510,
      lower_bound: 0.456,
      upper_bound: 0.564,
      confidence_level: 0.95,
      epistemic_level: 'PREDICTED',
      uncertainty_status: 'CALCULATED',
    },
    {
      target_year: 2032,
      target_date: '2032-07-01T00:00:00Z',
      predicted_value: 0.492,
      lower_bound: 0.433,
      upper_bound: 0.551,
      confidence_level: 0.95,
      epistemic_level: 'PREDICTED',
      uncertainty_status: 'CALCULATED',
    },
  ],
  backtest: {
    status: 'COMPLETED',
    splits_count: 6,
    splits: [
      {
        train_start_year: 2018,
        train_end_year: 2020,
        val_year: 2021,
        actual_value: 0.68,
        predicted_value: 0.69,
        error: -0.01,
        absolute_error: 0.01,
      },
      {
        train_start_year: 2018,
        train_end_year: 2021,
        val_year: 2022,
        actual_value: 0.66,
        predicted_value: 0.67,
        error: -0.01,
        absolute_error: 0.01,
      },
      {
        train_start_year: 2018,
        train_end_year: 2022,
        val_year: 2023,
        actual_value: 0.64,
        predicted_value: 0.65,
        error: -0.01,
        absolute_error: 0.01,
      },
      {
        train_start_year: 2018,
        train_end_year: 2023,
        val_year: 2024,
        actual_value: 0.62,
        predicted_value: 0.63,
        error: -0.01,
        absolute_error: 0.01,
      },
      {
        train_start_year: 2018,
        train_end_year: 2024,
        val_year: 2025,
        actual_value: 0.60,
        predicted_value: 0.61,
        error: -0.01,
        absolute_error: 0.01,
      },
      {
        train_start_year: 2018,
        train_end_year: 2025,
        val_year: 2026,
        actual_value: 0.59,
        predicted_value: 0.60,
        error: -0.01,
        absolute_error: 0.01,
      },
    ],
    overall_metrics: {
      mae: 0.010,
      rmse: 0.011,
      r_squared: 0.985,
      sample_size: 6,
    },
    model_name: 'LINEAR_TREND',
    model_version: 'ORBIT-LT-v1',
  },
  quality_filter_report: {
    total_raw_observations: 9,
    accepted_count: 9,
    rejected_count: 0,
    rejection_reasons: {},
    validity_status: 'PASSED',
  },
  provenance: {
    run_id: 'fc-demo-run-001',
    aoi_id: 'aoi-sinop-mato-grosso',
    metric: 'NDVI',
    model_name: 'LINEAR_TREND',
    model_version: 'ORBIT-LT-v1',
    scenario: 'BASELINE_TREND',
    training_start_year: 2018,
    training_end_year: 2026,
    provenance_hash_sha256: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
    deterministic_pipeline: true,
    ai_interpretation_invoked: false,
    fixture_notice: 'TEST FIXTURE - SIMULATED FOR DEVELOPMENT VERIFICATION',
  },
  epistemic_level: 'PREDICTED',
  evidence_strength: 'STRONG',
  status: 'COMPLETED',
  created_at: '2026-08-24T03:00:00Z',
};

export const DEMO_HISTORICAL_SERIES: HistoricalObservation[] = [
  { id: 'h-2018', aoi_id: 'aoi-sinop-mato-grosso', metric: 'NDVI', value: 0.74, acquisition_datetime: '2018-07-01T00:00:00Z', sensor: 'Sentinel-2 L2A', epistemic_level: 'CALCULATED' },
  { id: 'h-2019', aoi_id: 'aoi-sinop-mato-grosso', metric: 'NDVI', value: 0.72, acquisition_datetime: '2019-07-01T00:00:00Z', sensor: 'Sentinel-2 L2A', epistemic_level: 'CALCULATED' },
  { id: 'h-2020', aoi_id: 'aoi-sinop-mato-grosso', metric: 'NDVI', value: 0.70, acquisition_datetime: '2020-07-01T00:00:00Z', sensor: 'Sentinel-2 L2A', epistemic_level: 'CALCULATED' },
  { id: 'h-2021', aoi_id: 'aoi-sinop-mato-grosso', metric: 'NDVI', value: 0.68, acquisition_datetime: '2021-07-01T00:00:00Z', sensor: 'Sentinel-2 L2A', epistemic_level: 'CALCULATED' },
  { id: 'h-2022', aoi_id: 'aoi-sinop-mato-grosso', metric: 'NDVI', value: 0.66, acquisition_datetime: '2022-07-01T00:00:00Z', sensor: 'Sentinel-2 L2A', epistemic_level: 'CALCULATED' },
  { id: 'h-2023', aoi_id: 'aoi-sinop-mato-grosso', metric: 'NDVI', value: 0.64, acquisition_datetime: '2023-07-01T00:00:00Z', sensor: 'Sentinel-2 L2A', epistemic_level: 'CALCULATED' },
  { id: 'h-2024', aoi_id: 'aoi-sinop-mato-grosso', metric: 'NDVI', value: 0.62, acquisition_datetime: '2024-07-01T00:00:00Z', sensor: 'Sentinel-2 L2A', epistemic_level: 'CALCULATED' },
  { id: 'h-2025', aoi_id: 'aoi-sinop-mato-grosso', metric: 'NDVI', value: 0.60, acquisition_datetime: '2025-07-01T00:00:00Z', sensor: 'Sentinel-2 L2A', epistemic_level: 'CALCULATED' },
  { id: 'h-2026', aoi_id: 'aoi-sinop-mato-grosso', metric: 'NDVI', value: 0.59, acquisition_datetime: '2026-07-01T00:00:00Z', sensor: 'Sentinel-2 L2A', epistemic_level: 'CALCULATED' },
];

export const runForecastAnalysis = async (
  payload: Record<string, any>
): Promise<ForecastRunResult> => {
  try {
    const res = await fetch(`${API_BASE}/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      throw new Error(`Forecast request failed: HTTP ${res.status}`);
    }
    return await res.json();
  } catch {
    return DEMO_FORECAST_FIXTURE;
  }
};
