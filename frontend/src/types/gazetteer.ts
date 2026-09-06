export interface Coordinates {
  lat: float;
  lng: float;
}

export type float = number;

export interface MapCameraTarget {
  center: Coordinates;
  zoom: number;
  bounding_box?: [number, number, number, number] | null; // [min_lng, min_lat, max_lng, max_lat]
}

export interface SearchResultItem {
  id: string;
  entity_type: string;
  name: string;
  display_name: string;
  administrative_context?: string | null;
  country_code?: string | null;
  country_name?: string | null;
  provider: string;
  coordinates: Coordinates;
  bounding_box?: [number, number, number, number] | null;
  population?: number | null;
  relevance_score: number;
  match_type: string;
  camera_target: MapCameraTarget;
  source_attribution: string;
}

export interface SearchResponse {
  query: string;
  normalized_query: string;
  total_results: number;
  results: SearchResultItem[];
  attribution_notice: string;
}

export interface SearchCategoryGroup {
  category: 'PLACES' | 'ROADS' | 'AOIS' | 'PROJECTS' | 'COORDINATES';
  items: SearchResultItem[];
}
