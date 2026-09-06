# ORBIT: Database & Data Storage Architecture

## 1. Multi-Tier Storage Hierarchy

ORBIT avoids storing massive multi-gigabyte satellite imagery directly inside relational database tables. Instead, the architecture establishes a **Three-Tier Storage Hierarchy**:

```
+-----------------------------------------------------------------------------------+
| TIER 1: RELATIONAL & SPATIAL DATA (PostgreSQL 16 + PostGIS 3.4)                   |
| * Users, Projects, AOIs, Workspaces, Road Vectors, Analysis DAGs                  |
| * Dataset Licensing Registry, STAC References, Measurements, Events               |
| * Evidence Chains, Evidence Strength Scores, Annual Historical Metrics, Audit Logs|
+-----------------------------------------------------------------------------------+
                                         | Referenced by URI / Relative Path
                                         v
+-----------------------------------------------------------------------------------+
| TIER 2: LOCAL HIGH-PERFORMANCE ARTIFACT STORE (Filesystem / MinIO Object Tier)    |
| * Cloud-Optimized GeoTIFFs (COGs) of cropped AOI bands (B02, B03, B04, B08, B11)  |
| * Derived Spectral Index Rasters (NDVI, NDWI, NDBI Float32 COGs)                  |
| * Binary Change Masks, Morphological GeoTIFFs                                     |
| * Generated PDF Intelligence Dossiers, High-Res Map Exports, Vector GeoPackages   |
+-----------------------------------------------------------------------------------+
                                         | Transient Read-Through & Caching
                                         v
+-----------------------------------------------------------------------------------+
| TIER 3: IN-MEMORY CACHING & MESSAGE BUFFER (Redis 7.2)                            |
| * Vector Tile (MVT) Cache (Key: `mvt:{layer}:{z}:{x}:{y}`, TTL: 24h)             |
| * Geocoding Query Cache (Key: `geocode:{hash(query)}`, TTL: 7d)                   |
| * Celery Task Broker & Result Store, Live Analysis Run Progress State             |
+-----------------------------------------------------------------------------------+
```

---

## 2. PostgreSQL + PostGIS Schema Definition (DDL Specification)

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS workspace;
CREATE SCHEMA IF NOT EXISTS geo;
CREATE SCHEMA IF NOT EXISTS eo;
CREATE SCHEMA IF NOT EXISTS analysis;
CREATE SCHEMA IF NOT EXISTS intelligence;
CREATE SCHEMA IF NOT EXISTS history_deep;

-- ============================================================================
-- SCHEMA: auth & workspace
-- ============================================================================
CREATE TABLE auth.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'ANALYST',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE workspace.projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE workspace.areas_of_interest (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES workspace.projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    geometry GEOMETRY(Polygon, 4326) NOT NULL,
    bounding_box GEOMETRY(Polygon, 4326) NOT NULL,
    surface_area_km2 DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_aoi_geometry ON workspace.areas_of_interest USING GIST(geometry);

-- ============================================================================
-- SCHEMA: geo (Road Network & Infrastructure)
-- ============================================================================
CREATE TABLE geo.road_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    osm_id BIGINT UNIQUE NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'OpenStreetMap',
    source_version VARCHAR(50),
    source_timestamp TIMESTAMPTZ,
    name VARCHAR(255),
    road_class VARCHAR(50) NOT NULL,
    surface VARCHAR(50),
    lanes INT DEFAULT 1,
    maxspeed INT,
    oneway BOOLEAN DEFAULT FALSE,
    bridge BOOLEAN DEFAULT FALSE,
    tunnel BOOLEAN DEFAULT FALSE,
    geometry GEOMETRY(LineString, 4326) NOT NULL,
    length_m DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_roads_geometry ON geo.road_features USING GIST(geometry);
CREATE INDEX idx_roads_class ON geo.road_features(road_class);

-- ============================================================================
-- SCHEMA: eo (Dataset Registry & Imagery Catalog)
-- ============================================================================
CREATE TABLE eo.dataset_registry (
    id VARCHAR(50) PRIMARY KEY, -- 'copernicus-s2-l2a', 'copernicus-s1-grd', 'usgs-landsat-c2l2'
    name VARCHAR(255) NOT NULL,
    provider_name VARCHAR(100) NOT NULL,
    sensing_modality VARCHAR(50) NOT NULL, -- 'OPTICAL', 'SAR', 'DEM'
    license_type VARCHAR(100) NOT NULL,
    license_url VARCHAR(500) NOT NULL,
    mandatory_attribution_text TEXT NOT NULL,
    commercial_use_terms TEXT NOT NULL,
    redistribution_constraints TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE eo.imagery_scenes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id VARCHAR(50) NOT NULL REFERENCES eo.dataset_registry(id),
    scene_identifier VARCHAR(255) UNIQUE NOT NULL,
    sensing_modality VARCHAR(50) NOT NULL,
    acquisition_datetime TIMESTAMPTZ NOT NULL,
    cloud_cover_percent DOUBLE PRECISION,
    spatial_resolution_m DOUBLE PRECISION NOT NULL,
    crs VARCHAR(50) NOT NULL,
    geometry GEOMETRY(Polygon, 4326) NOT NULL,
    stac_metadata JSONB NOT NULL,
    storage_uri VARCHAR(1000),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_scenes_geometry ON eo.imagery_scenes USING GIST(geometry);
CREATE INDEX idx_scenes_datetime ON eo.imagery_scenes(acquisition_datetime);

-- ============================================================================
-- SCHEMA: analysis & pipeline
-- ============================================================================
CREATE TYPE analysis.execution_status AS ENUM (
    'QUEUED', 'INGESTING', 'PROCESSING', 'ANALYZING', 'SYNTHESIZING', 'COMPLETED', 'FAILED', 'CANCELLED'
);

CREATE TABLE analysis.runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES workspace.projects(id) ON DELETE CASCADE,
    aoi_id UUID NOT NULL REFERENCES workspace.areas_of_interest(id) ON DELETE CASCADE,
    analysis_type VARCHAR(100) NOT NULL,
    status analysis.execution_status NOT NULL DEFAULT 'QUEUED',
    progress_percent INT NOT NULL DEFAULT 0,
    current_stage VARCHAR(100) NOT NULL DEFAULT 'INITIALIZATION',
    parameters JSONB NOT NULL,
    baseline_scene_id UUID REFERENCES eo.imagery_scenes(id),
    target_scene_id UUID REFERENCES eo.imagery_scenes(id),
    algorithm_tier VARCHAR(50) NOT NULL, -- 'TIER_1_DETERMINISTIC', 'TIER_2_STATISTICAL', 'TIER_3_ML', 'TIER_4_EVENT'
    algorithm_version VARCHAR(50) NOT NULL,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- SCHEMA: intelligence (Measurements, Evidence, Events, Reports)
-- ============================================================================
CREATE TYPE intelligence.epistemic_level AS ENUM (
    'OBSERVED', 'CALCULATED', 'DETECTED', 'ESTIMATED', 'PREDICTED', 'AI_INTERPRETATION'
);

CREATE TYPE intelligence.evidence_strength AS ENUM (
    'STRONG', 'MODERATE', 'LIMITED', 'INSUFFICIENT'
);

CREATE TABLE intelligence.measurements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_run_id UUID NOT NULL REFERENCES analysis.runs(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(50) NOT NULL,
    epistemic_level intelligence.epistemic_level NOT NULL DEFAULT 'CALCULATED',
    evidence_strength intelligence.evidence_strength NOT NULL DEFAULT 'STRONG',
    uncertainty_margin DOUBLE PRECISION,
    confidence DOUBLE PRECISION NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    calculation_method VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE intelligence.geographic_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aoi_id UUID NOT NULL REFERENCES workspace.areas_of_interest(id) ON DELETE CASCADE,
    event_title VARCHAR(255) NOT NULL,
    event_category VARCHAR(100) NOT NULL,
    first_observed_date DATE NOT NULL,
    last_observed_date DATE NOT NULL,
    lifecycle_state VARCHAR(50) NOT NULL,
    geometry GEOMETRY(MultiPolygon, 4326) NOT NULL,
    affected_area_km2 DOUBLE PRECISION NOT NULL,
    evidence_strength intelligence.evidence_strength NOT NULL DEFAULT 'STRONG',
    related_road_id UUID REFERENCES geo.road_features(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_geographic_events_geom ON intelligence.geographic_events USING GIST(geometry);

CREATE TABLE intelligence.evidence_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_run_id UUID NOT NULL REFERENCES analysis.runs(id) ON DELETE CASCADE,
    claim_text TEXT NOT NULL,
    epistemic_level intelligence.epistemic_level NOT NULL,
    evidence_strength intelligence.evidence_strength NOT NULL,
    evidence_strength_score DOUBLE PRECISION NOT NULL,
    source_telemetry_id VARCHAR(255) NOT NULL,
    dataset_name VARCHAR(100) NOT NULL,
    acquisition_date TIMESTAMPTZ NOT NULL,
    processing_pipeline VARCHAR(255) NOT NULL,
    calculation_formula TEXT NOT NULL,
    sha256_checksum VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE intelligence.historical_annual_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aoi_id UUID NOT NULL REFERENCES workspace.areas_of_interest(id) ON DELETE CASCADE,
    summary_year INT NOT NULL,
    support_level VARCHAR(50) NOT NULL, -- 'STRONGLY_SUPPORTED', 'PARTIALLY_SUPPORTED', 'ESTIMATED', 'UNAVAILABLE'
    mean_ndvi DOUBLE PRECISION,
    mean_ndwi DOUBLE PRECISION,
    mean_ndbi DOUBLE PRECISION,
    built_up_area_km2 DOUBLE PRECISION,
    vegetation_cover_km2 DOUBLE PRECISION,
    water_surface_km2 DOUBLE PRECISION,
    new_roads_length_km DOUBLE PRECISION,
    evidence_strength intelligence.evidence_strength NOT NULL,
    evidence_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(aoi_id, summary_year)
);

CREATE TABLE intelligence.reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_run_id UUID NOT NULL REFERENCES analysis.runs(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    executive_summary TEXT NOT NULL,
    ai_narrative_payload JSONB NOT NULL,
    pdf_storage_path VARCHAR(1000),
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- SCHEMA: history_deep (Geological History & Classified Islamic Sources)
-- ============================================================================
CREATE TABLE history_deep.geological_epochs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    epoch_name VARCHAR(100) NOT NULL,
    start_mya DOUBLE PRECISION NOT NULL,
    end_mya DOUBLE PRECISION NOT NULL,
    paleo_climate_description TEXT NOT NULL,
    global_sea_level_relative_m DOUBLE PRECISION NOT NULL
);

CREATE TYPE history_deep.islamic_source_grade AS ENUM (
    'QURAN', 'MUTAWATIR_HADITH', 'AHAD_SAHIH', 'SCHOLARLY_IJMA', 'HISTORICAL_TARIKH', 'UNVERIFIED_ISRAILIYYAT'
);

CREATE TABLE history_deep.islamic_geographic_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_name VARCHAR(255) NOT NULL,
    geometry GEOMETRY(Geometry, 4326),
    source_grade history_deep.islamic_source_grade NOT NULL,
    primary_source_reference VARCHAR(500) NOT NULL,
    text_arabic TEXT NOT NULL,
    text_translation TEXT NOT NULL,
    scholarly_commentary TEXT,
    verified_historical_context TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_islamic_geo_geom ON history_deep.islamic_geographic_records USING GIST(geometry);
```
