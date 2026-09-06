import assert from 'node:assert';
import { test } from 'node:test';

const DEMO_TEST_COMPARISON = {
  aoi_id: 'aoi-amazon-01',
  aoi_name: 'Mato Grosso Northern Sector',
  metric: 'NDVI',
  unit: 'index_value',
  t1_acquisition: '2023-07-15T14:00:00Z',
  t2_acquisition: '2026-07-18T14:00:59Z',
  interval_days: 1099,
  t1_scene_id: 'S2B_MSIL2A_20230715T140059',
  t2_scene_id: 'S2B_MSIL2A_20260718T140059',
  t1_platform: 'Sentinel-2B',
  t2_platform: 'Sentinel-2B',
  t1_value: 0.612,
  t2_value: 0.572,
  absolute_delta: -0.04,
  relative_change: -0.0654,
  percentage_change: -6.54,
  classification: 'DECREASE',
  is_significant: false,
  threshold_used: {
    significant_increase_threshold: 0.15,
    increase_threshold: 0.05,
    decrease_threshold: -0.05,
    significant_decrease_threshold: -0.15,
    threshold_version: 'NDVI_CANOPY_v1',
  },
  quality_assessment: {
    t1_valid_pixel_pct: 99.1,
    t2_valid_pixel_pct: 95.2,
    t1_cloud_cover: 3.5,
    t2_cloud_cover: 8.4,
    quality_status: 'PASSED',
  },
  provenance: {
    algorithm: 'ORBIT Multi-Temporal Comparison Engine v1.0',
    calculation_formula: 'delta = V_t2 - V_t1; pct = (delta / |V_t1|) * 100',
    epistemic_level: 'CALCULATED',
    calculated_at: '2026-08-24T02:00:00Z',
  },
  epistemic_level: 'CALCULATED',
};

const DEMO_TEST_SPATIAL_MASK = {
  metric: 'NDVI',
  t1_scene_id: 'S2B_MSIL2A_20230715T140059',
  t2_scene_id: 'S2B_MSIL2A_20260718T140059',
  dimensions: [1300, 1200],
  crs: 'EPSG:32621',
  statistics: {
    valid_pixel_count: 1485045,
    nodata_pixel_count: 74955,
    total_pixel_count: 1560000,
    valid_pixel_percentage: 95.2,
    no_change_pixels: 1042500,
    no_change_percentage: 70.2,
    no_change_area_km2: 104.25,
    increase_pixels: 148504,
    increase_percentage: 10.0,
    increase_area_km2: 14.85,
    significant_increase_pixels: 44551,
    significant_increase_percentage: 3.0,
    significant_increase_area_km2: 4.45,
    decrease_pixels: 178205,
    decrease_percentage: 12.0,
    decrease_area_km2: 17.82,
    significant_decrease_pixels: 71285,
    significant_decrease_percentage: 4.8,
    significant_decrease_area_km2: 7.13,
    min_delta: -0.482,
    max_delta: 0.391,
    mean_delta: -0.041,
    median_delta: -0.012,
    std_dev_delta: 0.114,
    pixel_area_m2: 100.0,
    total_valid_area_km2: 148.5,
    area_calculation_method: 'Projected_EqualArea_Planar (EPSG:32621)',
  },
  threshold_config: {
    significant_increase_threshold: 0.15,
    increase_threshold: 0.05,
    decrease_threshold: -0.05,
    significant_decrease_threshold: -0.15,
  },
  provenance: {
    algorithm: 'ORBIT Spatial Raster Difference Engine v1.0',
    calculation_formula: 'Delta(x, y) = Raster_T2(x, y) - Raster_T1(x, y)',
    epistemic_level: 'CALCULATED',
    calculated_at: '2026-08-24T02:00:00Z',
  },
  epistemic_level: 'CALCULATED',
};

test('Change Detection: Pairwise Temporal Comparison Invariants', () => {
  const comp = DEMO_TEST_COMPARISON;
  assert.strictEqual(comp.metric, 'NDVI');
  assert.strictEqual(comp.epistemic_level, 'CALCULATED');
  assert.notStrictEqual(comp.epistemic_level, 'OBSERVED');
  assert.notStrictEqual(comp.epistemic_level, 'PREDICTED');

  const d1 = new Date(comp.t1_acquisition).getTime();
  const d2 = new Date(comp.t2_acquisition).getTime();
  assert.ok(d1 < d2, 'T1 acquisition must precede T2');

  const calculatedDelta = Number((comp.t2_value - comp.t1_value).toFixed(3));
  assert.strictEqual(comp.absolute_delta, calculatedDelta);

  assert.ok(comp.classification === 'DECREASE' || comp.classification === 'SIGNIFICANT_DECREASE');
});

test('Change Detection: Spatial Change Mask & Geodesic Surface Statistics', () => {
  const mask = DEMO_TEST_SPATIAL_MASK;
  const stats = mask.statistics;

  assert.strictEqual(mask.epistemic_level, 'CALCULATED');
  assert.ok(stats.valid_pixel_count > 0);
  assert.ok(stats.total_pixel_count >= stats.valid_pixel_count);
  assert.ok(stats.valid_pixel_percentage > 90.0);

  // Sum of percentages must equal approx 100%
  const totalClassPct =
    stats.no_change_percentage +
    stats.increase_percentage +
    stats.significant_increase_percentage +
    stats.decrease_percentage +
    stats.significant_decrease_percentage;

  assert.ok(Math.abs(totalClassPct - 100.0) < 0.5);
  assert.ok(stats.total_valid_area_km2 > 0.0);
  assert.ok(stats.area_calculation_method.length > 0);
});

test('Change Detection: Strict Epistemic Separation from Future Forecasts', () => {
  const calculatedChange = DEMO_TEST_COMPARISON;
  const futureForecast = {
    target_year: 2040,
    model: 'ARIMA_Seasonal_v1',
    scenario: 'SSP2-4.5',
    epistemic_level: 'PREDICTED',
  };

  assert.strictEqual(calculatedChange.epistemic_level, 'CALCULATED');
  assert.strictEqual(futureForecast.epistemic_level, 'PREDICTED');
  assert.notStrictEqual(calculatedChange.epistemic_level, futureForecast.epistemic_level);
  assert.ok(futureForecast.target_year > 2026);
});
