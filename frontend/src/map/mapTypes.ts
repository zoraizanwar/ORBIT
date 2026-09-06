// ==============================================================================
// ORBIT Map Engine: Domain Types & State Model (MapLibre GL JS)
// ==============================================================================

export type MapThemeMode = 'TACTICAL_DARK' | 'SCIENTIFIC_LIGHT';

export interface Coordinates {
  lng: number;
  lat: number;
}

export interface CameraState {
  center: [number, number];
  zoom: number;
  bearing: number;
  pitch: number;
}

export interface LayerToggleState {
  // Basemap & Reference
  basemapLabels: boolean;
  adminBoundaries: boolean;
  coordinateGrid: boolean;

  // Infrastructure Hierarchy
  roadsMotorway: boolean;
  roadsPrimary: boolean;
  roadsSecondary: boolean;
  roadsLocal: boolean;

  // Analysis & Earth Observation
  aoiBoundary: boolean;
  opticalTrueColor: boolean;
  sarCoherence: boolean;
  changeDetectionMask: boolean;

  // Temporal & Projections
  historicalArchiveOverlay: boolean;
  futureProjectionOverlay: boolean;
}

export interface FeatureInspectionPayload {
  featureType: 'AOI' | 'ROAD' | 'CHANGE_DETECTION' | 'TELEMETRY_SCENE' | 'COORDINATE_POINT';
  featureId: string;
  name: string;
  coordinates: Coordinates;
  properties: Record<string, unknown>;
  evidenceStrength?: 'STRONG' | 'MODERATE' | 'LIMITED' | 'INSUFFICIENT';
  epistemicLevel?: 'OBSERVED' | 'CALCULATED' | 'DETECTED' | 'ESTIMATED' | 'PREDICTED' | 'AI_INTERPRETATION';
}

export interface MapScaleInfo {
  distanceText: string;
  pixelWidth: number;
}
