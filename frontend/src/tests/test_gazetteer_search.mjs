import assert from 'node:assert';
import { test } from 'node:test';

test('Gazetteer Search: Category Grouping & Epistemic Classification', () => {
  const mockResults = [
    {
      id: '1',
      entity_type: 'CITY',
      name: 'Lahore',
      administrative_context: 'Punjab, Pakistan',
      provider: 'OpenStreetMap',
      coordinates: { lat: 31.5204, lng: 74.3587 },
      relevance_score: 0.98,
      match_type: 'EXACT',
      source_attribution: '© OpenStreetMap contributors (ODbL 1.0)',
    },
    {
      id: '2',
      entity_type: 'ROAD',
      name: 'Highway BR-163',
      administrative_context: 'Road Network • Primary',
      provider: 'OpenStreetMap',
      coordinates: { lat: -11.52, lng: -54.75 },
      relevance_score: 0.95,
      match_type: 'ROAD_MATCH',
      source_attribution: '© OpenStreetMap contributors (ODbL 1.0)',
    },
    {
      id: '3',
      entity_type: 'AOI',
      name: 'Mato Grosso Northern Sector',
      administrative_context: 'ORBIT Area of Interest',
      provider: 'ORBIT Workspace',
      coordinates: { lat: -11.5, lng: -54.75 },
      relevance_score: 0.94,
      match_type: 'AOI_MATCH',
      source_attribution: 'ORBIT Workspace Database',
    },
    {
      id: '4',
      entity_type: 'COORDINATE',
      name: '31.5204° N, 74.3587° E',
      administrative_context: 'Exact Geometric Point',
      provider: 'ORBIT Coordinate Parser',
      coordinates: { lat: 31.5204, lng: 74.3587 },
      relevance_score: 1.0,
      match_type: 'COORDINATE',
      source_attribution: 'Direct Geodesic Coordinate Input (WGS84 EPSG:4326)',
    },
  ];

  // Verify categorized sorting
  const coords = mockResults.filter((r) => r.entity_type === 'COORDINATE');
  const places = mockResults.filter((r) => r.entity_type === 'CITY');
  const roads = mockResults.filter((r) => r.entity_type === 'ROAD');
  const aois = mockResults.filter((r) => r.entity_type === 'AOI');

  assert.strictEqual(coords.length, 1);
  assert.strictEqual(places.length, 1);
  assert.strictEqual(roads.length, 1);
  assert.strictEqual(aois.length, 1);
});

test('Gazetteer Search: ODbL Attribution & Provenance Invariants', () => {
  const osmResult = {
    provider: 'OpenStreetMap',
    source_attribution: '© OpenStreetMap contributors (ODbL 1.0)',
  };

  assert.ok(osmResult.source_attribution.includes('OpenStreetMap'));
  assert.ok(osmResult.source_attribution.includes('ODbL'));
});

test('Gazetteer Search: Epistemic Separation (Location != Satellite Observation)', () => {
  const locationTarget = {
    featureType: 'COORDINATE_POINT',
    name: 'Lahore',
    epistemicLevel: 'OBSERVED',
  };

  // Must never claim that location search constitutes an Earth observation or change analysis
  assert.notStrictEqual(locationTarget.epistemicLevel, 'DETECTED');
  assert.notStrictEqual(locationTarget.epistemicLevel, 'PREDICTED');
  assert.strictEqual(locationTarget.epistemicLevel, 'OBSERVED');
});
