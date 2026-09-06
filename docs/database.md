# ORBIT: Database & PostGIS Foundation Specification

## 1. Database Architecture & Multi-Schema Design

ORBIT employs **PostgreSQL 16 with PostGIS 3.4** partitioned across **7 modular schemas**. This multi-schema design prevents table namespace collisions, enforces clean domain boundaries, and enables granular access control and temporal partitioning:

```
+-----------------------------------------------------------------------------------+
| POSTGRESQL 16 + POSTGIS 3.4 MULTI-SCHEMA TOPOLOGY                                 |
+-----------------------------------------------------------------------------------+
| 1. auth          | User identities, roles, password hashes, and session state.     |
| 2. workspace     | User projects, investigations, and Areas of Interest (AOIs).   |
| 3. geo           | Global mapped road network, street hierarchy, topology vectors. |
| 4. eo            | Dataset licensing registry and satellite imagery scene catalog. |
| 5. analysis      | Analysis runs, execution states, and algorithm parameters.      |
| 6. intelligence  | Authoritative measurements, detected changes, events, evidence. |
| 7. history_deep  | Historical annual summaries, predictions, geology, Islamic data.|
+-----------------------------------------------------------------------------------+
```

---

## 2. Relational Schema & Tables Catalog

### Schema 1: `auth`
- **`auth.users`**:
  - `id`: UUID (Primary Key)
  - `email`: VARCHAR(255) (Unique, Indexed)
  - `password_hash`: VARCHAR(255) (Argon2id hash)
  - `full_name`: VARCHAR(255)
  - `role`: ENUM (`ANALYST`, `RESEARCHER`, `ADMIN`, `VIEWER`)
  - `is_active`: BOOLEAN
  - `created_at`, `updated_at`: TIMESTAMPTZ

### Schema 2: `workspace`
- **`workspace.projects`**:
  - `id`: UUID (Primary Key)
  - `user_id`: UUID (Foreign Key to `auth.users.id` ON DELETE CASCADE)
  - `name`: VARCHAR(255)
  - `description`: TEXT
  - `status`: ENUM (`ACTIVE`, `ARCHIVED`, `COMPLETED`)
  - `created_at`, `updated_at`: TIMESTAMPTZ
- **`workspace.areas_of_interest`**:
  - `id`: UUID (Primary Key)
  - `project_id`: UUID (Foreign Key to `workspace.projects.id` ON DELETE CASCADE)
  - `name`: VARCHAR(255)
  - `description`: TEXT
  - `geometry`: GEOMETRY(MULTIPOLYGON, 4326) with GiST Index
  - `centroid`: GEOMETRY(POINT, 4326) with GiST Index
  - `bounding_box`: GEOMETRY(POLYGON, 4326) with GiST Index
  - `surface_area_km2`: FLOAT (Authoritative geodesic area computed on WGS84 spheroid)
  - `created_at`, `updated_at`: TIMESTAMPTZ

### Schema 3: `geo`
- **`geo.road_features`**:
  - `id`: UUID (Primary Key)
  - `osm_id`: BIGINT (Unique, Indexed)
  - `geometry`: GEOMETRY(LINESTRING, 4326) with GiST Index
  - `highway_class`: VARCHAR(50) (Indexed - `motorway`, `trunk`, `primary`, `secondary`, `tertiary`, `residential`, `service`, `track`, `path`)
  - `name`: VARCHAR(255)
  - `ref`: VARCHAR(50) (e.g. `BR-163`, `I-95`)
  - `surface`: VARCHAR(50) (`paved`, `unpaved`, `asphalt`, `gravel`)
  - `lanes`: INTEGER
  - `maxspeed`: INTEGER
  - `oneway`: BOOLEAN
  - `access`: VARCHAR(50)
  - `bridge`: BOOLEAN
  - `tunnel`: BOOLEAN
  - `source`: VARCHAR(50) (`OpenStreetMap`)
  - `source_version`: VARCHAR(50)
  - `length_m`: FLOAT (Authoritative geodesic length)
  - `created_at`, `updated_at`: TIMESTAMPTZ

### Schema 4: `eo`
- **`eo.dataset_registry`**:
  - `id`: VARCHAR(50) (Primary Key - e.g. `copernicus-s2-l2a`, `copernicus-s1-grd`, `usgs-landsat-c2l2`)
  - `provider`: VARCHAR(100) (e.g. `European Space Agency`, `USGS`)
  - `dataset_name`: VARCHAR(255)
  - `dataset_version`: VARCHAR(50)
  - `modality`: ENUM (`OPTICAL`, `SAR`, `DEM`, `VECTOR`, `MULTISPECTRAL`)
  - `description`: TEXT
  - `license`: VARCHAR(100)
  - `attribution`: TEXT (Mandatory legal citation)
  - `terms_url`, `api_url`, `documentation_url`: VARCHAR(500)
  - `redistribution_allowed`, `commercial_use_allowed`, `active`: BOOLEAN
  - `created_at`, `updated_at`: TIMESTAMPTZ
- **`eo.imagery_scenes`**:
  - `id`: UUID (Primary Key)
  - `dataset_id`: VARCHAR(50) (Foreign Key to `eo.dataset_registry.id` ON DELETE CASCADE)
  - `provider_scene_id`: VARCHAR(255) (Unique, Indexed)
  - `acquisition_datetime`: TIMESTAMPTZ (Indexed)
  - `platform`: VARCHAR(100) (`Sentinel-2A`, `Landsat-8`)
  - `sensor`: VARCHAR(100) (`MSI`, `C-SAR`, `OLI`)
  - `modality`: ENUM (`OPTICAL`, `SAR`, `DEM`, `VECTOR`, `MULTISPECTRAL`)
  - `cloud_cover`: FLOAT (0.0 to 100.0 Check Constraint)
  - `processing_level`: VARCHAR(50) (`Level-2A`, `Level-1C`, `GRD`)
  - `spatial_resolution`: FLOAT (GSD in meters)
  - `geometry`: GEOMETRY(POLYGON, 4326) with GiST Index
  - `asset_url`, `thumbnail_url`: VARCHAR(1000)
  - `metadata_payload`: JSONB
  - `created_at`: TIMESTAMPTZ

### Schema 5: `analysis`
- **`analysis.runs`**:
  - `id`: UUID (Primary Key)
  - `project_id`: UUID (Foreign Key to `workspace.projects.id` ON DELETE CASCADE)
  - `area_of_interest_id`: UUID (Foreign Key to `workspace.areas_of_interest.id` ON DELETE CASCADE)
  - `status`: ENUM (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`)
  - `analysis_type`: VARCHAR(100) (`BI_TEMPORAL_CHANGE`, `MULTI_YEAR_TIMELINE`, `URBAN_EXPANSION`)
  - `start_date`, `end_date`: TIMESTAMPTZ (`end_date >= start_date` Check Constraint)
  - `parameters`: JSONB (Algorithm settings, indices, thresholds)
  - `pipeline_version`: VARCHAR(50)
  - `started_at`, `completed_at`: TIMESTAMPTZ
  - `error_message`: TEXT
  - `created_at`, `updated_at`: TIMESTAMPTZ

### Schema 6: `intelligence`
- **`intelligence.measurements`**:
  - `id`: UUID (Primary Key)
  - `analysis_run_id`: UUID (Foreign Key to `analysis.runs.id` ON DELETE CASCADE)
  - `measurement_type`: VARCHAR(100) (`mean_ndvi`, `affected_area_km2`, `built_up_km2`, `road_length_km`)
  - `value`: FLOAT (Authoritative scalar value - read only for AI)
  - `unit`: VARCHAR(50) (`km2`, `ha`, `percent`, `meters`)
  - `uncertainty`: FLOAT ($\pm \text{delta}$)
  - `epistemic_level`: ENUM (`OBSERVED`, `CALCULATED`, `DETECTED`, `ESTIMATED`, `PREDICTED`, `AI_INTERPRETATION`)
  - `methodology`: VARCHAR(255)
  - `source`: VARCHAR(255)
  - `created_at`: TIMESTAMPTZ
- **`intelligence.detected_changes`**:
  - `id`: UUID (Primary Key)
  - `analysis_run_id`: UUID (Foreign Key to `analysis.runs.id` ON DELETE CASCADE)
  - `change_type`: VARCHAR(100) (`VEGETATION_LOSS`, `URBAN_EXPANSION`, `WATER_RECESSION`)
  - `geometry`: GEOMETRY(MULTIPOLYGON, 4326) with GiST Index
  - `affected_area`: FLOAT ($km^2$)
  - `percentage_change`: FLOAT
  - `confidence`: FLOAT (0.0 to 1.0 Check Constraint)
  - `evidence_strength`: ENUM (`STRONG`, `MODERATE`, `LIMITED`, `INSUFFICIENT`)
  - `detection_method`: VARCHAR(255)
  - `before_date`, `after_date`: TIMESTAMPTZ (`after_date >= before_date` Check Constraint)
  - `created_at`: TIMESTAMPTZ
- **`intelligence.geographic_events`**:
  - `id`: UUID (Primary Key)
  - `analysis_run_id`: UUID (Foreign Key to `analysis.runs.id` ON DELETE CASCADE)
  - `event_type`: VARCHAR(100) (`URBAN_SPRAWL_EXPANSION`, `CANOPY_DEFORESTATION_SURGE`)
  - `geometry`: GEOMETRY(MULTIPOLYGON, 4326) with GiST Index
  - `severity`: VARCHAR(50)
  - `confidence`: FLOAT (0.0 to 1.0 Check Constraint)
  - `evidence_strength`: ENUM (`STRONG`, `MODERATE`, `LIMITED`, `INSUFFICIENT`)
  - `start_date`, `end_date`: TIMESTAMPTZ (`end_date >= start_date` Check Constraint)
  - `description`: TEXT
  - `created_at`: TIMESTAMPTZ
- **`intelligence.evidence_records`**:
  - `id`: UUID (Primary Key)
  - `analysis_run_id`: UUID (Foreign Key to `analysis.runs.id` ON DELETE CASCADE)
  - `source_type`: VARCHAR(100) (`SATELLITE_TELEMETRY`, `ROAD_VECTOR_REGISTRY`)
  - `source_id`: VARCHAR(255)
  - `claim_type`: VARCHAR(100)
  - `claim_reference`: VARCHAR(255)
  - `input_checksum`: VARCHAR(64) (Cryptographic SHA-256)
  - `processing_version`: VARCHAR(50)
  - `algorithm`: VARCHAR(100)
  - `parameters`: JSONB
  - `evidence_strength`: ENUM (`STRONG`, `MODERATE`, `LIMITED`, `INSUFFICIENT`)
  - `created_at`: TIMESTAMPTZ
- **`intelligence.reports`**:
  - `id`: UUID (Primary Key)
  - `analysis_run_id`: UUID (Foreign Key to `analysis.runs.id` ON DELETE CASCADE)
  - `title`: VARCHAR(255)
  - `report_type`: VARCHAR(100)
  - `status`: ENUM (`PENDING`, `GENERATING`, `COMPLETED`, `FAILED`)
  - `executive_summary`: TEXT
  - `file_path`: VARCHAR(1000)
  - `methodology_version`: VARCHAR(50)
  - `generated_at`: TIMESTAMPTZ
  - `created_at`: TIMESTAMPTZ

### Schema 7: `history_deep`
- **`history_deep.historical_annual_summaries`**:
  - `id`: UUID (Primary Key)
  - `area_of_interest_id`: UUID (Foreign Key to `workspace.areas_of_interest.id` ON DELETE CASCADE)
  - `year`: INTEGER
  - `support_classification`: ENUM (`STRONGLY_SUPPORTED`, `PARTIALLY_SUPPORTED`, `ESTIMATED`, `UNAVAILABLE`)
  - `summary_data`: JSONB
  - `data_sources`: JSONB
  - `created_at`, `updated_at`: TIMESTAMPTZ
  - `UniqueConstraint(area_of_interest_id, year)`
- **`history_deep.future_predictions`**:
  - `id`: UUID (Primary Key)
  - `area_of_interest_id`: UUID (Foreign Key to `workspace.areas_of_interest.id` ON DELETE CASCADE)
  - `prediction_type`: ENUM (`URBAN_EXPANSION`, `VEGETATION_TREND`, `WATER_COVERAGE`, `ROAD_DEVELOPMENT`, `LAND_USE_CHANGE`)
  - `target_year`: INTEGER
  - `prediction_value`: FLOAT
  - `lower_bound`, `upper_bound`: FLOAT
  - `unit`: VARCHAR(50)
  - `model_name`: VARCHAR(100)
  - `model_version`: VARCHAR(50)
  - `training_start_year`, `training_end_year`: INTEGER
  - `confidence`: FLOAT (0.0 to 1.0)
  - `evidence_strength`: ENUM (`STRONG`, `MODERATE`, `LIMITED`, `INSUFFICIENT`)
  - `scenario`: VARCHAR(100)
  - `assumptions`, `limitations`: JSONB
  - `created_at`: TIMESTAMPTZ
  - Check Constraints: `target_year > training_end_year`, `training_end_year >= training_start_year`, `upper_bound >= lower_bound`
- **`history_deep.geological_epochs`**:
  - `id`: UUID (Primary Key)
  - `name`: VARCHAR(100) (Unique)
  - `start_age`: FLOAT (Millions of Years Ago, Ma)
  - `end_age`: FLOAT (Ma) (`start_age >= end_age` Check Constraint)
  - `description`: TEXT
  - `evidence_type`: VARCHAR(100)
  - `source`: VARCHAR(255)
  - `confidence`: FLOAT
  - `created_at`: TIMESTAMPTZ
- **`history_deep.islamic_geographic_records`**:
  - `id`: UUID (Primary Key)
  - `title`: VARCHAR(255)
  - `source_type`: VARCHAR(100)
  - `classification`: ENUM (`QURAN`, `MUTAWATIR_HADITH`, `AHAD_SAHIH`, `SCHOLARLY_IJMA`, `HISTORICAL_TARIKH`, `UNVERIFIED_ISRAILIYYAT`)
  - `description`: TEXT
  - `date_reference`: VARCHAR(100)
  - `geographic_reference`: VARCHAR(255)
  - `geometry`: GEOMETRY(GEOMETRY, 4326) with GiST Index
  - `source`: VARCHAR(500)
  - `source_url`: VARCHAR(500)
  - `scholarly_notes`: TEXT
  - `confidence`: FLOAT
  - `created_at`: TIMESTAMPTZ

---

## 3. PostGIS Strategy & Spatial Computation Rules

1. **Canonical Coordinate System**:
   - All spatial geometries are stored in **SRID 4326 (WGS84 Lon/Lat)**.
2. **Authoritative Geodesic Calculations**:
   - Surface area and distance calculations MUST cast geometries to `geography` type to execute ellipsoidal computations on the true WGS84 spheroid:
   ```sql
   -- Authoritative surface area in km²
   SELECT ST_Area(geometry::geography, use_spheroid=true) * 1e-6 AS area_km2 
   FROM workspace.areas_of_interest;

   -- Authoritative road length in km
   SELECT ST_Length(geometry::geography, use_spheroid=true) * 1e-3 AS length_km 
   FROM geo.road_features;
   ```
3. **Spatial Indexing Strategy**:
   - Every spatial column across all schemas (`areas_of_interest.geometry`, `road_features.geometry`, `imagery_scenes.geometry`, `detected_changes.geometry`, `geographic_events.geometry`, `islamic_geographic_records.geometry`) is indexed with Generalized Search Trees (**GiST**), accelerating bounding-box spatial joins and viewport tile queries (`ST_Intersects`, `ST_DWithin`).

---

## 4. Migration & Seeding Workflows

### Running Migrations
```powershell
cd backend
.\venv\Scripts\Activate.ps1
alembic upgrade head
```

### Seeding Reference Metadata
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m app.db.seed
```
