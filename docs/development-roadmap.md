# ORBIT: Granular 26-Phase Engineering Roadmap

## 1. Master Phase Overview

ORBIT is engineered through **26 granular, sequentially verified phases**. Each phase contains explicit **Entry Criteria**, **Implementation Scope**, **Verification Criteria**, and **Exit Criteria**:

```
[ Phase 1: Product Architecture & Technical Design ] <--- CURRENT PHASE
    |
    v
[ Phase 2: Repository + Local Development Environment ]
    |
    v
[ Phase 3: PostgreSQL + PostGIS Foundation ]
    |
    v
[ Phase 4: ORBIT Design System + Frontend Shell ]
    |
    v
[ Phase 5: Global Map Engine (2D WebGL Workstation) ]
    |
    v
[ Phase 6: Global Road Network & Vector Tile Engine ]
    |
    v
[ Phase 7: Geographic Search & Gazetteer ]
    |
    v
[ Phase 8: Earth Observation Data Infrastructure & STAC Client ]
    |
    v
[ Phase 9: Raster Processing & Radiometric Band Math Engine ]
    |
    v
[ Phase 10: Vegetation + Water Intelligence Subsystem ]
    |
    v
[ Phase 11: Urban / Built-up Analysis Subsystem ]
    |
    v
[ Phase 12: Infrastructure + Road Intelligence Subsystem ]
    |
    v
[ Phase 13: Change Detection Engine (Tiered Levels 1-4) ]
    |
    v
[ Phase 14: Geospatial Measurements + Evidence & Provenance Engine ]
    |
    v
[ Phase 15: Historical Timeline + Yearly Intelligence Engine ]
    |
    v
[ Phase 16: Disaster / Spatiotemporal Event Intelligence ]
    |
    v
[ Phase 17: AI Intelligence & Anti-Hallucination Validation Gate ]
    |
    v
[ Phase 18: Analysis Workspace & Project Management ]
    |
    v
[ Phase 19: Professional Intelligence Dashboard & Split-Screen Workstation ]
    |
    v
[ Phase 20: Report Generation Engine (Publication-Grade PDF Dossiers) ]
    |
    v
[ Phase 21: Authentication, Tenant Isolation & Security Hardening ]
    |
    v
[ Phase 22: Testing Suite + End-to-End Verification (Playwright) ]
    |
    v
[ Phase 23: Performance Optimization, Caching & Reliability ]
    |
    v
[ Phase 24: Scientific Earth History + Categorized Islamic Sources Module ]
    |
    v
[ Phase 25: Comprehensive Documentation & Methodology Publication ]
    |
    v
[ Phase 26: Portfolio Finalization, Polishing & System Handoff ]
```

---

## 2. Granular Phase Specifications

### Phase 1: Product Architecture & Technical Design *(Current)*
- **Entry Criteria**: Product specification and engineering directives provided.
- **Implementation Scope**: System blueprints, PostGIS DDL, 5-tier change detection, Evidence Strength framework, historical capability model, multi-modal sensing architecture, 2D workstation design, and 26-phase roadmap.
- **Verification Criteria**: Complete documentation suite created in `docs/` and `architecture/`. Zero application code written.
- **Exit Criteria**: Formal user sign-off and explicit Phase 1 approval.

### Phase 2: Repository + Local Development Environment
- **Entry Criteria**: Phase 1 formal sign-off.
- **Implementation Scope**: Git repo setup, Python 3.11 virtualenv with uv/pip-tools, Node.js 20 LTS, Docker Compose for PostgreSQL 16 + PostGIS 3.4 and Redis 7.2, pre-commit hooks, linters (Ruff, ESLint).
- **Verification Criteria**: `docker compose up -d` boots healthy database and Redis containers; Python/Node environments build cleanly.
- **Exit Criteria**: Environment healthcheck script returns exit code 0.

### Phase 3: PostgreSQL + PostGIS Foundation
- **Entry Criteria**: Phase 2 environment operational.
- **Implementation Scope**: SQLAlchemy 2.0 async engine, GeoAlchemy2 integration, Alembic migrations for all 7 schemas (`auth`, `workspace`, `geo`, `eo`, `analysis`, `intelligence`, `history_deep`), spatial indexes (GiST), DDL constraints.
- **Verification Criteria**: Migrations apply up and down without errors; automated test verifies PostGIS spatial query execution.
- **Exit Criteria**: Database schema migration test suite passes 100%.

### Phase 4: ORBIT Design System + Frontend Shell
- **Entry Criteria**: Node.js environment configured.
- **Implementation Scope**: Vite + React 18 + TypeScript scaffold, Tailwind CSS configuration with Tactical Dark and Scientific Light themes, Radix UI primitives, Lucide icons, responsive workstation docking layout.
- **Verification Criteria**: Workstation shell renders at 60fps with zero layout shifts; theme switcher toggles palettes seamlessly.
- **Exit Criteria**: Frontend design system component test suite passes.

### Phase 5: Global Map Engine
- **Entry Criteria**: Frontend shell ready.
- **Implementation Scope**: MapLibre GL 2D high-performance canvas integration, coordinate transformations (EPSG:4326 to EPSG:3857), bounding box selection tool, polygon drawing tool, view state synchronizer.
- **Verification Criteria**: MapLibre canvas renders global vector/raster basemaps with sub-second panning and polygon coordinate extraction.
- **Exit Criteria**: Interactive polygon drawing and viewport bounds tests pass.

### Phase 6: Global Road Network & Vector Tile Engine
- **Entry Criteria**: PostGIS database and MapLibre canvas active.
- **Implementation Scope**: OpenStreetMap PBF parser and importer into `geo.road_features`, dynamic PostGIS `ST_AsMVT` tile endpoint (`/api/v1/geo/tiles/roads/{z}/{x}/{y}.pbf`), 5-tier Level of Detail (LoD) zoom filtering, Redis tile cache.
- **Verification Criteria**: Dynamic vector tiles render roads from Motorway to Track by zoom level; tile response latency $< 25\text{ms}$ from cache.
- **Exit Criteria**: Road tile generation benchmark and rendering tests pass.

### Phase 7: Geographic Search & Gazetteer
- **Entry Criteria**: Road network and map canvas operational.
- **Implementation Scope**: Forward/reverse geocoding service (Nominatim / Photon integration), local gazetteer database, bounding box resolver, autocomplete search bar.
- **Verification Criteria**: Querying "Tokyo", "Suez Canal", or "Amazon Basin" returns accurate bounding polygons and smoothly zooms map.
- **Exit Criteria**: Geocoding accuracy and response caching tests pass.

### Phase 8: Earth Observation Data Infrastructure & STAC Client
- **Entry Criteria**: Core backend operational.
- **Implementation Scope**: Abstract `EarthObservationProvider` base class, concrete connectors for Copernicus CDSE, Microsoft Planetary Computer, and AWS USGS Landsat STAC APIs, modality suitability evaluator (Optical vs. SAR), licensing metadata catalog.
- **Verification Criteria**: STAC search queries return valid scene footprints, acquisition dates, cloud scores, and COG asset URLs.
- **Exit Criteria**: Provider STAC search and licensing compliance unit tests pass.

### Phase 9: Raster Processing & Radiometric Band Math Engine
- **Entry Criteria**: EO STAC client operational.
- **Implementation Scope**: Celery worker integration, `rasterio` windowed COG streaming (HTTP Range requests), Float32 band math, SCL and QA_PIXEL cloud/shadow masking, auto-UTM reprojection.
- **Verification Criteria**: Computes cropped cloud-masked NDVI/NDBI/MNDWI arrays within 5 seconds for sample $100\text{ km}^2$ AOI.
- **Exit Criteria**: Raster math and masking unit tests match analytical ground truth.

### Phase 10: Vegetation + Water Intelligence Subsystem
- **Entry Criteria**: Raster engine operational.
- **Implementation Scope**: NDVI, SAVI, EVI, MNDWI algorithms, seasonal baseline comparisons, water body surface area tracking, drought anomaly detection.
- **Verification Criteria**: Correctly segments water surfaces ($MNDWI > 0$) and dense canopy ($NDVI > 0.6$) across historical benchmarks.
- **Exit Criteria**: Hydrological and vegetation calculation test suite passes.

### Phase 11: Urban / Built-up Analysis Subsystem
- **Entry Criteria**: Raster engine operational.
- **Implementation Scope**: NDBI, Bare Soil Index (BSI), impervious surface index, urban sprawl envelope extraction, building density estimation.
- **Verification Criteria**: Accurately differentiates developed impervious surfaces from bare agricultural soil.
- **Exit Criteria**: Urban expansion detection tests pass.

### Phase 12: Infrastructure + Road Intelligence Subsystem
- **Entry Criteria**: Road network and urban subsystems ready.
- **Implementation Scope**: Spatial intersection between road buffer envelopes (`ST_DWithin`) and detected spectral change masks, linear infrastructure disturbance calculations.
- **Verification Criteria**: Detects new road clearing corridors and outputs linear kilometers of disturbance.
- **Exit Criteria**: Infrastructure correlation tests pass.

### Phase 13: Change Detection Engine (Tiered Levels 1–4)
- **Entry Criteria**: Subsystems 9–12 active.
- **Implementation Scope**: Bi-temporal pixel differencing ($\Delta I$), adaptive Otsu thresholding, morphological kernel filtering ($3 \times 3$), CCDC time-series trend fitting, vector polygonization (`rasterio.features.shapes`).
- **Verification Criteria**: Detects injected synthetic change zones and outputs clean multi-polygon change vectors.
- **Exit Criteria**: Tier 1–4 change detection integration tests pass.

### Phase 14: Geospatial Measurements + Evidence & Provenance Engine
- **Entry Criteria**: Change detection engine active.
- **Implementation Scope**: PostGIS geodesic surface area (`ST_Area(geom::geography)`), length calculations, Evidence Strength calculator ($ESI$), Lineage DAG generator, SHA-256 scene checksum recorder.
- **Verification Criteria**: Calculates ellipsoidal areas matching WGS84 benchmarks within $0.001\%$; persists complete audit DAG.
- **Exit Criteria**: Measurement precision and cryptographic evidence tests pass.

### Phase 15: Historical Timeline + Yearly Intelligence Engine
- **Entry Criteria**: Measurement and evidence engine ready.
- **Implementation Scope**: Multi-decadal historical capability model (1972–Present), annual profile synthesizer, support level classifier (`STRONGLY_SUPPORTED`, `PARTIALLY_SUPPORTED`, `ESTIMATED`, `UNAVAILABLE`), multi-year trend aggregator.
- **Verification Criteria**: Synthesizes 10-year annual vectors; asserts `INSUFFICIENT_EVIDENCE` for unobserved years without fabrication.
- **Exit Criteria**: Historical timeline synthesis test suite passes.

### Phase 16: Disaster / Spatiotemporal Event Intelligence
- **Entry Criteria**: Historical engine active.
- **Implementation Scope**: PostGIS `ST_ClusterDBSCAN` event extraction, lifecycle state tracker (`EMERGING`, `EXPANDING`, `STABILIZED`), disaster impact polygon analyzer (flood, wildfire, storm surge).
- **Verification Criteria**: Groups contiguous change pixels into discrete event entities with bounding hulls and temporal timestamps.
- **Exit Criteria**: Spatiotemporal event clustering tests pass.

### Phase 17: AI Intelligence & Anti-Hallucination Validation Gate
- **Entry Criteria**: Analytical pipeline and evidence engine complete.
- **Implementation Scope**: Grounded prompt compiler, immutable JSON Fact Sheet builder, structured JSON schema response parser, automated AST/Regex validation gate verifying zero ungrounded numbers.
- **Verification Criteria**: Validation gate passes valid grounded narratives; intercepts and rejects any hallucinated scalar value.
- **Exit Criteria**: AI grounding and anti-hallucination unit test suite passes 100%.

### Phase 18: Analysis Workspace & Project Management
- **Entry Criteria**: Backend analytical services complete.
- **Implementation Scope**: Project workspace CRUD, AOI manager, analysis run queue manager, Server-Sent Events (SSE) live progress dispatcher, execution history viewer.
- **Verification Criteria**: User can create projects, save AOIs, trigger runs, and observe real-time progress via SSE stream.
- **Exit Criteria**: Workspace and execution lifecycle integration tests pass.

### Phase 19: Professional Intelligence Dashboard & Split-Screen Workstation
- **Entry Criteria**: Frontend shell and backend workspace ready.
- **Implementation Scope**: Hardware-accelerated split-screen swipe curtain, interactive evidence inspector drawer, authoritative measurement table, historical timeline scrub bar, Recharts analytical sparklines.
- **Verification Criteria**: Analyst can swipe between baseline/comparison imagery, click change polygons to inspect evidence lineage, and scrub multi-year timeline.
- **Exit Criteria**: Workstation UI interaction test suite passes.

### Phase 20: Report Generation Engine
- **Entry Criteria**: Dashboard and measurement engine active.
- **Implementation Scope**: Headless PDF report compiler (WeasyPrint / Jinja2), high-resolution map snapshot renderer, chart embedder, evidence annex compiler, STAC/GeoJSON export packager.
- **Verification Criteria**: Generates publication-grade, ISO-standard PDF intelligence dossier containing authoritative measurements, maps, charts, and license attributions.
- **Exit Criteria**: PDF compilation and export verification tests pass.

### Phase 21: Authentication, Tenant Isolation & Security Hardening
- **Entry Criteria**: Endpoints and workflows complete.
- **Implementation Scope**: Argon2id password hashing, RS256/Ed25519 JWT dual-token rotation, SQL tenant query isolation, PostGIS geometry sanitization (`ST_MakeValid`), rate limiting, immutable audit logging.
- **Verification Criteria**: Unauthorized cross-tenant queries return HTTP 404/403; invalid/malformed geometries are safely sanitized.
- **Exit Criteria**: Security and authorization test suite passes.

### Phase 22: Testing Suite + End-to-End Verification (Playwright)
- **Entry Criteria**: Full application stack integrated.
- **Implementation Scope**: 12 automated Playwright E2E test flows covering user registration, location search, AOI drawing, EO discovery, analysis execution, evidence inspection, and report download.
- **Verification Criteria**: All 12 automated E2E user journeys pass with zero flaky steps or unhandled exceptions.
- **Exit Criteria**: Full CI/CD test suite reports 100% green pass rate.

### Phase 23: Performance Optimization, Caching & Reliability
- **Entry Criteria**: E2E tests passing.
- **Implementation Scope**: Redis multi-tier caching (MVTs, geocoding, STAC metadata), database query indexing optimization (`EXPLAIN ANALYZE`), Celery worker pre-fetching, memory leak audits.
- **Verification Criteria**: Vector tile response $< 20\text{ms}$; raster windowed processing memory footprint $< 1.5\text{GB}$ per worker.
- **Exit Criteria**: Performance benchmark suite meets all latency and throughput targets.

### Phase 24: Scientific Earth History + Categorized Islamic Sources Module
- **Entry Criteria**: Core intelligence workstation stable.
- **Implementation Scope**: Deep geological epoch timeline (Quaternary to Mesozoic), paleo-hydrological layer, scholarly-classified Islamic sources explorer with strict epistemic grading badges (`QURAN`, `MUTAWATIR_HADITH`, `AHAD_SAHIH`, `SCHOLARLY_IJMA`, `HISTORICAL_TARIKH`, `UNVERIFIED_ISRAILIYYAT`).
- **Verification Criteria**: Renders deep-time stratigraphy and authenticated Islamic geographic records with zero fabricated dates or traditions.
- **Exit Criteria**: Deep history module unit and content verification tests pass.

### Phase 25: Comprehensive Documentation & Methodology Publication
- **Entry Criteria**: All features implemented.
- **Implementation Scope**: Developer onboarding guides, API reference docs (OpenAPI/Swagger), mathematical methodology whitepaper, user workstation manual, dataset license directory.
- **Verification Criteria**: Complete documentation suite verified for clarity, technical rigor, and architectural synchronization.
- **Exit Criteria**: Documentation review and static site build pass.

### Phase 26: Portfolio Finalization, Polishing & System Handoff
- **Entry Criteria**: All previous 25 phases verified.
- **Implementation Scope**: UI micro-interactions and polish, demo scenario dataset seeding (e.g. Aral Sea desiccation, Amazon corridor deforestation, urban growth in Cairo), sample PDF dossier generation, final portfolio readiness audit.
- **Verification Criteria**: Clean local startup via single command (`docker compose up` + backend/frontend launch); flawless demo presentations.
- **Exit Criteria**: Final architecture and project handoff sign-off.
