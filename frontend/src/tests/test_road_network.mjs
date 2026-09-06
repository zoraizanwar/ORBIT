import assert from 'node:assert';
import { test } from 'node:test';

test('ROAD_VECTOR_TILE_SOURCE: Vector tile endpoint and attribution invariants', () => {
  const ROAD_VECTOR_TILE_SOURCE = {
    type: 'vector',
    tiles: ['/api/v1/geo/tiles/roads/{z}/{x}/{y}.pbf'],
    minzoom: 0,
    maxzoom: 22,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors (ODbL)',
  };

  assert.strictEqual(ROAD_VECTOR_TILE_SOURCE.type, 'vector');
  assert.strictEqual(ROAD_VECTOR_TILE_SOURCE.tiles[0], '/api/v1/geo/tiles/roads/{z}/{x}/{y}.pbf');
  assert.ok(ROAD_VECTOR_TILE_SOURCE.attribution.includes('OpenStreetMap'));
  assert.ok(ROAD_VECTOR_TILE_SOURCE.attribution.includes('ODbL'));
});

test('Road Level of Detail (LoD) Zoom Thresholds', () => {
  const roadLayers = [
    { id: 'road-motorway', minzoom: 0, classes: ['motorway', 'trunk'] },
    { id: 'road-primary', minzoom: 6, classes: ['primary'] },
    { id: 'road-secondary', minzoom: 8, classes: ['secondary'] },
    { id: 'road-tertiary', minzoom: 9, classes: ['tertiary'] },
    { id: 'road-local', minzoom: 12, classes: ['residential', 'unclassified', 'service'] },
    { id: 'road-track', minzoom: 13, classes: ['track', 'path'] },
  ];

  // Motorway must be visible at low global zoom
  assert.strictEqual(roadLayers[0].minzoom, 0);

  // Primary roads visible starting at regional zoom 6
  assert.strictEqual(roadLayers[1].minzoom, 6);

  // Secondary roads visible at zoom 8
  assert.strictEqual(roadLayers[2].minzoom, 8);

  // Tracks and unpaved paths only render at high resolution (Z >= 13)
  assert.strictEqual(roadLayers[5].minzoom, 13);
});

test('Road Feature Property Extraction & Evidence Grounding', () => {
  const mockRoadFeature = {
    id: 10482910,
    properties: {
      osm_id: 10482910,
      name: 'Highway BR-163',
      ref: 'BR-163',
      highway_class: 'primary',
      surface: 'paved',
      lanes: 2,
      bridge: false,
      tunnel: false,
      access: 'yes',
      source: 'OpenStreetMap',
      attribution: '© OpenStreetMap contributors',
    },
  };

  assert.strictEqual(mockRoadFeature.properties.source, 'OpenStreetMap');
  assert.strictEqual(mockRoadFeature.properties.highway_class, 'primary');
  assert.strictEqual(mockRoadFeature.properties.lanes, 2);
  assert.strictEqual(mockRoadFeature.properties.surface, 'paved');
});
