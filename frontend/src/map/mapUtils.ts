import { Coordinates, MapScaleInfo } from './mapTypes';

// Geodesic Scale Calculation on WGS84 Web Mercator
export const calculateGeodesicScale = (latitude: number, zoom: number, targetPixelWidth = 100): MapScaleInfo => {
  // Ground resolution in meters per pixel at latitude and zoom level
  const latRad = (latitude * Math.PI) / 180;
  const metersPerPixel = (156543.03392 * Math.cos(latRad)) / Math.pow(2, zoom);

  const rawMeters = metersPerPixel * targetPixelWidth;

  // Discrete standard metric cartography intervals (meters)
  const intervals = [
    5000000, 2000000, 1000000, 500000, 200000, 100000, 50000, 20000, 10000,
    5000, 2000, 1000, 500, 200, 100, 50, 20, 10, 5, 2, 1,
  ];

  // Find nearest lower standard interval
  let chosenMeters = intervals[intervals.length - 1];
  for (const interval of intervals) {
    if (rawMeters >= interval) {
      chosenMeters = interval;
      break;
    }
  }

  const pixelWidth = Math.round(chosenMeters / metersPerPixel);

  let distanceText = '';
  if (chosenMeters >= 1000) {
    distanceText = `${chosenMeters / 1000} km`;
  } else {
    distanceText = `${chosenMeters} m`;
  }

  return {
    distanceText,
    pixelWidth: Math.max(40, pixelWidth),
  };
};

// Coordinate String Parser: parses "lat, lng" or "[lat, lng]"
export const parseCoordinates = (input: string): Coordinates | null => {
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
};

// Format latitude and longitude coordinates with cardinal direction
export const formatCoordinates = (coords: Coordinates, precision = 4): { latFormatted: string; lngFormatted: string } => {
  const latDir = coords.lat >= 0 ? 'N' : 'S';
  const lngDir = coords.lng >= 0 ? 'E' : 'W';

  const latAbs = Math.abs(coords.lat).toFixed(precision);
  const lngAbs = Math.abs(coords.lng).toFixed(precision);

  return {
    latFormatted: `LAT ${latAbs}° ${latDir}`,
    lngFormatted: `LON ${lngAbs}° ${lngDir}`,
  };
};
