import type { SourceSpecification } from 'maplibre-gl';

// 1. Area of Interest (AOI) GeoJSON Feature (Mato Grosso Northern Sector)
export const DEMO_AOI_GEOJSON: GeoJSON.FeatureCollection = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'aoi-amazon-01',
      properties: {
        id: 'aoi-amazon-01',
        name: 'Mato Grosso Northern Sector (Demo AOI)',
        surface_area_km2: 14850.45,
        project_id: 'proj-001',
        status: 'ACTIVE',
        crs: 'EPSG:4326',
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-55.4, -12.1],
            [-54.1, -12.1],
            [-54.1, -10.9],
            [-55.4, -10.9],
            [-55.4, -12.1],
          ],
        ],
      },
    },
  ],
};

// 2. OpenStreetMap Dynamic Mapbox Vector Tile (MVT) Source Specification
export const ROAD_VECTOR_TILE_SOURCE: SourceSpecification = {
  type: 'vector',
  tiles: ['/api/v1/geo/tiles/roads/{z}/{x}/{y}.pbf'],
  minzoom: 0,
  maxzoom: 22,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors (ODbL)',
};

// 3. Fallback Seed Road Vectors GeoJSON (Highway BR-163 Primary Corridor & Feeder Tracks)
export const DEMO_ROADS_GEOJSON: GeoJSON.FeatureCollection = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'road-br-163',
      properties: {
        osm_id: 10482910,
        name: 'Highway BR-163 (Cuiaba - Santarem)',
        ref: 'BR-163',
        highway_class: 'primary',
        surface: 'paved',
        lanes: 2,
        length_km: 142.5,
        source: 'OpenStreetMap',
      },
      geometry: {
        type: 'LineString',
        coordinates: [
          [-54.78, -12.1],
          [-54.76, -11.8],
          [-54.75, -11.52],
          [-54.74, -11.2],
          [-54.72, -10.9],
        ],
      },
    },
    {
      type: 'Feature',
      id: 'road-feeder-east-1',
      properties: {
        osm_id: 28491023,
        name: 'Agro-Corridor Feeder Track 1',
        ref: 'TR-01',
        highway_class: 'tertiary',
        surface: 'unpaved',
        lanes: 1,
        length_km: 38.2,
        source: 'OpenStreetMap',
      },
      geometry: {
        type: 'LineString',
        coordinates: [
          [-54.75, -11.52],
          [-54.55, -11.54],
          [-54.35, -11.58],
        ],
      },
    },
    {
      type: 'Feature',
      id: 'road-feeder-west-1',
      properties: {
        osm_id: 28491024,
        name: 'Logging Extension Spur West',
        ref: 'SP-04',
        highway_class: 'track',
        surface: 'ground',
        lanes: 1,
        length_km: 26.4,
        source: 'OpenStreetMap',
      },
      geometry: {
        type: 'LineString',
        coordinates: [
          [-54.76, -11.8],
          [-54.95, -11.85],
          [-55.15, -11.88],
        ],
      },
    },
  ],
};

// 4. Detected Change GeoJSON (dNDVI Vegetation Loss Cluster)
export const DEMO_CHANGE_DETECTION_GEOJSON: GeoJSON.FeatureCollection = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'chg-01',
      properties: {
        id: 'chg-01',
        change_type: 'CANOPY_DEFORESTATION',
        affected_area_km2: 14.23,
        percentage_change: -18.4,
        confidence: 0.94,
        evidence_strength: 'STRONG',
        detection_method: 'Tier_2_Adaptive_Otsu_dNDVI',
        before_date: '2023-07-15',
        after_date: '2026-07-18',
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-54.68, -11.45],
            [-54.60, -11.45],
            [-54.60, -11.38],
            [-54.68, -11.38],
            [-54.68, -11.45],
          ],
        ],
      },
    },
  ],
};

// 5. Active Satellite Scene Footprint GeoJSON (EPSG:4326)
export const DEMO_SCENE_FOOTPRINT_GEOJSON: GeoJSON.FeatureCollection = {
  type: 'FeatureCollection',
  features: [],
};

