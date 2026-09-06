import React, { useState, useEffect } from 'react';
import { Satellite } from 'lucide-react';
import { OrbitMap } from '../components/map/OrbitMap';
import { IntelligencePanel } from '../components/intelligence/IntelligencePanel';
import { OrbitTimeline } from '../components/timeline/OrbitTimeline';
import { ImageryDiscoveryPanel } from '../components/eo/ImageryDiscoveryPanel';
import { Coordinates, FeatureInspectionPayload } from '../map/mapTypes';
import { NormalizedImageryScene } from '../types/earthObservation';

interface Props {
  theme?: 'dark' | 'light';
  targetCoordinates?: Coordinates | null;
  initialFeature?: FeatureInspectionPayload | null;
}

export const MapWorkspace: React.FC<Props> = ({
  theme = 'dark',
  targetCoordinates,
  initialFeature = null,
}) => {
  const [isInspectorOpen, setIsInspectorOpen] = useState(true);
  const [isEoPanelOpen, setIsEoPanelOpen] = useState(false);
  const [selectedYear, setSelectedYear] = useState<number>(2026);
  const [selectedFeature, setSelectedFeature] = useState<FeatureInspectionPayload | null>(initialFeature);
  const [selectedScene, setSelectedScene] = useState<NormalizedImageryScene | null>(null);

  useEffect(() => {
    if (initialFeature) {
      setSelectedFeature(initialFeature);
      setIsInspectorOpen(true);
    }
  }, [initialFeature]);

  const handleFeatureSelect = (payload: FeatureInspectionPayload) => {
    setSelectedFeature(payload);
    setIsInspectorOpen(true);
  };

  const handleSelectScene = (scene: NormalizedImageryScene) => {
    setSelectedScene(scene);

    // Sync inspection panel with observed telemetry
    setSelectedFeature({
      featureType: 'COORDINATE_POINT',
      featureId: scene.item_id,
      name: `${scene.platform} (${scene.sensor}) STAC Scene`,
      coordinates: {
        lng: scene.bbox ? (scene.bbox[0] + scene.bbox[2]) / 2 : -54.75,
        lat: scene.bbox ? (scene.bbox[1] + scene.bbox[3]) / 2 : -11.5,
      },
      properties: {
        platform: scene.platform,
        sensor: scene.sensor,
        modality: scene.modality,
        acquisition_datetime: scene.acquisition_datetime,
        cloud_cover: scene.cloud_cover !== null ? `${scene.cloud_cover}%` : 'N/A (SAR)',
        spatial_resolution: `${scene.spatial_resolution}m`,
        processing_level: scene.processing_level,
        license: scene.license,
        attribution: scene.attribution,
        total_assets: Object.keys(scene.assets || {}).length,
      },
      evidenceStrength: 'STRONG',
      epistemicLevel: 'OBSERVED',
    });

    setIsInspectorOpen(true);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden relative" data-testid="map-workspace-page">
      {/* Upper Main Workspace (Map Canvas + Collapsible Panels) */}
      <div className="flex-1 flex relative overflow-hidden">
        {/* Central MapLibre GL JS Real Map Canvas */}
        <div className="flex-1 relative h-full">
          <OrbitMap
            theme={theme}
            onFeatureSelect={handleFeatureSelect}
            targetCoordinates={targetCoordinates}
            selectedScene={selectedScene}
          />

          {/* Floating Earth Observation Discovery Trigger Button */}
          <button
            onClick={() => setIsEoPanelOpen(!isEoPanelOpen)}
            className={`absolute top-4 left-20 z-20 flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-mono font-bold transition shadow-lg backdrop-blur-md border ${
              isEoPanelOpen
                ? 'bg-orbit-emerald text-orbit-void border-orbit-emerald font-extrabold shadow-glow-emerald'
                : 'bg-orbit-carbon/90 text-orbit-text border-orbit-border hover:border-orbit-emerald/60 hover:text-orbit-emerald'
            }`}
            title="Open Earth Observation STAC Scene Discovery"
          >
            <Satellite className="w-4 h-4" />
            <span>STAC EO</span>
          </button>

          {/* Earth Observation Discovery Panel */}
          <ImageryDiscoveryPanel
            isOpen={isEoPanelOpen}
            onClose={() => setIsEoPanelOpen(false)}
            onSelectScene={handleSelectScene}
            selectedSceneId={selectedScene?.item_id}
          />
        </div>

        {/* Right Collapsible Intelligence Inspector */}
        <IntelligencePanel
          isOpen={isInspectorOpen}
          onToggle={() => setIsInspectorOpen(!isInspectorOpen)}
          selectedFeature={selectedFeature}
        />
      </div>

      {/* Bottom Temporal Timeline */}
      <OrbitTimeline
        selectedYear={selectedYear}
        onYearChange={(year) => setSelectedYear(year)}
      />
    </div>
  );
};
