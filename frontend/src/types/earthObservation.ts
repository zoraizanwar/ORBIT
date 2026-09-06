export type SensingModality = 'OPTICAL_MULTISPECTRAL' | 'SAR_MICROWAVE' | 'HYBRID_FUSION';

export interface NormalizedBand {
  name: string;
  common_name?: string | null;
  center_wavelength_nm?: number | null;
  polarization?: string | null;
}

export interface RasterAssetReference {
  asset_key: string;
  href: string;
  media_type?: string | null;
  roles: string[];
  title?: string | null;
  band?: NormalizedBand | null;
  gsd?: number | null;
  nodata?: number | null;
  file_size_bytes?: number | null;
  checksum?: string | null;
  is_cloud_optimized: boolean;
  access_method: string;
}

export interface NormalizedImageryScene {
  provider: string;
  dataset_id: string;
  collection_id: string;
  item_id: string;
  platform: string;
  sensor: string;
  modality: SensingModality;
  acquisition_datetime: string;
  processing_datetime?: string | null;
  geometry: GeoJSON.Polygon | GeoJSON.MultiPolygon;
  bbox: [number, number, number, number];
  cloud_cover?: number | null;
  spatial_resolution: number;
  processing_level: string;
  bands: NormalizedBand[];
  assets: Record<string, RasterAssetReference>;
  thumbnail_url?: string | null;
  stac_version: string;
  license: string;
  attribution: string;
  provider_url?: string | null;
  metadata_payload: Record<string, any>;
  source_checksum?: string | null;
  epistemic_level: 'OBSERVED';
  geometry_repaired: boolean;
}

export interface RankedImageryScene {
  scene: NormalizedImageryScene;
  rank_score: number;
  temporal_score: number;
  cloud_cover_score: number;
  spatial_score: number;
  resolution_score: number;
  ranking_explanation: string;
  is_test_fixture: boolean;
}

export interface SceneRankingCriteria {
  temporal_proximity_weight: number;
  cloud_cover_weight: number;
  spatial_coverage_weight: number;
  resolution_weight: number;
}

export interface STACSearchRequest {
  collections?: string[];
  bbox?: [number, number, number, number];
  datetime_start?: string;
  datetime_end?: string;
  cloud_cover_max?: number;
  limit?: number;
  modality?: SensingModality;
  platform?: string;
  provider?: string;
}

export interface STACSearchResponse {
  query: STACSearchRequest;
  total_matched: number;
  returned_count: number;
  scenes: NormalizedImageryScene[];
  providers_contacted: string[];
  attribution_summary: string[];
}

export interface RankedSearchResponse {
  query: STACSearchRequest;
  total_matched: number;
  ranked_scenes: RankedImageryScene[];
  providers_contacted: string[];
  attribution_summary: string[];
}

export interface AcquiredAssetRecord {
  asset_key: string;
  source_url: string;
  local_path: string;
  file_size_bytes: number;
  sha256_checksum: string;
  acquisition_timestamp: string;
  mime_type?: string | null;
  is_test_fixture: boolean;
  metadata: Record<string, any>;
}

export interface RasterValidationReport {
  is_valid: boolean;
  source_uri: string;
  file_size_bytes: number;
  sha256_checksum: string;
  driver?: string | null;
  width?: number | null;
  height?: number | null;
  band_count?: number | null;
  dtype?: string | null;
  crs?: string | null;
  bounds?: [number, number, number, number] | null;
  resolution_x?: number | null;
  resolution_y?: number | null;
  nodata_value?: number | null;
  is_tiled: boolean;
  validation_issues: string[];
  metadata_summary: Record<string, any>;
}

export interface RealPipelineRunRequest {
  aoi_id: string;
  aoi_name: string;
  aoi_geometry: Record<string, any>;
  t1_scene_id: string;
  t1_band_paths: Record<string, string>;
  t1_datetime: string;
  t2_scene_id: string;
  t2_band_paths: Record<string, string>;
  t2_datetime: string;
  platform?: string;
  sensor?: string;
  nearby_road_distance_m?: number;
  is_test_fixture?: boolean;
}
