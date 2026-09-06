import React, { useState, useEffect } from 'react';
import { NavigationSection } from '../../types';
import { Coordinates, FeatureInspectionPayload } from '../../map/mapTypes';
import { SearchResultItem } from '../../types/gazetteer';
import { TopCommandBar } from './TopCommandBar';
import { Sidebar } from './Sidebar';
import { StatusBar } from './StatusBar';
import { Overview } from '../../pages/Overview';
import { MapWorkspace } from '../../pages/MapWorkspace';
import { Projects } from '../../pages/Projects';
import { Analyses } from '../../pages/Analyses';
import { History } from '../../pages/History';
import { Predictions } from '../../pages/Predictions';
import { Evidence } from '../../pages/Evidence';
import { Reports } from '../../pages/Reports';
import { Datasets } from '../../pages/Datasets';
import { Settings } from '../../pages/Settings';

export const WorkspaceShell: React.FC = () => {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [activeSection, setActiveSection] = useState<NavigationSection>('overview');
  const [targetCoordinates, setTargetCoordinates] = useState<Coordinates | null>(null);
  const [searchedFeature, setSearchedFeature] = useState<FeatureInspectionPayload | null>(null);

  // Toggle Theme Class on document root
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
      root.classList.remove('light');
    } else {
      root.classList.add('light');
      root.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleSelectLocation = (result: SearchResultItem) => {
    setTargetCoordinates({ lat: result.coordinates.lat, lng: result.coordinates.lng });
    
    // Create an epistemic inspection payload for the resolved geographic target
    const inspectionPayload: FeatureInspectionPayload = {
      featureType: result.entity_type === 'AOI' ? 'AOI' : result.entity_type === 'ROAD' ? 'ROAD' : 'COORDINATE_POINT',
      featureId: result.id,
      name: result.name,
      coordinates: { lat: result.coordinates.lat, lng: result.coordinates.lng },
      properties: {
        display_name: result.display_name,
        entity_type: result.entity_type,
        administrative_context: result.administrative_context || 'N/A',
        country_code: result.country_code || 'N/A',
        population: result.population ? result.population.toLocaleString() : 'N/A',
        provider: result.provider,
        source: result.source_attribution,
        relevance_score: `${(result.relevance_score * 100).toFixed(0)}%`,
        match_type: result.match_type,
      },
      evidenceStrength: 'STRONG',
      epistemicLevel: 'OBSERVED',
    };

    setSearchedFeature(inspectionPayload);
    setActiveSection('map');
  };

  const renderActivePage = () => {
    switch (activeSection) {
      case 'overview':
        return <Overview onNavigateToMap={() => setActiveSection('map')} />;
      case 'map':
        return (
          <MapWorkspace
            theme={theme}
            targetCoordinates={targetCoordinates}
            initialFeature={searchedFeature}
          />
        );
      case 'projects':
        return <Projects onSelectProject={() => setActiveSection('map')} />;
      case 'analyses':
        return <Analyses />;
      case 'changes':
      case 'infrastructure':
      case 'environment':
      case 'events':
        return (
          <MapWorkspace
            theme={theme}
            targetCoordinates={targetCoordinates}
            initialFeature={searchedFeature}
          />
        );
      case 'timeline':
      case 'history':
      case 'deep_history':
      case 'islamic_sources':
        return <History />;
      case 'predictions':
      case 'scenarios':
        return <Predictions />;
      case 'evidence':
        return <Evidence />;
      case 'reports':
      case 'exports':
        return <Reports />;
      case 'datasets':
        return <Datasets />;
      case 'health':
      case 'settings':
        return <Settings />;
      default:
        return <Overview onNavigateToMap={() => setActiveSection('map')} />;
    }
  };

  return (
    <div className={`flex flex-col h-screen w-screen overflow-hidden ${
      theme === 'dark' ? 'bg-orbit-void text-orbit-text' : 'bg-slate-50 text-slate-900'
    }`}>
      {/* 1. Top Command Bar */}
      <TopCommandBar
        theme={theme}
        onToggleTheme={toggleTheme}
        onSelectLocation={handleSelectLocation}
      />

      {/* 2. Middle Workstation Body: Sidebar + Active Canvas */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Vertical Navigation */}
        <Sidebar
          activeSection={activeSection}
          onSelectSection={(sec) => setActiveSection(sec)}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        />

        {/* Central Workstation Main View */}
        <main className="flex-1 flex flex-col overflow-hidden relative bg-orbit-slate/10">
          {renderActivePage()}
        </main>
      </div>

      {/* 3. Bottom Status Bar */}
      <StatusBar />
    </div>
  );
};
