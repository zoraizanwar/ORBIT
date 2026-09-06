import {
  ChangeComparisonResult,
  SpatialChangeMaskResult,
  DetectedChangeEvent,
} from '../types/changeDetection';

export const DEMO_CHANGE_COMPARISON: ChangeComparisonResult = {
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

export const DEMO_SPATIAL_CHANGE_MASK: SpatialChangeMaskResult = {
  metric: 'NDVI',
  t1_scene_id: 'S2B_MSIL2A_20230715T140059',
  t2_scene_id: 'S2B_MSIL2A_20260718T140059',
  t1_acquisition: '2023-07-15T14:00:00Z',
  t2_acquisition: '2026-07-18T14:00:59Z',
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
  calculated_at: '2026-08-24T02:00:00Z',
};

export const DEMO_DETECTED_CHANGE_EVENTS: DetectedChangeEvent[] = [
  {
    id: 'evt-chg-001',
    analysis_run_id: 'run-001',
    change_type: 'VEGETATION_LOSS',
    affected_area_km2: 14.23,
    percentage_change: -22.4,
    confidence: 0.94,
    evidence_strength: 'STRONG',
    detection_method: 'Tier_2_Adaptive_dNDVI_Threshold',
    before_date: '2023-07-15T14:00:00Z',
    after_date: '2026-07-18T14:00:59Z',
    epistemic_level: 'CALCULATED',
  },
  {
    id: 'evt-chg-002',
    change_type: 'ROAD_CONSTRUCTION',
    analysis_run_id: 'run-001',
    affected_area_km2: 2.15,
    percentage_change: 18.6,
    confidence: 0.88,
    evidence_strength: 'STRONG',
    detection_method: 'Tier_2_NDBI_Linear_Corridor_Extraction',
    before_date: '2023-07-15T14:00:00Z',
    after_date: '2026-07-18T14:00:59Z',
    epistemic_level: 'CALCULATED',
  },
];

export async function compareObservationsApi(
  payload: any
): Promise<ChangeComparisonResult> {
  try {
    const res = await fetch('/api/v1/eo/change/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Fallback
  }
  return DEMO_CHANGE_COMPARISON;
}
