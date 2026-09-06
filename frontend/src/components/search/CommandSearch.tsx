import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  Search,
  MapPin,
  Compass,
  FolderKanban,
  Target,
  Navigation,
  Globe,
  Loader2,
  X,
} from 'lucide-react';
import { SearchResultItem, SearchCategoryGroup } from '../../types/gazetteer';
import { searchLocationsApi } from '../../services/gazetteerService';

interface Props {
  onSelectResult: (result: SearchResultItem) => void;
  onClose?: () => void;
  autoFocus?: boolean;
}

export const CommandSearch: React.FC<Props> = ({
  onSelectResult,
  onClose,
  autoFocus = true,
}) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [attributionNotice, setAttributionNotice] = useState<string>('');
  const [isOpen, setIsOpen] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Group results by category
  const groupedCategories = useMemo<SearchCategoryGroup[]>(() => {
    const places: SearchResultItem[] = [];
    const roads: SearchResultItem[] = [];
    const aois: SearchResultItem[] = [];
    const projects: SearchResultItem[] = [];
    const coords: SearchResultItem[] = [];

    results.forEach((item) => {
      const type = item.entity_type.toUpperCase();
      if (type === 'COORDINATE') coords.push(item);
      else if (type === 'ROAD' || type === 'STREET' || type === 'HIGHWAY') roads.push(item);
      else if (type === 'AOI') aois.push(item);
      else if (type === 'PROJECT') projects.push(item);
      else places.push(item);
    });

    const groups: SearchCategoryGroup[] = [];
    if (coords.length > 0) groups.push({ category: 'COORDINATES', items: coords });
    if (places.length > 0) groups.push({ category: 'PLACES', items: places });
    if (roads.length > 0) groups.push({ category: 'ROADS', items: roads });
    if (aois.length > 0) groups.push({ category: 'AOIS', items: aois });
    if (projects.length > 0) groups.push({ category: 'PROJECTS', items: projects });

    return groups;
  }, [results]);

  // Flattened items for keyboard navigation index calculation
  const flatItems = useMemo(() => {
    return groupedCategories.flatMap((g) => g.items);
  }, [groupedCategories]);

  // Debounced search effect
  useEffect(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const trimmed = query.trim();
    if (!trimmed) {
      setResults([]);
      setLoading(false);
      setIsOpen(false);
      return;
    }

    setLoading(true);
    setIsOpen(true);
    const controller = new AbortController();
    abortControllerRef.current = controller;

    const timer = setTimeout(async () => {
      try {
        const data = await searchLocationsApi(trimmed, controller.signal);
        setResults(data.results || []);
        setAttributionNotice(data.attribution_notice || '© OpenStreetMap contributors');
        setSelectedIndex(0);
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          setResults([]);
        }
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => {
      clearTimeout(timer);
    };
  }, [query]);

  // Handle outside clicks
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        if (onClose) onClose();
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onClose]);

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (flatItems.length > 0 ? (prev + 1) % flatItems.length : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (flatItems.length > 0 ? (prev - 1 + flatItems.length) % flatItems.length : 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (flatItems.length > 0 && flatItems[selectedIndex]) {
        handleSelectItem(flatItems[selectedIndex]);
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setIsOpen(false);
      if (onClose) onClose();
    }
  };

  const handleSelectItem = (item: SearchResultItem) => {
    onSelectResult(item);
    setQuery(item.name);
    setIsOpen(false);
  };

  const getEntityIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case 'COORDINATE':
        return <Navigation className="w-3.5 h-3.5 text-orbit-emerald" />;
      case 'ROAD':
      case 'STREET':
        return <Compass className="w-3.5 h-3.5 text-orbit-amber" />;
      case 'AOI':
        return <Target className="w-3.5 h-3.5 text-orbit-sky" />;
      case 'PROJECT':
        return <FolderKanban className="w-3.5 h-3.5 text-orbit-purple" />;
      case 'COUNTRY':
      case 'STATE':
        return <Globe className="w-3.5 h-3.5 text-orbit-cyan" />;
      default:
        return <MapPin className="w-3.5 h-3.5 text-orbit-emerald" />;
    }
  };

  return (
    <div ref={containerRef} className="relative w-full" data-testid="command-search-container">
      {/* Search Input Bar */}
      <div className="relative flex items-center w-full bg-orbit-slate/60 hover:bg-orbit-slate border border-orbit-border focus-within:border-orbit-emerald/60 focus-within:ring-1 focus-within:ring-orbit-emerald/30 transition rounded-lg px-3 py-1.5 text-xs text-orbit-muted font-mono shadow-inner">
        {loading ? (
          <Loader2 className="w-3.5 h-3.5 text-orbit-emerald animate-spin mr-2 shrink-0" />
        ) : (
          <Search className="w-3.5 h-3.5 text-orbit-muted mr-2 shrink-0" />
        )}
        <input
          ref={inputRef}
          type="text"
          placeholder="Search places (Lahore), roads (BR-163), coordinates (31.52, 74.35)..."
          value={query}
          autoFocus={autoFocus}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.trim() && setIsOpen(true)}
          onKeyDown={handleKeyDown}
          className="bg-transparent border-none outline-none text-orbit-text placeholder-orbit-muted/70 w-full text-xs font-mono"
          aria-label="Global Spatial & Gazetteer Search"
          aria-expanded={isOpen}
          role="combobox"
        />
        {query && (
          <button
            onClick={() => {
              setQuery('');
              setResults([]);
              setIsOpen(false);
            }}
            className="p-1 text-orbit-muted hover:text-orbit-text rounded transition mr-1"
            title="Clear search"
          >
            <X className="w-3 h-3" />
          </button>
        )}
        <div className="hidden sm:flex items-center gap-1 text-[10px] font-mono bg-orbit-carbon px-1.5 py-0.5 rounded border border-orbit-border text-orbit-muted ml-1 shrink-0">
          <span>ESC</span>
        </div>
      </div>

      {/* Autocomplete Dropdown Listbox */}
      {isOpen && (
        <div
          className="absolute top-full left-0 right-0 mt-1.5 bg-orbit-carbon/95 backdrop-blur-md border border-orbit-border rounded-lg shadow-2xl overflow-hidden z-50 max-h-96 flex flex-col"
          role="listbox"
        >
          {results.length === 0 && !loading && (
            <div className="p-4 text-center text-xs font-mono text-orbit-muted">
              No matching geographic entities found for <span className="text-orbit-text font-bold">"{query}"</span>
            </div>
          )}

          <div className="overflow-y-auto flex-1 divide-y divide-orbit-border/40">
            {groupedCategories.map((group) => (
              <div key={group.category} className="py-1">
                <div className="px-3 py-1 text-[10px] font-mono font-bold tracking-wider text-orbit-muted uppercase bg-orbit-slate/30">
                  {group.category} ({group.items.length})
                </div>
                {group.items.map((item) => {
                  const globalIdx = flatItems.indexOf(item);
                  const isSelected = globalIdx === selectedIndex;
                  return (
                    <div
                      key={item.id}
                      onClick={() => handleSelectItem(item)}
                      onMouseEnter={() => setSelectedIndex(globalIdx)}
                      className={`px-3 py-2 flex items-center justify-between cursor-pointer transition text-xs font-mono ${
                        isSelected
                          ? 'bg-orbit-emerald/15 border-l-2 border-orbit-emerald text-orbit-text'
                          : 'hover:bg-orbit-slate/40 text-orbit-muted hover:text-orbit-text'
                      }`}
                      role="option"
                      aria-selected={isSelected}
                    >
                      <div className="flex items-center gap-2.5 min-w-0 pr-2">
                        <div className="shrink-0 p-1 rounded bg-orbit-slate/60 border border-orbit-border">
                          {getEntityIcon(item.entity_type)}
                        </div>
                        <div className="min-w-0 truncate">
                          <div className="flex items-center gap-1.5 leading-tight">
                            <span className="font-semibold text-orbit-text truncate">{item.name}</span>
                            <span className="text-[9px] px-1 rounded bg-orbit-border/50 text-orbit-muted font-bold">
                              {item.entity_type}
                            </span>
                          </div>
                          {item.administrative_context && (
                            <div className="text-[10px] text-orbit-muted truncate mt-0.5">
                              {item.administrative_context}
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="text-right shrink-0 font-mono text-[10px]">
                        <div className="text-orbit-emerald">
                          {item.coordinates.lat.toFixed(4)}°, {item.coordinates.lng.toFixed(4)}°
                        </div>
                        <div className="text-orbit-muted text-[9px]">
                          Score: {(item.relevance_score * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>

          {/* Footer Attribution Banner */}
          {attributionNotice && (
            <div className="p-2 text-[9px] font-mono text-orbit-muted bg-orbit-slate/50 border-t border-orbit-border flex items-center justify-between">
              <span>{attributionNotice}</span>
              <span>EPSG:4326</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
