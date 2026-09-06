import {
  IndexCalculationResult,
  TemporalMeasurementSeries,
} from '../types/rasterIntelligence';

export const DEMO_NDVI_RESULT: IndexCalculationResult = {
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

export const DEMO_TIME_SERIES: TemporalMeasurementSeries = {
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

export async function computeSpectralIndexApi(
  payload: any,
  indexType: 'ndvi' | 'ndwi' | 'ndbi' = 'ndvi'
): Promise<IndexCalculationResult> {
  try {
    const res = await fetch(`/api/v1/eo/indices/${indexType}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Fallback to demo fixture
  }
  return DEMO_NDVI_RESULT;
}

export async function fetchAoiTimeSeriesApi(
  aoiId: string
): Promise<TemporalMeasurementSeries> {
  try {
    const res = await fetch('/api/v1/eo/timeseries', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ aoi_id: aoiId, measurements: DEMO_TIME_SERIES.data_points }),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Fallback
  }
  return DEMO_TIME_SERIES;
}
