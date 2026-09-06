# ORBIT Global Gazetteer & Spatial Search Engine (Phase 7)

## 1. Executive Summary

The **ORBIT Global Gazetteer & Spatial Search Engine** provides a high-performance, local-first search system and coordinate resolution subsystem. Analysts can search across administrative boundaries, populated places, transport infrastructure (roads and streets), Areas of Interest (AOIs), workspace projects, and raw geographic coordinates.

```
┌─────────────────────────┐
│ User Query / Input      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Query Normalization     │ ──► [Case / Whitespace / Admin Decompose]
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Coordinate Parser       │ ──► [Matches Decimal / Cardinal / Labeled Point?]
└────────────┬────────────┘
             │ (If text query)
             ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Unified PostGIS Search Layer                                           │
│ ├─ geo.gazetteer_entities (Countries, States, Cities, Places, etc.)    │
│ ├─ geo.road_features (Motorways, Primaries, Streets from Phase 6)      │
│ ├─ workspace.areas_of_interest (Existing User AOIs)                    │
│ └─ workspace.projects (Existing User Projects)                         │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Deterministic Relevance Ranking & Map Camera Target Generation         │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Structured Search Result -> MapLibre GL Camera Navigation              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Architectural Principles

1. **Local-First & Open Data**: Relies on PostgreSQL 16 + PostGIS 3.4 rather than third-party proprietary geocoding APIs. Supports local imports from OpenStreetMap, GeoNames, Natural Earth, and GADM.
2. **Epistemic Separation**: Geographic search resolves **spatial location context**, not satellite Earth observation or change analysis evidence. All resolved locations are classified strictly as `OBSERVED` or `CALCULATED`.
3. **Deterministic Relevance Ranking**: Ranking is computed via explicit mathematical rules (exact match, prefix match, alias match, administrative alignment, and population prominence). LLMs are never used for geographic ranking.
4. **Canonical Coordinate System**: All database records and search centroid calculations use `EPSG:4326` (WGS84 ellipsoidal coordinates).

---

## 3. Supported Entity Types (`GeographicEntityType`)

| Entity Type | Description | Default Camera Zoom |
|---|---|---|
| `COUNTRY` | Sovereign nations and territories | 4.5 |
| `STATE` / `PROVINCE` | First-level administrative divisions | 6.5 |
| `REGION` / `DISTRICT` | Second-level administrative divisions | 7.0 – 9.0 |
| `CITY` | Major urban agglomerations / municipalities | 11.5 |
| `TOWN` / `VILLAGE` | Secondary settlements and rural localities | 13.0 – 14.5 |
| `SUBURB` / `PLACE` | Urban neighborhoods and named places | 14.0 |
| `ROAD` / `STREET` | Road network features (Phase 6 integration) | 14.5 – 16.0 |
| `WATERBODY` / `MOUNTAIN` | Natural geographic features | 10.0 – 11.0 |
| `LANDMARK` / `AIRPORT` | Built infrastructure and transport hubs | 14.0 – 16.0 |
| `COORDINATE` | Direct coordinate pair inputs | 13.0 |
| `AOI` | Existing ORBIT Areas of Interest | 12.0 |
| `PROJECT` | Existing ORBIT Workspace Projects | 11.0 |

---

## 4. Database Architecture & PostGIS Schema

Table: `geo.gazetteer_entities`

```sql
CREATE TABLE geo.gazetteer_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider VARCHAR(50) NOT NULL DEFAULT 'OpenStreetMap',
    provider_entity_id VARCHAR(100),
    entity_type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255) NOT NULL,
    alternate_names JSONB DEFAULT '[]',
    country_code VARCHAR(10),
    country_name VARCHAR(100),
    admin_level_1 VARCHAR(100),
    admin_level_2 VARCHAR(100),
    admin_level_3 VARCHAR(100),
    population BIGINT,
    geometry Geometry(GEOMETRY, 4326),
    centroid Geometry(POINT, 4326) NOT NULL,
    bounding_box Geometry(POLYGON, 4326),
    metadata_json JSONB DEFAULT '{}',
    source_version VARCHAR(50),
    is_searchable BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Indexes:
- `idx_gazetteer_centroid`: PostGIS GiST index on `centroid` for spatial range & reverse lookups.
- `idx_gazetteer_geometry`: PostGIS GiST index on full `geometry`.
- `idx_gazetteer_normalized_name`: B-Tree index for fast prefix and equality searches.
- `idx_gazetteer_country_code`: B-Tree index for ISO country filtering.
- `idx_gazetteer_entity_type`: B-Tree index for entity category filtering.

---

## 5. Relevance Ranking Algorithm

Relevance score $S \in [0.0, 1.0]$ is computed deterministically:

$$S = S_{\text{base}} + \Delta_{\text{admin}} + \Delta_{\text{population}}$$

Where:
- **Base Match ($S_{\text{base}}$)**:
  - Exact normalized name match: $0.95$
  - Exact alias match: $0.90$
  - Prefix match: $0.80$
  - Substring / word match: $0.70$
  - Fuzzy match: $0.50$
- **Administrative Bonus ($\Delta_{\text{admin}}$)**: $+0.05$ if administrative tokens (e.g. "punjab", "pakistan") align with `admin_level_1`, `admin_level_2`, or `country_name`.
- **Population Prominence Bonus ($\Delta_{\text{population}}$)**:
  $$\Delta_{\text{population}} = \min\left(0.05, \frac{\log_{10}(\max(\text{population}, 1))}{10} \times 0.05\right)$$

---

## 6. Coordinate Parsing System

Supports multiple coordinate formats:
- **Decimal Pair**: `31.5204, 74.3587` or `-12.1 54.78`
- **Cardinal Pair**: `31.5204 N, 74.3587 E` or `12.1 S, 54.78 W`
- **Labeled Format**: `lat: 31.5204, lon: 74.3587` or `latitude: -11.52, longitude: -54.75`
- **Validation**: Latitudes strictly $\in [-90.0, 90.0]$, longitudes strictly $\in [-180.0, 180.0]$.

---

## 7. API Endpoints

### 7.1 Unified Search
`GET /api/v1/geo/search?q={query}&limit=20&entity_type={type}&country_code={cc}&bbox={bbox}`
- Returns structured `SearchResponse` containing sorted `results` with camera targets.

### 7.2 Entity Detail
`GET /api/v1/geo/entities/{entity_id}`
- Returns `GazetteerEntityDetail` with full boundary GeoJSON geometry, administrative hierarchy, and provider attribution.

### 7.3 Spatial Reverse Geocoder
`GET /api/v1/geo/reverse?lat={lat}&lon={lon}&radius_km=10`
- Returns nearest geographic entities ordered by true spheroid distance `ST_Distance(centroid::geography, point::geography)`.

---

## 8. Frontend Command Search & Map Integration

Integrated into `TopCommandBar.tsx` and `WorkspaceShell.tsx`:
- **Keyboard Navigation**: ArrowUp / ArrowDown for selection, Enter for resolution, Escape for closing.
- **Categorized Rendering**: Grouped into `PLACES`, `ROADS`, `AOIS`, `PROJECTS`, and `COORDINATES`.
- **Map Camera Execution**: Dispatches `map.flyTo({ center, zoom })` or `map.fitBounds(bbox)`.
- **Inspector Grounding**: Opens `IntelligencePanel` with full metadata and ODbL attribution notice.

---

## 9. Future Extension Points & Epistemic Separation

- **Future Prediction Extension**: Search targets provide the starting geographic anchor for future predictive modeling (e.g. urban sprawl, agricultural frontier expansion). Modeled geometries are strictly stored under `PREDICTED` and never merged into empirical gazetteer records.
- **Report Generation**: Licensing metadata (`source_attribution`, `provider`) is preserved on each entity and can be automatically compiled into PDF export dossiers.
