import React, { useEffect, useRef, useState, useCallback } from 'react';
import maplibregl, { Map as MapLibreMap, MapMouseEvent } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

import { Coordinates, LayerToggleState, FeatureInspectionPayload, MapThemeMode } from '../../map/mapTypes';
import { MAP_CONFIG } from '../../map/mapConfig';
import { getMapStyleByTheme } from '../../map/mapStyles';
import { attachOrbitSourcesAndLayers, syncLayerVisibilities } from '../../map/mapLayers';
import { MapControls } from './MapControls';
import { CoordinateInspector } from './CoordinateInspector';
import { MapScaleDisplay } from './MapScaleDisplay';
import { LayerControlPanel } from './LayerControlPanel';

import { NormalizedImageryScene } from '../../types/earthObservation';

interface Props {
  theme: 'dark' | 'light';
  onFeatureSelect?: (payload: FeatureInspectionPayload) => void;
  targetCoordinates?: Coordinates | null;
  selectedScene?: NormalizedImageryScene | null;
}

export const OrbitMap: React.FC<Props> = ({
  theme,
  onFeatureSelect,
  targetCoordinates,
  selectedScene,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);

  const [mapLoaded, setMapLoaded] = useState(false);
  const [initError, setInitError] = useState<string | null>(null);
  const [cursorCoords, setCursorCoords] = useState<Coordinates>({ lat: 0, lng: 0 });
  const [zoomLevel, setZoomLevel] = useState<number>(MAP_CONFIG.defaultWorldCamera.zoom);
  const [centerLat, setCenterLat] = useState<number>(MAP_CONFIG.defaultWorldCamera.center[1]);
  const [bearing, setBearing] = useState<number>(0);
  const [pitch, setPitch] = useState<number>(0);
  const [layers, setLayers] = useState<LayerToggleState>(MAP_CONFIG.defaultLayers);

  const mapTheme: MapThemeMode = theme === 'dark' ? 'TACTICAL_DARK' : 'SCIENTIFIC_LIGHT';

  // 1. Initialize MapLibre GL Map Instance
  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Destroy any existing map instance before re-initializing
    if (mapRef.current) {
      mapRef.current.remove();
      mapRef.current = null;
    }

    // Verify WebGL availability if supported API is exported
    const isSupported = typeof (maplibregl as any).supported === 'function' 
      ? (maplibregl as any).supported() 
      : true;

    if (!isSupported) {
      setInitError('WebGL is not supported or hardware acceleration is disabled in this environment.');
      return;
    }

    const maptilerApiKey = (import.meta as any).env?.VITE_MAPTILER_API_KEY || '';
    if (!maptilerApiKey && import.meta.env.DEV) {
      console.info(
        '[ORBIT Map Engine] VITE_MAPTILER_API_KEY not configured in .env. Running in OpenStreetMap fallback baseline mode.'
      );
    }

    let map: MapLibreMap;
    try {
      map = new maplibregl.Map({
        container: mapContainerRef.current,
        style: getMapStyleByTheme(mapTheme),
        center: MAP_CONFIG.defaultWorldCamera.center,
        zoom: MAP_CONFIG.defaultWorldCamera.zoom,
        bearing: MAP_CONFIG.defaultWorldCamera.bearing,
        pitch: MAP_CONFIG.defaultWorldCamera.pitch,
        minZoom: MAP_CONFIG.minZoom,
        maxZoom: MAP_CONFIG.maxZoom,
        maxPitch: MAP_CONFIG.maxPitch,
        attributionControl: false, // Customized in bottom/style
      });
      mapRef.current = map;
      setInitError(null);
    } catch (err: any) {
      setInitError(err?.message || 'Failed to initialize MapLibre GL rendering engine.');
      return;
    }

    map.on('error', (e) => {
      // Gracefully handle tile 404s or non-fatal style issues in dev mode
      if (import.meta.env.DEV) {
        console.warn('MapLibre GL non-fatal error:', e.error);
      }
    });

    map.on('load', () => {
      setMapLoaded(true);
      attachOrbitSourcesAndLayers(map);
      syncLayerVisibilities(map, layers);
    });

    // Responsive Resize Observer
    let resizeObserver: ResizeObserver | null = null;
    if (typeof ResizeObserver !== 'undefined' && mapContainerRef.current) {
      resizeObserver = new ResizeObserver(() => {
        if (mapRef.current) {
          mapRef.current.resize();
        }
      });
      resizeObserver.observe(mapContainerRef.current);
    }

    // Cursor Coordinate Inspector Handler (Throttled via native pointer event)
    map.on('mousemove', (e: MapMouseEvent) => {
      setCursorCoords({
        lng: Number(e.lngLat.lng.toFixed(6)),
        lat: Number(e.lngLat.lat.toFixed(6)),
      });
    });

    // Viewport & Scale Change Handlers
    map.on('move', () => {
      const center = map.getCenter();
      setZoomLevel(map.getZoom());
      setCenterLat(center.lat);
      setBearing(map.getBearing());
      setPitch(map.getPitch());
    });

    // Feature Click Inspection Handler
    map.on('click', (e: MapMouseEvent) => {
      const bbox: [maplibregl.PointLike, maplibregl.PointLike] = [
        [e.point.x - 5, e.point.y - 5],
        [e.point.x + 5, e.point.y + 5],
      ];

      const queryLayers = [
        'aoi-fill',
        'change-fill',
        'road-motorway',
        'road-primary',
        'road-secondary',
        'road-tertiary',
        'road-local',
        'road-track',
      ];
      const activeQueryLayers = queryLayers.filter((id) => map.getLayer(id));

      const features = map.queryRenderedFeatures(bbox, { layers: activeQueryLayers });

      if (features.length > 0 && onFeatureSelect) {
        const feat = features[0];
        const layerId = feat.layer.id;

        let featureType: FeatureInspectionPayload['featureType'] = 'COORDINATE_POINT';
        let name = 'Selected Feature';
        let evidenceStrength: FeatureInspectionPayload['evidenceStrength'] = 'STRONG';

        if (layerId === 'aoi-fill') {
          featureType = 'AOI';
          name = String(feat.properties?.name || 'Area of Interest');
        } else if (layerId === 'change-fill') {
          featureType = 'CHANGE_DETECTION';
          name = `Detected Change: ${feat.properties?.change_type || 'Canopy Disturbance'}`;
          evidenceStrength = (feat.properties?.evidence_strength as any) || 'STRONG';
        } else if (layerId.startsWith('road-')) {
          featureType = 'ROAD';
          const roadClass = feat.properties?.highway_class || feat.properties?.class || 'road';
          const roadName = feat.properties?.name || feat.properties?.ref;
          name = roadName ? `${roadName} (${roadClass})` : `OSM Road (${roadClass})`;
        }

        onFeatureSelect({
          featureType,
          featureId: String(feat.id || feat.properties?.osm_id || feat.properties?.id || 'feat-01'),
          name,
          coordinates: { lng: e.lngLat.lng, lat: e.lngLat.lat },
          properties: {
            ...feat.properties,
            source: 'OpenStreetMap',
            attribution: '© OpenStreetMap contributors',
          },
          evidenceStrength,
          epistemicLevel: featureType === 'CHANGE_DETECTION' ? 'DETECTED' : 'OBSERVED',
        });
      }
    });

    // Cleanup on component unmount (Strict Mode Safe)
    return () => {
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
      map.remove();
      mapRef.current = null;
    };
  }, []); // Run once on mount

  // 2. React to Theme Changes
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;

    map.setStyle(getMapStyleByTheme(mapTheme));

    // Re-attach custom vector and GeoJSON layers after style replacement
    map.once('style.load', () => {
      attachOrbitSourcesAndLayers(map);
      syncLayerVisibilities(map, layers);
    });
  }, [mapTheme]);

  // 3. React to Target Coordinates Navigation
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !targetCoordinates) return;

    map.flyTo({
      center: [targetCoordinates.lng, targetCoordinates.lat],
      zoom: 12,
      duration: 2000,
      essential: true,
    });
  }, [targetCoordinates]);

  // 4. React to Selected Imagery Scene Footprint
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;

    const source = map.getSource('scene-footprint-source') as maplibregl.GeoJSONSource;
    if (source) {
      if (selectedScene) {
        source.setData({
          type: 'FeatureCollection',
          features: [
            {
              type: 'Feature',
              id: selectedScene.item_id,
              properties: {
                id: selectedScene.item_id,
                platform: selectedScene.platform,
                sensor: selectedScene.sensor,
                cloud_cover: selectedScene.cloud_cover,
                spatial_resolution: selectedScene.spatial_resolution,
              },
              geometry: selectedScene.geometry,
            },
          ],
        });

        // Fit map view to scene bounding box
        if (selectedScene.bbox && selectedScene.bbox.length === 4) {
          const [minLng, minLat, maxLng, maxLat] = selectedScene.bbox;
          map.fitBounds(
            [
              [minLng, minLat],
              [maxLng, maxLat],
            ],
            { padding: 80, duration: 1500 }
          );
        }
      } else {
        source.setData({
          type: 'FeatureCollection',
          features: [],
        });
      }
    }
  }, [selectedScene, mapLoaded]);


  // 4. React to Layer Visibility Toggles
  const handleToggleLayer = useCallback((layerKey: keyof LayerToggleState) => {
    setLayers((prev) => {
      const updated = { ...prev, [layerKey]: !prev[layerKey] };
      const map = mapRef.current;
      if (map && mapLoaded) {
        syncLayerVisibilities(map, updated);
      }
      return updated;
    });
  }, [mapLoaded]);

  // Map Controls Actions
  const handleZoomIn = () => mapRef.current?.zoomIn();
  const handleZoomOut = () => mapRef.current?.zoomOut();
  const handleResetNorth = () => mapRef.current?.resetNorthPitch();
  const handleRecenterAoi = () => {
    mapRef.current?.flyTo({
      center: MAP_CONFIG.defaultAoiCamera.center,
      zoom: MAP_CONFIG.defaultAoiCamera.zoom,
      bearing: 0,
      pitch: 0,
      duration: 2000,
    });
  };
  const handleTogglePitch = () => {
    const map = mapRef.current;
    if (!map) return;
    map.easeTo({ pitch: map.getPitch() > 0 ? 0 : 45, duration: 800 });
  };
  const handleToggleFullscreen = () => {
    if (!document.fullscreenElement) {
      mapContainerRef.current?.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  };

  return (
    <div
      ref={mapContainerRef}
      className="relative w-full h-full bg-orbit-void overflow-hidden select-none outline-none"
      data-testid="orbit-map-container"
    >
      {/* Fallback Initialization Error Banner */}
      {initError && (
        <div
          className="absolute inset-0 z-30 flex flex-col items-center justify-center bg-orbit-void/95 p-6 text-center"
          data-testid="map-init-error"
        >
          <div className="max-w-md p-6 bg-orbit-carbon border border-orbit-critical/40 rounded-xl shadow-2xl">
            <div className="text-xs font-mono font-bold text-orbit-critical uppercase tracking-wider mb-2">
              Map Engine Initialization Notice
            </div>
            <p className="text-xs text-orbit-muted mb-4 font-mono">
              {initError}
            </p>
            <div className="text-[11px] text-orbit-muted/70 font-mono border-t border-orbit-border/40 pt-3">
              ORBIT requires WebGL hardware acceleration to render real-time vector and raster layers.
            </div>
          </div>
        </div>
      )}

      {/* 1. Floating Top Left Controls */}
      <div className="absolute top-4 left-4 z-20">
        <MapControls
          onZoomIn={handleZoomIn}
          onZoomOut={handleZoomOut}
          onResetNorth={handleResetNorth}
          onRecenterAoi={handleRecenterAoi}
          onTogglePitch={handleTogglePitch}
          onToggleFullscreen={handleToggleFullscreen}
          pitch={pitch}
          bearing={bearing}
        />
      </div>

      {/* 2. Floating Top Right Layer Switcher Panel */}
      <div className="absolute top-4 right-4 z-20">
        <LayerControlPanel
          layers={layers}
          onToggleLayer={handleToggleLayer}
        />
      </div>

      {/* 3. Floating Bottom Center Coordinate Inspector HUD */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20">
        <CoordinateInspector
          coordinates={cursorCoords}
          zoom={zoomLevel}
        />
      </div>

      {/* 4. Floating Bottom Left Scale Indicator */}
      <div className="absolute bottom-4 left-4 z-20">
        <MapScaleDisplay
          latitude={centerLat}
          zoom={zoomLevel}
        />
      </div>
    </div>
  );
};
