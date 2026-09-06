import { SearchResponse, SearchResultItem } from '../types/gazetteer';

const SEED_FALLBACK_RESULTS: SearchResultItem[] = [
  {
    id: 'seed-lahore',
    entity_type: 'CITY',
    name: 'Lahore',
    display_name: 'Lahore, Punjab, Pakistan',
    administrative_context: 'Punjab, Pakistan',
    country_code: 'PK',
    country_name: 'Pakistan',
    provider: 'OpenStreetMap',
    coordinates: { lat: 31.5204, lng: 74.3587 },
    bounding_box: [74.15, 31.35, 74.55, 31.65],
    population: 11126285,
    relevance_score: 0.98,
    match_type: 'EXACT',
    camera_target: {
      center: { lat: 31.5204, lng: 74.3587 },
      zoom: 11.5,
      bounding_box: [74.15, 31.35, 74.55, 31.65],
    },
    source_attribution: '© OpenStreetMap contributors (ODbL 1.0)',
  },
  {
    id: 'seed-br-163',
    entity_type: 'ROAD',
    name: 'Highway BR-163 (Cuiaba - Santarem)',
    display_name: 'Highway BR-163 [BR-163], Mato Grosso, Brazil',
    administrative_context: 'Road Network • Primary',
    country_code: 'BR',
    country_name: 'Brazil',
    provider: 'OpenStreetMap',
    coordinates: { lat: -11.52, lng: -54.75 },
    bounding_box: [-54.78, -12.1, -54.72, -10.9],
    population: null,
    relevance_score: 0.95,
    match_type: 'ROAD_MATCH',
    camera_target: {
      center: { lat: -11.52, lng: -54.75 },
      zoom: 13.0,
      bounding_box: [-54.78, -12.1, -54.72, -10.9],
    },
    source_attribution: '© OpenStreetMap contributors (ODbL 1.0)',
  },
  {
    id: 'seed-mato-grosso',
    entity_type: 'STATE',
    name: 'Mato Grosso',
    display_name: 'Mato Grosso, Brazil',
    administrative_context: 'Central-West Region, Brazil',
    country_code: 'BR',
    country_name: 'Brazil',
    provider: 'OpenStreetMap',
    coordinates: { lat: -12.68, lng: -55.42 },
    bounding_box: [-61.6, -18.0, -50.2, -7.3],
    population: 3567234,
    relevance_score: 0.92,
    match_type: 'EXACT',
    camera_target: {
      center: { lat: -12.68, lng: -55.42 },
      zoom: 6.5,
      bounding_box: [-61.6, -18.0, -50.2, -7.3],
    },
    source_attribution: '© OpenStreetMap contributors (ODbL 1.0)',
  },
  {
    id: 'seed-aoi-amazon',
    entity_type: 'AOI',
    name: 'Mato Grosso Northern Sector',
    display_name: 'AOI: Mato Grosso Northern Sector (14,850.5 km²)',
    administrative_context: 'ORBIT Area of Interest',
    country_code: 'BR',
    country_name: 'Brazil',
    provider: 'ORBIT Workspace',
    coordinates: { lat: -11.5, lng: -54.75 },
    bounding_box: [-55.4, -12.1, -54.1, -10.9],
    population: null,
    relevance_score: 0.94,
    match_type: 'AOI_MATCH',
    camera_target: {
      center: { lat: -11.5, lng: -54.75 },
      zoom: 10.5,
      bounding_box: [-55.4, -12.1, -54.1, -10.9],
    },
    source_attribution: 'ORBIT Workspace Database',
  },
];

export async function searchLocationsApi(
  query: string,
  signal?: AbortSignal
): Promise<SearchResponse> {
  const trimmed = query.trim();
  if (!trimmed) {
    return {
      query: '',
      normalized_query: '',
      total_results: 0,
      results: [],
      attribution_notice: 'ORBIT Global Search Engine',
    };
  }

  try {
    const res = await fetch(`/api/v1/geo/search?q=${encodeURIComponent(trimmed)}&limit=15`, {
      signal,
      headers: { Accept: 'application/json' },
    });

    if (res.ok) {
      const data: SearchResponse = await res.json();
      return data;
    }
  } catch {
    // Graceful fallback to client-side seed index if network is unavailable
  }

  // Client-side search simulation over seed data
  const lower = trimmed.toLowerCase();
  const matched = SEED_FALLBACK_RESULTS.filter(
    (item) =>
      item.name.toLowerCase().includes(lower) ||
      (item.administrative_context && item.administrative_context.toLowerCase().includes(lower)) ||
      (item.country_name && item.country_name.toLowerCase().includes(lower))
  );

  return {
    query: trimmed,
    normalized_query: lower,
    total_results: matched.length,
    results: matched,
    attribution_notice: 'ORBIT Global Search Engine • Local & OpenStreetMap Data',
  };
}
