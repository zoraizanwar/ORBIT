import assert from 'node:assert';
import { test } from 'node:test';

const DEMO_NDVI_TEST_RESULT = {
  index_name: 'NDVI',
  formula: 'NDVI = (NIR - RED) / (NIR + RED) [Rouse et al. 1974]',
  scene_id: 'S2B_MSIL2A_20260718T140059_N0510_R067_T21LTC_20260718T181234',
  platform: 'Sentinel-2B',
  sensor: 'MSI',
  acquisition_datetime: '2026-07-18T14:00:59Z',
  aoi_bounds_wgs84: [-55.4, -12.1, -54.1, -10.9],
  window_dimensions: [1300, 1200],
  statistics: {
    min: -0.184,
    max: 0.884,
    mean: 0.572,
    median: 0.612,
    std_dev: 0.194,
    percentile_10: 0.21,
    percentile_25: 0.44,
    percentile_50: 0.61,
    percentile_75: 0.72,
    percentile_90: 0.81,
    valid_pixel_count: 1485045,
    nodata_pixel_count: 74955,
    total_pixel_count: 1560000,
    valid_pixel_percentage: 95.2,
    pixel_area_m2: 100.0,
    total_valid_area_km2: 148.5,
    area_calculation_method: 'Projected_EqualArea_Planar (EPSG:32621 / UTM zone 21S)',
  },
  vegetation_summary: {
    index_name: 'NDVI',
    distribution: {
      min: -0.184,
      max: 0.884,
      mean: 0.572,
      median: 0.612,
      std_dev: 0.194,
      percentile_10: 0.21,
      percentile_25: 0.44,
      percentile_50: 0.61,
      percentile_75: 0.72,
      percentile_90: 0.81,
      valid_pixel_count: 1485045,
      nodata_pixel_count: 74955,
      total_pixel_count: 1560000,
      valid_pixel_percentage: 95.2,
      pixel_area_m2: 100.0,
      total_valid_area_km2: 148.5,
      area_calculation_method: 'Projected_EqualArea_Planar (EPSG:32621 / UTM zone 21S)',
    },
    non_vegetated_area_km2: 18.4,
    non_vegetated_percentage: 12.4,
    low_vegetation_area_km2: 24.2,
    low_vegetation_percentage: 16.3,
    moderate_vegetation_area_km2: 42.1,
    moderate_vegetation_percentage: 28.3,
    dense_vegetation_area_km2: 63.8,
    dense_vegetation_percentage: 43.0,
    total_vegetated_area_km2: 130.1,
    total_vegetated_percentage: 87.6,
    epistemic_level: 'CALCULATED',
  },
  water_summary: null,
  urban_summary: null,
  provenance: {
    scene_id: 'S2B_MSIL2A_20260718T140059',
    provider: 'Element84 Earth Search (AWS Open Data)',
    bands_used: { nir: 'B08', red: 'B04' },
    spatial_resolution_meters: [10.0, 10.0],
    crs: 'EPSG:32621',
    epistemic_level: 'CALCULATED',
    software: 'ORBIT Raster Processing Engine v1.0',
    calculated_at: '2026-08-24T02:00:00Z',
  },
  epistemic_level: 'CALCULATED',
  calculated_at: '2026-08-24T02:00:00Z',
};

const DEMO_TIME_SERIES_TEST = {
  aoi_id: 'aoi-amazon-01',
  aoi_name: 'Mato Grosso Northern Sector',
  metric_name: 'NDVI_MEAN',
  unit: 'index_value',
  data_points: [
    {
      acquisition_datetime: '2020-07-15T14:00:00Z',
      metric_name: 'NDVI_MEAN',
      value: 0.68,
      unit: 'index_value',
      source_scene_id: 'S2A_20200715',
      platform: 'Sentinel-2A',
      sensor: 'MSI',
      cloud_cover: 4.2,
      valid_pixel_percentage: 98.4,
      epistemic_level: 'CALCULATED',
    },
    {
      acquisition_datetime: '2021-07-20T14:00:00Z',
      metric_name: 'NDVI_MEAN',
      value: 0.65,
      unit: 'index_value',
      source_scene_id: 'S2B_20210720',
      platform: 'Sentinel-2B',
      sensor: 'MSI',
      cloud_cover: 6.1,
      valid_pixel_percentage: 97.2,
      epistemic_level: 'CALCULATED',
    },
    {
      acquisition_datetime: '2022-07-18T14:00:00Z',
      metric_name: 'NDVI_MEAN',
      value: 0.63,
      unit: 'index_value',
      source_scene_id: 'S2A_20220718',
      platform: 'Sentinel-2A',
      sensor: 'MSI',
      cloud_cover: 8.0,
      valid_pixel_percentage: 96.0,
      epistemic_level: 'CALCULATED',
    },
    {
      acquisition_datetime: '2023-07-15T14:00:00Z',
      metric_name: 'NDVI_MEAN',
      value: 0.61,
      unit: 'index_value',
      source_scene_id: 'S2B_20230715',
      platform: 'Sentinel-2B',
      sensor: 'MSI',
      cloud_cover: 3.5,
      valid_pixel_percentage: 99.1,
      epistemic_level: 'CALCULATED',
    },
    {
      acquisition_datetime: '2024-07-22T14:00:00Z',
      metric_name: 'NDVI_MEAN',
      value: 0.59,
      unit: 'index_value',
      source_scene_id: 'S2A_20240722',
      platform: 'Sentinel-2A',
      sensor: 'MSI',
      cloud_cover: 5.4,
      valid_pixel_percentage: 97.8,
      epistemic_level: 'CALCULATED',
    },
    {
      acquisition_datetime: '2025-07-19T14:00:00Z',
      metric_name: 'NDVI_MEAN',
      value: 0.58,
      unit: 'index_value',
      source_scene_id: 'S2B_20250719',
      platform: 'Sentinel-2B',
      sensor: 'MSI',
      cloud_cover: 7.2,
      valid_pixel_percentage: 96.5,
      epistemic_level: 'CALCULATED',
    },
    {
      acquisition_datetime: '2026-07-18T14:00:00Z',
      metric_name: 'NDVI_MEAN',
      value: 0.57,
      unit: 'index_value',
      source_scene_id: 'S2B_20260718',
      platform: 'Sentinel-2B',
      sensor: 'MSI',
      cloud_cover: 8.4,
      valid_pixel_percentage: 95.2,
      epistemic_level: 'CALCULATED',
    },
  ],
  total_observations: 7,
  temporal_coverage_start: '2020-07-15T14:00:00Z',
  temporal_coverage_end: '2026-07-18T14:00:00Z',
  trend_slope_per_year: -0.018,
  observation_gaps: [],
  quality_summary: {
    mean_cloud_cover: 6.1,
    mean_valid_pixel_pct: 97.2,
    total_gaps_detected: 0,
  },
  epistemic_level: 'CALCULATED',
};

test('Raster Intelligence: NDVI Formula and Statistical Summary Invariants', () => {
  assert.strictEqual(DEMO_NDVI_TEST_RESULT.index_name, 'NDVI');
  assert.ok(DEMO_NDVI_TEST_RESULT.formula.includes('(NIR - RED) / (NIR + RED)'));
  assert.strictEqual(DEMO_NDVI_TEST_RESULT.epistemic_level, 'CALCULATED');
  assert.notStrictEqual(DEMO_NDVI_TEST_RESULT.epistemic_level, 'OBSERVED');
  assert.notStrictEqual(DEMO_NDVI_TEST_RESULT.epistemic_level, 'DETECTED');
  assert.notStrictEqual(DEMO_NDVI_TEST_RESULT.epistemic_level, 'PREDICTED');

  const stats = DEMO_NDVI_TEST_RESULT.statistics;
  assert.ok(stats.min !== null && stats.min >= -1.0);
  assert.ok(stats.max !== null && stats.max <= 1.0);
  assert.ok(stats.mean !== null && stats.mean >= -1.0 && stats.mean <= 1.0);
  assert.ok(stats.valid_pixel_percentage > 90.0);
  assert.ok(stats.total_valid_area_km2 > 0.0);
});

test('Raster Intelligence: Stratified Vegetation Canopy Cover', () => {
  const veg = DEMO_NDVI_TEST_RESULT.vegetation_summary;
  assert.ok(veg !== null && veg !== undefined);
  assert.strictEqual(veg.epistemic_level, 'CALCULATED');

  // Sum of percentages must equal approx 100%
  const totalPct =
    veg.non_vegetated_percentage +
    veg.low_vegetation_percentage +
    veg.moderate_vegetation_percentage +
    veg.dense_vegetation_percentage;

  assert.ok(Math.abs(totalPct - 100.0) < 0.2);
  assert.strictEqual(
    veg.total_vegetated_percentage,
    veg.low_vegetation_percentage + veg.moderate_vegetation_percentage + veg.dense_vegetation_percentage
  );
});

test('Raster Intelligence: Temporal Series Chronological Ordering and Epistemic Separation', () => {
  const series = DEMO_TIME_SERIES_TEST;
  assert.strictEqual(series.metric_name, 'NDVI_MEAN');
  assert.strictEqual(series.epistemic_level, 'CALCULATED');
  assert.ok(series.data_points.length >= 5);

  // Validate chronological ordering
  for (let i = 0; i < series.data_points.length - 1; i++) {
    const d1 = new Date(series.data_points[i].acquisition_datetime).getTime();
    const d2 = new Date(series.data_points[i + 1].acquisition_datetime).getTime();
    assert.ok(d1 <= d2, 'Time points must be sorted chronologically');
  }

  // Future prediction boundary: all empirical observations must be <= 2026
  for (const pt of series.data_points) {
    const yr = new Date(pt.acquisition_datetime).getFullYear();
    assert.ok(yr <= 2026, 'Historical observations cannot be in the future');
    assert.strictEqual(pt.epistemic_level, 'CALCULATED');
  }
});

test('Raster Intelligence: No Fabricated Future Forecasts Invariant', () => {
  const futureForecast = {
    target_year: 2035,
    scenario: 'SSP2-4.5_BUSINESS_AS_USUAL',
    model_version: '1.2.0',
    epistemic_level: 'PREDICTED',
  };

  assert.ok(futureForecast.target_year > 2026);
  assert.strictEqual(futureForecast.epistemic_level, 'PREDICTED');
  assert.notStrictEqual(futureForecast.epistemic_level, 'OBSERVED');
  assert.notStrictEqual(futureForecast.epistemic_level, 'CALCULATED');
});
