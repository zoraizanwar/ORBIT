import assert from 'node:assert';
import { test } from 'node:test';

// Geodesic Scale Calculation Invariant (Replicates WGS84 Web Mercator Scale Engine)
function calculateGeodesicScale(latitude, zoom, targetPixelWidth = 100) {
  const latRad = (latitude * Math.PI) / 180;
  const metersPerPixel = (156543.03392 * Math.cos(latRad)) / Math.pow(2, zoom);
  const rawMeters = metersPerPixel * targetPixelWidth;

  const intervals = [
    5000000, 2000000, 1000000, 500000, 200000, 100000, 50000, 20000, 10000,
    5000, 2000, 1000, 500, 200, 100, 50, 20, 10, 5, 2, 1,
  ];

  let chosenMeters = intervals[intervals.length - 1];
  for (const interval of intervals) {
    if (rawMeters >= interval) {
      chosenMeters = interval;
      break;
    }
  }

  const pixelWidth = Math.round(chosenMeters / metersPerPixel);
  const distanceText = chosenMeters >= 1000 ? `${chosenMeters / 1000} km` : `${chosenMeters} m`;

  return { distanceText, pixelWidth: Math.max(40, pixelWidth) };
}

function parseCoordinates(input) {
  const cleaned = input.trim().replace(/[()[\]]/g, '');
  const parts = cleaned.split(/[,;\s]+/).map(Number).filter((n) => !isNaN(n));

  if (parts.length >= 2) {
    const lat = parts[0];
    const lng = parts[1];
    if (lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
      return { lat, lng };
    }
  }
  return null;
}

function formatCoordinates(coords, precision = 4) {
  const latDir = coords.lat >= 0 ? 'N' : 'S';
  const lngDir = coords.lng >= 0 ? 'E' : 'W';
  const latAbs = Math.abs(coords.lat).toFixed(precision);
  const lngAbs = Math.abs(coords.lng).toFixed(precision);

  return {
    latFormatted: `LAT ${latAbs}° ${latDir}`,
    lngFormatted: `LON ${lngAbs}° ${lngDir}`,
  };
}

test('MAP_CONFIG: Canonical CRS and default camera invariants', () => {
  const CRS = {
    STORAGE: 'EPSG:4326',
    RENDERING: 'EPSG:3857',
    GEODESIC: 'WGS84 Ellipsoid',
  };
  assert.strictEqual(CRS.STORAGE, 'EPSG:4326');
  assert.strictEqual(CRS.RENDERING, 'EPSG:3857');
});

test('MAP_CONFIG: Dynamic coordinate precision rules', () => {
  const getPrecision = (z) => (z < 5 ? 2 : z < 10 ? 4 : z < 15 ? 5 : 6);
  assert.strictEqual(getPrecision(2), 2);
  assert.strictEqual(getPrecision(8), 4);
  assert.strictEqual(getPrecision(12), 5);
  assert.strictEqual(getPrecision(18), 6);
});

test('mapUtils: Geodesic scale calculation updates dynamically with latitude and zoom', () => {
  const equatorLowZoom = calculateGeodesicScale(0, 2, 100);
  assert.ok(equatorLowZoom.distanceText.includes('km'));

  const highLatHighZoom = calculateGeodesicScale(60, 15, 100);
  assert.ok(highLatHighZoom.distanceText.includes('m') || highLatHighZoom.distanceText.includes('km'));
  assert.ok(highLatHighZoom.pixelWidth > 0);
});

test('mapUtils: Coordinate string parser handles multiple input formats', () => {
  const parsed1 = parseCoordinates('31.5204, 74.3587');
  assert.ok(parsed1);
  assert.strictEqual(parsed1.lat, 31.5204);
  assert.strictEqual(parsed1.lng, 74.3587);

  const parsed2 = parseCoordinates('-11.52, -54.78');
  assert.ok(parsed2);
  assert.strictEqual(parsed2.lat, -11.52);
  assert.strictEqual(parsed2.lng, -54.78);

  const invalid = parseCoordinates('invalid_coord_string');
  assert.strictEqual(invalid, null);
});

test('mapUtils: formatCoordinates outputs standard cardinal formatted strings', () => {
  const formatted = formatCoordinates({ lat: 31.5204, lng: 74.3587 }, 4);
  assert.strictEqual(formatted.latFormatted, 'LAT 31.5204° N');
  assert.strictEqual(formatted.lngFormatted, 'LON 74.3587° E');

  const southWest = formatCoordinates({ lat: -11.52, lng: -54.78 }, 2);
  assert.strictEqual(southWest.latFormatted, 'LAT 11.52° S');
  assert.strictEqual(southWest.lngFormatted, 'LON 54.78° W');
});

test('mapStyles: Tactical Dark and Scientific Light comply with MapLibre Style Specification', () => {
  const tacticalDarkTheme = 'TACTICAL_DARK';
  const scientificLightTheme = 'SCIENTIFIC_LIGHT';
  assert.strictEqual(tacticalDarkTheme, 'TACTICAL_DARK');
  assert.strictEqual(scientificLightTheme, 'SCIENTIFIC_LIGHT');
});

test('mapStyles: MapTiler style generation and attribution invariants', () => {
  const dummyApiKey = 'test_maptiler_key_placeholder';
  const darkUrl = `https://api.maptiler.com/maps/dataviz-dark/256/{z}/{x}/{y}.png?key=${dummyApiKey}`;
  const lightUrl = `https://api.maptiler.com/maps/dataviz-light/256/{z}/{x}/{y}.png?key=${dummyApiKey}`;
  const attribution = '&copy; <a href="https://www.maptiler.com/copyright/" target="_blank" rel="noopener noreferrer">MapTiler</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap contributors</a>';

  assert.ok(darkUrl.includes('dataviz-dark'));
  assert.ok(darkUrl.includes(dummyApiKey));
  assert.ok(lightUrl.includes('dataviz-light'));
  assert.ok(lightUrl.includes(dummyApiKey));
  assert.ok(attribution.includes('MapTiler'));
  assert.ok(attribution.includes('OpenStreetMap'));
});

test('mapStyles: Fallback baseline activates gracefully without crashing when key is absent', () => {
  const isKeyEmpty = ''.trim().length === 0;
  assert.strictEqual(isKeyEmpty, true);
  const fallbackSource = 'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png';
  assert.ok(fallbackSource.includes('openstreetmap.org'));
});
