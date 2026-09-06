import type { StyleSpecification } from 'maplibre-gl';
import { MapThemeMode } from './mapTypes';

// Authoritative Cartographic Attribution Strings
export const MAPTILER_ATTRIBUTION =
  '&copy; <a href="https://www.maptiler.com/copyright/" target="_blank" rel="noopener noreferrer">MapTiler</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap contributors</a>';

export const OPENSTREETMAP_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors';

/**
 * Builds a MapTiler Vector Style JSON URL.
 */
export const getMapTilerStyleUrl = (styleName: string, apiKey: string): string => {
  return `https://api.maptiler.com/maps/${styleName}/style.json?key=${apiKey}`;
};

/**
 * Builds a MapTiler Raster Style Specification for MapLibre GL JS.
 * Uses MapTiler's high-performance dataviz-dark / dataviz-light raster tile server.
 */
export const getMapTilerRasterStyle = (
  theme: MapThemeMode,
  apiKey: string
): StyleSpecification => {
  const isDark = theme === 'TACTICAL_DARK';
  const styleId = isDark ? 'dataviz-dark' : 'dataviz-light';
  const sourceId = isDark ? 'maptiler-dark-basemap' : 'maptiler-light-basemap';
  const layerId = isDark ? 'maptiler-dark-raster-layer' : 'maptiler-light-raster-layer';
  const bgColor = isDark ? '#080C10' : '#F8FAFC';

  return {
    version: 8,
    name: `ORBIT ${isDark ? 'Tactical Dark' : 'Scientific Light'} (MapTiler)`,
    metadata: {
      'orbit:theme': theme,
      'orbit:provider': 'MapTiler / OpenStreetMap Contributors',
      'orbit:license': 'Open Database License (ODbL 1.0) & MapTiler Terms of Service',
    },
    sources: {
      [sourceId]: {
        type: 'raster',
        tiles: [
          `https://api.maptiler.com/maps/${styleId}/256/{z}/{x}/{y}.png?key=${apiKey}`,
          `https://api.maptiler.com/maps/${styleId}/256/{z}/{x}/{y}@2x.png?key=${apiKey}`,
        ],
        tileSize: 256,
        attribution: MAPTILER_ATTRIBUTION,
        maxzoom: 20,
      },
    },
    layers: [
      {
        id: 'background-void',
        type: 'background',
        paint: {
          'background-color': bgColor,
        },
      },
      {
        id: layerId,
        type: 'raster',
        source: sourceId,
        paint: {
          'raster-opacity': isDark ? 0.95 : 0.98,
          'raster-contrast': isDark ? 0.1 : 0.05,
        },
      },
    ],
  };
};

/**
 * Fallback Baseline Style when MapTiler API Key is not configured.
 * Renders standard OpenStreetMap tiles with dark/light tone adjustments.
 */
export const getFallbackStyle = (theme: MapThemeMode): StyleSpecification => {
  const isDark = theme === 'TACTICAL_DARK';
  const sourceId = isDark ? 'fallback-osm-dark' : 'fallback-osm-light';
  const layerId = isDark ? 'fallback-osm-dark-raster-layer' : 'fallback-osm-light-raster-layer';

  return {
    version: 8,
    name: `ORBIT ${isDark ? 'Tactical Dark' : 'Scientific Light'} (OSM Fallback)`,
    metadata: {
      'orbit:theme': theme,
      'orbit:provider': 'OpenStreetMap Contributors (Fallback - Set VITE_MAPTILER_API_KEY)',
      'orbit:license': 'Open Database License (ODbL 1.0)',
    },
    sources: {
      [sourceId]: {
        type: 'raster',
        tiles: [
          'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
          'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
          'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
        ],
        tileSize: 256,
        attribution: OPENSTREETMAP_ATTRIBUTION,
        maxzoom: 19,
      },
    },
    layers: [
      {
        id: 'background-void',
        type: 'background',
        paint: {
          'background-color': isDark ? '#080C10' : '#F8FAFC',
        },
      },
      {
        id: layerId,
        type: 'raster',
        source: sourceId,
        paint: {
          'raster-opacity': isDark ? 0.88 : 0.95,
          'raster-contrast': isDark ? 0.15 : 0.0,
          'raster-brightness-max': isDark ? 0.45 : 1.0,
        },
      },
    ],
  };
};

/**
 * Resolves the active MapLibre StyleSpecification based on theme mode and API key.
 */
export const getMapStyleByTheme = (
  theme: MapThemeMode,
  apiKey?: string
): StyleSpecification => {
  const key = apiKey ?? (typeof import.meta !== 'undefined' ? (import.meta as any).env?.VITE_MAPTILER_API_KEY : '') ?? '';
  const trimmedKey = typeof key === 'string' ? key.trim() : '';

  if (trimmedKey.length > 0) {
    return getMapTilerRasterStyle(theme, trimmedKey);
  }
  return getFallbackStyle(theme);
};

// Backwards-compatible static exports (evaluate with available environment key or fallback)
export const TACTICAL_DARK_STYLE: StyleSpecification = getMapStyleByTheme('TACTICAL_DARK');
export const SCIENTIFIC_LIGHT_STYLE: StyleSpecification = getMapStyleByTheme('SCIENTIFIC_LIGHT');
