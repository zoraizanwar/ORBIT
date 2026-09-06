# ORBIT Map Engine Architecture: MapLibre GL JS & Interactive Geospatial Canvas

## 1. System Overview

The **ORBIT Map Engine** is the core interactive 2D geospatial visualization layer of the ORBIT platform. Powered by **MapLibre GL JS v4.7.1**, the map provides a high-performance, WebGL-accelerated cartographic workspace designed for progressive planetary-to-local scale exploration.

```
Planetary Navigation Hierarchy:
WORLD (Z0–2) ──► CONTINENT (Z3–5) ──► REGION/COUNTRY (Z6–8) ──► CITY (Z9–11) ──► DISTRICT (Z12–13) ──► STREET/ROAD (Z14–22)
```

---

## 2. Coordinate Systems & Geodesic Reference

ORBIT enforces strict mathematical and architectural separation across coordinate reference systems (CRS):

| Role | CRS / Spheroid | Description & Implementation |
|---|---|---|
| **Authoritative Storage & Exchange** | `EPSG:4326` (WGS84 Lon/Lat) | All database geometries, GeoJSON features, and REST/MVT endpoints are strictly stored and exchanged in decimal degrees `(longitude, latitude)`. |
| **Web Client Map Rendering** | `EPSG:3857` (Web Mercator) | MapLibre GL JS renders conformal planetary tiles using standard spherical Mercator planar projection. |
| **Authoritative Geodesic Computations** | `WGS84 Ellipsoid` (PostGIS `geography`) | All true geodesic surface areas ($\text{km}^2$), great-circle distances ($\text{meters}$), and road lengths are computed server-side via PostGIS `ST_Area(geom::geography)` and `ST_Length(geom::geography)`. Browser measurements are strictly labeled as client visual approximations. |

---

## 3. Map Lifecycle & React Strict Mode Safety

To ensure zero memory leaks and prevent multiple WebGL rendering contexts from conflicting during development or page transitions:

1. **Single Instance Lifecycle**: The `MapLibreMap` instance is stored in a mutable `useRef<MapLibreMap | null>(null)` and mounted once per workstation session.
2. **Explicit Teardown**: Upon unmounting, `map.remove()` is called in the `useEffect` cleanup return handler, immediately releasing WebGL shader buffers, event listeners, and tile worker threads.
3. **Throttled Pointer Events**: Cursor coordinate sampling on `mousemove` uses native MapLibre pointer events without triggering whole-component React re-renders.

---

## 4. Cartographic Style Architecture

ORBIT implements custom cartographic styles with **zero commercial API keys** or paid cloud SaaS dependencies:

- **Tactical Dark Mode (`TACTICAL_DARK`)**:
  - Base surface: `#080C10` (ORBIT Void).
  - Basemap tiles: Open CARTO Dark Matter raster/vector tiles with ODbL / CC-BY 4.0 licensing.
  - High-contrast analytical vector overlays: `#19C37D` (AOI boundary), `#F59E0B` (Primary Highway BR-163), `#EF4444` (Canopy Loss Change Detection).
- **Scientific Light Mode (`SCIENTIFIC_LIGHT`)**:
  - Base surface: `#F8FAFC` (Cartographic Paper).
  - Basemap tiles: Open CARTO Positron raster/vector tiles.
  - Research GIS aesthetic with subdued road linework and dark slate typography.

Theme switching updates the map via `map.setStyle(getMapStyleByTheme(theme))` and dynamically re-attaches custom domain sources and analytical layers on the `style.load` event.

---

## 5. Layer Architecture & Progressive Road Hierarchy

To prevent client browser exhaustion when visualizing planetary road networks, ORBIT utilizes **progressive geographic level-of-detail (LOD)**:

```
┌───────────┬───────────────────────────────┬──────────────────────────────────────────┐
│ Zoom (Z)  │ Road / Geographic Scope       │ Rendering Strategy                       │
├───────────┼───────────────────────────────┼──────────────────────────────────────────┤
│ Z0 – Z5   │ Continental / Country Context │ National boundaries, ocean/land geometry │
│ Z6 – Z8   │ Major Motorways & Corridors   │ Motorways, Highway BR-163 (Orange/Amber) │
│ Z9 – Z11  │ Secondary / Primary Roads     │ Secondary arteries, agricultural tracks  │
│ Z12 – Z13 │ Tertiary & Feeder Roads       │ Feeder spurs, rural settlement links     │
│ Z14 – Z22 │ Local Streets & Unpaved Tracks│ Full local street grid, logging spurs    │
└───────────┴───────────────────────────────┴──────────────────────────────────────────┘
```

### Future Vector Tile Source Integration (Phase 6)
In Phase 6, road vectors will stream dynamically as Mapbox Vector Tiles (MVT) generated directly by PostGIS:
- Endpoint: `/api/v1/geo/tiles/roads/{z}/{x}/{y}.pbf`
- Caching: Redis binary tile cache.
- Filtering: Server-side `ST_AsMVT` tile clipping by bounding box and zoom-level road class filters.

---

## 6. Dynamic Cartographic Scale Engine

The map scale bar dynamically calculates the ground resolution $R$ in meters per pixel based on the viewport center latitude $\phi$ and zoom level $Z$:

$$R = \frac{156543.03392 \times \cos\left(\phi \times \frac{\pi}{180}\right)}{2^Z}$$

The scale display selects standard metric intervals ($5000\text{ km} \rightarrow 1\text{ m}$) and renders the exact physical pixel bar width, ensuring accurate spatial context at any latitude.

---

## 7. Interactive Feature Inspection & Evidence Grounding

Clicking any vector feature on the map (Area of Interest, Highway Segment, or Change Detection Polygon) triggers a spatial query (`queryRenderedFeatures`) that extracts:
- Feature ID & Feature Type (`AOI`, `ROAD`, `CHANGE_DETECTION`)
- Epistemic Level (`OBSERVED`, `CALCULATED`, `DETECTED`)
- Evidence Strength (`STRONG`, `MODERATE`, `LIMITED`, `INSUFFICIENT`)
- Coordinate Centroid & Lineage Properties

This payload automatically opens and populates the **Intelligence Inspector** (`IntelligencePanel`), ensuring seamless integration between cartographic inspection and cryptographic provenance records.
