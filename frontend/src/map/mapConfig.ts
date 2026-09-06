import { CameraState, LayerToggleState } from './mapTypes';

export const MAP_CONFIG = {
  // Global Planetary Overview Camera Default
  defaultWorldCamera: {
    center: [0, 20] as [number, number],
    zoom: 1.8,
    bearing: 0,
    pitch: 0,
  } satisfies CameraState,

  // Demo AOI Initial Framing (Mato Grosso Northern Sector)
  defaultAoiCamera: {
    center: [-54.78, -11.52] as [number, number],
    zoom: 8.5,
    bearing: 0,
    pitch: 0,
  } satisfies CameraState,

  // Canonical Constraints
  minZoom: 1.0,
  maxZoom: 22.0,
  maxPitch: 60,

  // Default Layer Toggles
  defaultLayers: {
    basemapLabels: true,
    adminBoundaries: true,
    coordinateGrid: false,
    roadsMotorway: true,
    roadsPrimary: true,
    roadsSecondary: true,
    roadsLocal: true,
    aoiBoundary: true,
    opticalTrueColor: true,
    sarCoherence: false,
    changeDetectionMask: true,
    historicalArchiveOverlay: false,
    futureProjectionOverlay: false,
  } satisfies LayerToggleState,

  // Dynamic Coordinate Precision Formatter by Zoom Level
  getCoordinatePrecision(zoom: number): number {
    if (zoom < 5) return 2;
    if (zoom < 10) return 4;
    if (zoom < 15) return 5;
    return 6;
  },

  // Authoritative Coordinate Reference Systems
  CRS: {
    STORAGE: 'EPSG:4326',
    RENDERING: 'EPSG:3857',
    GEODESIC: 'WGS84 Ellipsoid',
  },

  // MapTiler Basemap Engine Provider Specification
  MAPTILER: {
    API_KEY_ENV_VAR: 'VITE_MAPTILER_API_KEY',
    STYLES: {
      TACTICAL_DARK: 'dataviz-dark',
      SCIENTIFIC_LIGHT: 'dataviz-light',
      SATELLITE: 'satellite',
      HYBRID: 'hybrid',
      OUTDOOR: 'outdoor',
    },
    ATTRIBUTION:
      '&copy; <a href="https://www.maptiler.com/copyright/" target="_blank">MapTiler</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors</a>',
  },
};
