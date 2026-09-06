# ORBIT Global Road Network & Infrastructure Intelligence Engine (Phase 6)

## 1. Executive Summary

The **ORBIT Global Road Network Engine** provides a high-performance, local-first OpenStreetMap (OSM) infrastructure pipeline and dynamic Mapbox Vector Tile (MVT) delivery system. Roads are ingested into PostgreSQL 16 + PostGIS 3.4 in canonical `EPSG:4326` coordinates and delivered to the MapLibre GL JS frontend via dynamic `ST_AsMVT` vector tile streaming.

```
┌────────────────────────┐      ┌─────────────────────────┐      ┌────────────────────────┐
│  OSM PBF / GeoJSON     │ ───► │ PostGIS Ingestion Engine│ ───► │ geo.road_features      │
│  Regional Extracts     │      │ Normalization & Repair  │      │ (EPSG:4326 LineString) │
└────────────────────────┘      └─────────────────────────┘      └────────────────────────┘
                                                                             │
                                                                   ST_TileEnvelope / ST_AsMVT
                                                                             │
┌────────────────────────┐      ┌─────────────────────────┐                  ▼
│ MapLibre GL JS         │ ◄─── │ FastAPI MVT Endpoint    │ ◄─── PostGIS Binary MVT
│ Progressive LoD Layers │      │ /api/v1/geo/tiles/...   │      Protobuf Generation
└────────────────────────┘      └─────────────────────────┘
```

---

## 2. OpenStreetMap Ingestion & Licensing

### 2.1 Licensing & Attribution Invariants
All road network data sourced from OpenStreetMap is governed by the **Open Database License (ODbL 1.0)**.
- **Canonical Attribution**: `© OpenStreetMap contributors`
- **Redistribution & Derived Works**: Any dataset export, PDF dossier, or vector tile layer derived from OSM preserves the ODbL license metadata recorded in the ORBIT dataset registry (`eo.dataset_registry`).
- **Epistemic Integrity**: Real OSM road vectors are strictly categorized as `OBSERVED` Level 0–1 infrastructure data. They are never conflated with simulated scenarios or future predictions.

### 2.2 Ingestion Pipeline (`app.services.geo.osm_ingestion`)
The ingestion pipeline processes OSM PBF / JSON extracts in streaming chunks:
1. **Tag Filtering**: Evaluates raw OSM tags; ways lacking a valid `highway` tag are safely skipped.
2. **Classification Normalization**: Normalizes raw OSM tags into canonical ORBIT road classes (`motorway`, `trunk`, `primary`, `secondary`, `tertiary`, `unclassified`, `residential`, `service`, `track`, `path`).
3. **Property Extraction**: Parses surface classifications (`paved`, `unpaved`, `ground`), lane counts, speed limits ($\text{km/h}$ with automatic unit conversion from $\text{mph}$), and bridge/tunnel/oneway boolean flags.
4. **Topological Geometry Validation & Repair**: Coordinates are validated for WGS84 bounding compliance ($[-180, 180], [-90, 90]$), consecutive duplicate vertices are collapsed, and self-intersecting geometries are safely repaired via `shapely.make_valid`. Irreparable geometries are quarantined and logged rather than silently dropped or corrupted.
5. **Authoritative Geodesic Metric**: Calculates the true spheroid arc length in meters ($R = 6371008.8\text{ m}$) via Haversine summation and stores it in `geo.road_features.length_m`.
6. **Chunked Database Upsert**: Executes chunked upserts using PostgreSQL `ON CONFLICT (osm_id) DO UPDATE` to ensure idempotent re-ingestion.

---

## 3. Database Architecture & PostGIS Indexes

Table: `geo.road_features`

| Column | Type | Description |
|---|---|---|
| `id` | `UUID` (PK) | Unique ORBIT internal identifier |
| `osm_id` | `BigInteger` (Unique) | Original OpenStreetMap Way ID |
| `geometry` | `Geometry(LINESTRING, 4326)` | Canonical WGS84 LineString representation |
| `highway_class` | `VARCHAR(50)` | Normalized ORBIT road classification |
| `name` | `VARCHAR(255)` | Road / street name |
| `ref` | `VARCHAR(50)` | Highway reference identifier (e.g. BR-163) |
| `surface` | `VARCHAR(50)` | `paved`, `unpaved`, `ground` |
| `lanes` | `INTEGER` | Number of traffic lanes |
| `maxspeed` | `INTEGER` | Speed limit in $\text{km/h}$ |
| `oneway` | `BOOLEAN` | One-way traffic flag |
| `bridge` | `BOOLEAN` | Bridge flag |
| `tunnel` | `BOOLEAN` | Tunnel flag |
| `access` | `VARCHAR(50)` | `yes`, `private`, `permissive`, `no` |
| `length_m` | `FLOAT` | Authoritative spheroid length in meters |
| `source` | `VARCHAR(50)` | `OpenStreetMap` |

### Indexes:
- `idx_roads_geometry`: PostGIS GiST index on `geometry` for $O(\log N)$ bounding-box search.
- `idx_roads_osm_id`: B-Tree index on `osm_id` for $O(1)$ unique lookups and upsert conflicts.
- `idx_roads_highway_class`: B-Tree index on `highway_class` for fast zoom-based LoD filtering.

---

## 4. Vector Tile Engine & Dynamic PostGIS MVT

### 4.1 FastAPI Endpoint
`GET /api/v1/geo/tiles/roads/{z}/{x}/{y}.pbf`

- **Coordinate Validation**: Validates $z \in [0, 22]$, $x \in [0, 2^z - 1]$, $y \in [0, 2^z - 1]$. Returns HTTP 400 Bad Request for invalid coordinates.
- **Dynamic PostGIS Query**:
  ```sql
  WITH
  bounds AS (
    SELECT
      ST_TileEnvelope(:z, :x, :y) AS geom_3857,
      ST_Transform(ST_TileEnvelope(:z, :x, :y), 4326) AS geom_4326
  ),
  mvtgeom AS (
    SELECT
      ST_AsMVTGeom(
        ST_Transform(r.geometry, 3857),
        bounds.geom_3857,
        4096,
        64,
        true
      ) AS geom,
      r.id::text AS id,
      r.osm_id,
      r.highway_class,
      r.name,
      r.ref,
      r.surface,
      r.lanes,
      r.bridge,
      r.tunnel,
      r.access,
      'OpenStreetMap' AS source
    FROM geo.road_features r, bounds
    WHERE r.geometry && bounds.geom_4326
      AND ST_Intersects(r.geometry, bounds.geom_4326)
      AND r.highway_class IN (:classes)
  )
  SELECT ST_AsMVT(mvtgeom.*, 'roads', 4096, 'geom', 'id') AS mvt FROM mvtgeom;
  ```
- **Response**: Returns binary Mapbox Vector Tile Protobuf (`application/vnd.mapbox-vector-tile`) with HTTP 200 (or HTTP 204 No Content when no features intersect the tile envelope).

---

## 5. Progressive Level of Detail (LoD) Strategy

To maintain high rendering frame rates without exhausting browser memory, ORBIT dynamically restricts road classes and geometry density by zoom level:

```
┌───────────┬──────────────────────────────────────────┬──────────────────────────────────────────────┐
│ Zoom (Z)  │ Road Classes Ingested & Streamed         │ Visual Style & Palette                       │
├───────────┼──────────────────────────────────────────┼──────────────────────────────────────────────┤
│ Z0 – Z5   │ motorway, trunk                          │ Solid Amber/Orange (#F97316), width 1.0–2.0  │
│ Z6 – Z8   │ motorway, trunk, primary                 │ Primary Highway Amber (#F59E0B), width 1.2–3.5│
│ Z9 – Z11  │ primary, secondary, tertiary             │ Sky Blue (#38BDF8) / Emerald (#10B981)       │
│ Z12 – Z13 │ tertiary, residential, service           │ Slate Gray (#94A3B8), width 0.8–2.0          │
│ Z14 – Z22 │ all classes (tracks, paths, local spurs) │ Unpaved / Logging Spurs (#EA580C dashed)     │
└───────────┴──────────────────────────────────────────┴──────────────────────────────────────────────┘
```

---

## 6. Area of Interest (AOI) Geodesic Road Statistics

Endpoint: `GET /api/v1/geo/roads/stats/{aoi_id}`

Calculates authoritative road network metrics using PostGIS geography:
- **Total Network Length**: $\sum \text{ST\_Length}(\text{ST\_Intersection}(r.\text{geometry}, aoi.\text{geometry})::\text{geography})$
- **Road Length & Count by Class**: Aggregated metrics for motorways, primaries, secondaries, and tracks.
- **Road Density**: $\text{Road Density} = \frac{\text{Total Road Length (km)}}{\text{AOI Surface Area (km}^2\text{)}}$.

---

## 7. Future Extension Points: Infrastructure Intelligence & Forecasting

Phase 6 provides the data schema and query primitives for future analytical modules:
1. **Bi-Temporal Road Expansion Detection (Phase 8+)**: Comparing historical road network snapshots against new OSM / satellite-derived vector geometries to detect new illegal logging roads or expanding agro-industrial corridors.
2. **Infrastructure-Driven Change Proximity (Phase 10+)**: Evaluating distance buffers between detected canopy loss clusters and primary road axes (`ST_DWithin(change.geometry, road.geometry, distance)`).
3. **Scenario-Based Road Network Forecasting (Phase 12+)**: Simulating projected road network growth based on multi-decadal historical expansion vectors, strictly isolated under the `PREDICTED` epistemic classification.
