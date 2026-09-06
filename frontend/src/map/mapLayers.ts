import type { Map as MapLibreMap, LayerSpecification } from 'maplibre-gl';
import {
  DEMO_AOI_GEOJSON,
  DEMO_ROADS_GEOJSON,
  DEMO_CHANGE_DETECTION_GEOJSON,
  ROAD_VECTOR_TILE_SOURCE,
} from './mapSources';
import { LayerToggleState } from './mapTypes';

export const AOI_FILL_LAYER: LayerSpecification = {
  id: 'aoi-fill',
  type: 'fill',
  source: 'aoi-source',
  paint: {
    'fill-color': '#19C37D',
    'fill-opacity': 0.12,
  },
};

export const AOI_OUTLINE_LAYER: LayerSpecification = {
  id: 'aoi-outline',
  type: 'line',
  source: 'aoi-source',
  paint: {
    'line-color': '#19C37D',
    'line-width': 2,
    'line-dasharray': [3, 2],
  },
};

export const CHANGE_DETECTION_FILL_LAYER: LayerSpecification = {
  id: 'change-fill',
  type: 'fill',
  source: 'change-detection-source',
  paint: {
    'fill-color': '#EF4444',
    'fill-opacity': 0.35,
  },
};

export const CHANGE_DETECTION_OUTLINE_LAYER: LayerSpecification = {
  id: 'change-outline',
  type: 'line',
  source: 'change-detection-source',
  paint: {
    'line-color': '#EF4444',
    'line-width': 2,
  },
};

// ==============================================================================
// Progressive Road Level of Detail (LoD) Vector Layers
// ==============================================================================

export const ROAD_MOTORWAY_LAYER: LayerSpecification = {
  id: 'road-motorway',
  type: 'line',
  source: 'sample-roads-source',
  filter: ['in', 'highway_class', 'motorway', 'trunk'],
  minzoom: 0,
  paint: {
    'line-color': '#F97316',
    'line-width': ['interpolate', ['linear'], ['zoom'], 2, 1.0, 6, 2.0, 12, 4.5, 18, 7.0],
    'line-opacity': 0.95,
  },
};

export const ROAD_PRIMARY_LAYER: LayerSpecification = {
  id: 'road-primary',
  type: 'line',
  source: 'sample-roads-source',
  filter: ['==', 'highway_class', 'primary'],
  minzoom: 6,
  paint: {
    'line-color': '#F59E0B',
    'line-width': ['interpolate', ['linear'], ['zoom'], 6, 1.2, 12, 3.5, 18, 6.0],
    'line-opacity': 0.95,
  },
};

export const ROAD_SECONDARY_LAYER: LayerSpecification = {
  id: 'road-secondary',
  type: 'line',
  source: 'sample-roads-source',
  filter: ['==', 'highway_class', 'secondary'],
  minzoom: 8,
  paint: {
    'line-color': '#38BDF8',
    'line-width': ['interpolate', ['linear'], ['zoom'], 8, 1.0, 14, 3.0, 18, 5.0],
    'line-opacity': 0.9,
  },
};

export const ROAD_TERTIARY_LAYER: LayerSpecification = {
  id: 'road-tertiary',
  type: 'line',
  source: 'sample-roads-source',
  filter: ['==', 'highway_class', 'tertiary'],
  minzoom: 9,
  paint: {
    'line-color': '#10B981',
    'line-width': ['interpolate', ['linear'], ['zoom'], 9, 0.8, 14, 2.5, 18, 4.0],
    'line-opacity': 0.85,
  },
};

export const ROAD_LOCAL_LAYER: LayerSpecification = {
  id: 'road-local',
  type: 'line',
  source: 'sample-roads-source',
  filter: ['in', 'highway_class', 'residential', 'unclassified', 'service'],
  minzoom: 12,
  paint: {
    'line-color': '#94A3B8',
    'line-width': ['interpolate', ['linear'], ['zoom'], 12, 0.8, 16, 2.0],
    'line-opacity': 0.8,
  },
};

export const ROAD_TRACK_LAYER: LayerSpecification = {
  id: 'road-track',
  type: 'line',
  source: 'sample-roads-source',
  filter: ['in', 'highway_class', 'track', 'path'],
  minzoom: 13,
  paint: {
    'line-color': '#EA580C',
    'line-width': 1.5,
    'line-dasharray': [2, 2],
    'line-opacity': 0.85,
  },
};

export const SCENE_FOOTPRINT_FILL_LAYER: LayerSpecification = {
  id: 'scene-footprint-fill',
  type: 'fill',
  source: 'scene-footprint-source',
  paint: {
    'fill-color': '#06B6D4',
    'fill-opacity': 0.15,
  },
};

export const SCENE_FOOTPRINT_OUTLINE_LAYER: LayerSpecification = {
  id: 'scene-footprint-outline',
  type: 'line',
  source: 'scene-footprint-source',
  paint: {
    'line-color': '#06B6D4',
    'line-width': 2,
    'line-dasharray': [4, 2],
  },
};

export const attachOrbitSourcesAndLayers = (map: MapLibreMap) => {
  // 1. Attach GeoJSON and Vector Tile Sources
  if (!map.getSource('aoi-source')) {
    map.addSource('aoi-source', {
      type: 'geojson',
      data: DEMO_AOI_GEOJSON,
    });
  }

  if (!map.getSource('scene-footprint-source')) {
    map.addSource('scene-footprint-source', {
      type: 'geojson',
      data: {
        type: 'FeatureCollection',
        features: [],
      },
    });
  }

  if (!map.getSource('sample-roads-source')) {
    map.addSource('sample-roads-source', {
      type: 'geojson',
      data: DEMO_ROADS_GEOJSON,
    });
  }

  if (!map.getSource('road-vector-source')) {
    try {
      map.addSource('road-vector-source', ROAD_VECTOR_TILE_SOURCE);
    } catch {
      // Graceful fallback if endpoint is starting up
    }
  }

  if (!map.getSource('change-detection-source')) {
    map.addSource('change-detection-source', {
      type: 'geojson',
      data: DEMO_CHANGE_DETECTION_GEOJSON,
    });
  }

  // 2. Attach Analytical & Progressive Road Layers
  if (!map.getLayer('aoi-fill')) map.addLayer(AOI_FILL_LAYER);
  if (!map.getLayer('aoi-outline')) map.addLayer(AOI_OUTLINE_LAYER);
  if (!map.getLayer('scene-footprint-fill')) map.addLayer(SCENE_FOOTPRINT_FILL_LAYER);
  if (!map.getLayer('scene-footprint-outline')) map.addLayer(SCENE_FOOTPRINT_OUTLINE_LAYER);
  if (!map.getLayer('change-fill')) map.addLayer(CHANGE_DETECTION_FILL_LAYER);
  if (!map.getLayer('change-outline')) map.addLayer(CHANGE_DETECTION_OUTLINE_LAYER);

  if (!map.getLayer('road-motorway')) map.addLayer(ROAD_MOTORWAY_LAYER);
  if (!map.getLayer('road-primary')) map.addLayer(ROAD_PRIMARY_LAYER);
  if (!map.getLayer('road-secondary')) map.addLayer(ROAD_SECONDARY_LAYER);
  if (!map.getLayer('road-tertiary')) map.addLayer(ROAD_TERTIARY_LAYER);
  if (!map.getLayer('road-local')) map.addLayer(ROAD_LOCAL_LAYER);
  if (!map.getLayer('road-track')) map.addLayer(ROAD_TRACK_LAYER);
};


export const syncLayerVisibilities = (map: MapLibreMap, layers: LayerToggleState) => {
  const setVisibility = (layerId: string, isVisible: boolean) => {
    if (map.getLayer(layerId)) {
      map.setLayoutProperty(layerId, 'visibility', isVisible ? 'visible' : 'none');
    }
  };

  setVisibility('aoi-fill', layers.aoiBoundary);
  setVisibility('aoi-outline', layers.aoiBoundary);
  setVisibility('change-fill', layers.changeDetectionMask);
  setVisibility('change-outline', layers.changeDetectionMask);

  setVisibility('road-motorway', layers.roadsMotorway);
  setVisibility('road-primary', layers.roadsPrimary);
  setVisibility('road-secondary', layers.roadsSecondary);
  setVisibility('road-tertiary', layers.roadsSecondary);
  setVisibility('road-local', layers.roadsLocal);
  setVisibility('road-track', layers.roadsLocal);
};
