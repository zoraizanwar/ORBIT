# ORBIT: System Architecture & Subsystem Specification

## 1. Architectural Style: Modular Monolith with Asynchronous Task Workers

ORBIT is designed as a **High-Performance Modular Monolith with Asynchronous Distributed Workers**. This architecture eliminates the operational and network latency overhead of microservices during local execution and initial scale, while enforcing strict domain isolation and interface decoupling across 15 core subsystems.

```
+-----------------------------------------------------------------------------------+
|                                  USER BROWSER                                     |
|  React 18 + TypeScript + Vite + MapLibre GL + Tailwind CSS + Radix UI + Recharts  |
+-----------------------------------------+-----------------------------------------+
                                          | HTTP / REST / Server-Sent Events (SSE)
                                          v
+-----------------------------------------------------------------------------------+
|                           ORBIT FASTAPI CORE SERVICE                              |
|                                                                                   |
|  [ Auth & Security ]   [ Location Search ]   [ Project & Workspace Mgmt ]        |
|  [ Road Network Svc ]  [ EO Discovery Svc ]  [ Historical Intel Gateway ]        |
|  [ Vector Tile Server] [ Report Dispatcher]  [ Deep History / Islamic Svc ]      |
+-----------------------------------------+-----------------------------------------+
       |                                  |
       | Celery Tasks / RPC               | SQL / PostGIS Spatial Queries
       v                                  v
+-----------------------------+    +------------------------------------------------+
|    CELERY WORKER CLUSTER    |    |               POSTGRESQL 16 + POSTGIS          |
|                             |    |                                                |
|  * Raster Processing Engine |    |  * Vector Roads (GiST / pgRouting)             |
|  * Computer Vision / Change |    |  * AOI Geometries & Admin Boundaries           |
|  * Geospatial Measurements  |    |  * Analysis Runs & Execution DAGs              |
|  * Event Clustering Engine  |    |  * Geographic Events & Time-Series Metrics     |
|  * Provenance Compiler      |    |  * Cryptographic Evidence Records              |
|  * AI Narrative Synthesizer |    |  * User / Project / Audit Schemas              |
+--------------+--------------+    +------------------------------------------------+
               |
               v
+-----------------------------------------------------------------------------------+
|                        STORAGE & ARTIFACT LAYER                                   |
|                                                                                   |
|  * Redis 7.2 (Queue Broker, Result Backend, Tile & Metadata Cache)                |
|  * Local Object/File Tier (COGs, GeoTIFFs, Cloud Mask NetCDFs, PDF Reports)       |
|  * Remote Zero-Cost STAC Endpoints (Copernicus CDSE, Microsoft PC, AWS USGS)      |
+-----------------------------------------------------------------------------------+
```

---

## 2. Subsystem Decomposition & Service Boundaries

ORBIT is partitioned into **15 distinct, cohesive subsystems**. Each subsystem maintains dedicated domain schemas, repositories, services, and internal interfaces.

### Subsystem 1: Global Geospatial Engine
- **Purpose**: Core coordinate system transformations, bounding box calculations, spatial indexing, projection normalization, spatial geometry validation.
- **Responsibilities**: EPSG:4326 (WGS84) to EPSG:3857 (Web Mercator) and UTM projection management, GeoJSON parsing/serialization, PostGIS geometry conversions, validity repair (`ST_MakeValid`).

### Subsystem 2: Road Network Engine
- **Purpose**: Ingestion, indexing, hierarchical filtering, vector tile generation, and topological analysis of mapped road and street networks.
- **Responsibilities**: OpenStreetMap PBF parsing, highway hierarchy tagging (Motorway down to Service/Track), dynamic MVT (Mapbox Vector Tile) generation via PostGIS `ST_AsMVT`, road buffer extraction for infrastructure change correlation.

### Subsystem 3: Location Search Engine
- **Purpose**: Global geocoding, reverse geocoding, administrative region resolution, and spatial autocomplete.
- **Responsibilities**: Forward geocoding to bounding boxes and centroid coordinates, hierarchical administrative boundary lookup (Country $\rightarrow$ Admin1/State $\rightarrow$ Admin2/County $\rightarrow$ City/Settlement $\rightarrow$ Postal/Locality), local Gazetteer caching.

### Subsystem 4: Earth Observation (EO) Data Engine
- **Purpose**: Multi-provider metadata cataloging, spatial/temporal querying, cloud-cover filtering, scene asset acquisition, and licensing tracking.
- **Responsibilities**: Abstract `EarthObservationProvider` interface implementing connectors for Copernicus Open Access / CDSE (Sentinel-1, Sentinel-2), USGS Landsat (via AWS/Element84 STAC), and Microsoft Planetary Computer STAC. Handles rate limiting, authenticated token refreshes, and scene metadata normalization.

### Subsystem 5: Raster Processing Engine
- **Purpose**: Ingesting, reprojecting, windowed reading, radiometric calibration, cloud masking, and spectral index synthesis from multi-spectral and SAR raster assets.
- **Responsibilities**: Cloud-Optimized GeoTIFF (COG) windowed reads via `rasterio`, QA pixel-mask decoding (SCL / QA_PIXEL), band math calculation ($NDVI$, $NDWI$, $NDBI$, $SAVI$, $MNDWI$, $EVI$), SAR backscatter calibration ($\sigma^0$ in dB).

### Subsystem 6: Computer Vision & Change Detection Engine
- **Purpose**: Detecting bi-temporal and multi-temporal land-cover, infrastructure, vegetation, and hydrologic transitions across raster scenes.
- **Responsibilities**: Pixel-wise differencing ($\Delta \text{Index}$), adaptive Otsu thresholding, CCDC (Continuous Change Detection and Classification) time-series fitting, morphological noise reduction (opening/closing), polygonization of raster change masks (`rasterio.features.shapes`).

### Subsystem 7: Geospatial Measurement Engine
- **Purpose**: Authoritative, mathematically deterministic geometric and physical calculations over detected spatial features.
- **Responsibilities**: PostGIS geodesic surface area calculation on spheroids (`ST_Area(geom::geography)`), perimeter and centerline lengths (`ST_Length`), spatial intersection matrices (`ST_Intersection`), fragmentation indices, and percentage change computations.

### Subsystem 8: Geographic Event Engine
- **Purpose**: Structuring contiguous spatial changes across time into discrete, tracked "Geographic Events" with defined lifecycles.
- **Responsibilities**: Spatiotemporal clustering (`ST_ClusterDBSCAN`), temporal lifecycle state tracking (`INITIAL_OBSERVATION`, `EXPANDING`, `STABILIZED`, `REVERSED`), event centroid tracking, correlation with road and infrastructure vectors.

### Subsystem 9: Evidence & Provenance Engine
- **Purpose**: Maintaining an immutable, cryptographically verifiable audit trail of every analytical output from raw telemetry to final brief.
- **Responsibilities**: Generating Directed Acyclic Graphs (DAGs) of analytical lineage, recording dataset scene IDs, acquisition datetimes, processing parameters, software commit hashes, and SHA-256 checksums of source rasters.

### Subsystem 10: Historical Intelligence Engine
- **Purpose**: Compiling multi-decadal chronologies and structured year-by-year baseline profiles of analyzed geographic domains.
- **Responsibilities**: Aggregating historical indices and detected events into annual intelligence summaries, identifying inflection years (e.g., rapid urbanization spikes, catastrophic drought years), synthesizing trend metrics.

### Subsystem 11: AI Intelligence Engine
- **Purpose**: Generating high-level executive briefs, analytical narratives, and historical explanations strictly grounded in verified facts.
- **Responsibilities**: Constructing zero-hallucination prompt payloads injecting verified metrics and evidence trees, executing strict JSON-schema validated LLM inference, asserting epistemic labels (`AI_INTERPRETATION`), blocking ungrounded numeric hallucination.

### Subsystem 12: Deep History & Islamic Sources Engine
- **Purpose**: Integrating deep geological/archaeological timelines and an authenticated, scholarly-classified Islamic sources historical layer.
- **Responsibilities**: Curating deep-time geological epoch markers, ancient geographical descriptions, and Islamic historical records with rigorous source classification (`QURAN`, `MUTAWATIR_HADITH`, `AHAD_SAHIH`, `SCHOLARLY_IJMA`, `HISTORICAL_TARIKH`, `UNVERIFIED_ISRAILIYYAT`).

### Subsystem 13: Analysis Management & Orchestration
- **Purpose**: Managing user projects, Areas of Interest (AOIs), analysis run queues, execution lifecycle states, and Celery task coordination.
- **Responsibilities**: State machine management (`QUEUED`, `INGESTING`, `PROCESSING`, `ANALYZING`, `SYNTHESIZING`, `COMPLETED`, `FAILED`), progress reporting via Server-Sent Events (SSE), cancellation handling, idempotency checks.

### Subsystem 14: Report Generation Engine
- **Purpose**: Compiling authoritative, multi-format intelligence dossiers and dossiers for institutional dissemination.
- **Responsibilities**: Rendering PDF reports with embedded high-resolution map renders, spectral charts, metric tables, provenance annexes, and executive summaries (HTML/CSS to PDF via headless browser/WeasyPrint), exporting structured STAC and GeoJSON packages.

### Subsystem 15: Authentication & Security Subsystem
- **Purpose**: Identity management, token lifecycle, role-based access control, tenant data isolation, and API protection.
- **Responsibilities**: Argon2id password hashing, asymmetric JWT token validation, rate-limiting middleware, spatial query bounding box sanitization, secure file isolation.

---

## 3. Communication Protocols & Inter-Service Interaction

| Producer Subsystem | Consumer Subsystem | Mechanism | Payload / Interface |
|---|---|---|---|
| Frontend Client | FastAPI Core | HTTPS REST / JSON | Standardized REST requests, GeoJSON payloads |
| Frontend Client | Analysis Orchestrator | HTTPS Server-Sent Events (SSE) | Real-time analysis status, progress %, execution step logs |
| Analysis Orchestrator | Celery Worker Cluster | Redis AMQP Message Queue | Task message with `analysis_run_id`, serialized AOI, and execution DAG parameters |
| EO Data Engine | Public STAC Endpoints | HTTPS REST / STAC 1.0.0 | STAC Query payloads, GeoJSON bounding polygons, date intervals |
| Raster Engine | Celery Tasks | In-Process Python Memory & COG Reads | NumPy ndarrays, GDAL/Rasterio DatasetReaders, MemoryFiles |
| Measurement Engine | PostgreSQL / PostGIS | Async SQLAlchemy Core / GeoAlchemy2 | Parameterized spatial SQL (`ST_Area`, `ST_ClusterDBSCAN`, `ST_AsMVT`) |
| Celery Workers | Redis Backend | Redis Key-Value / PubSub | Task status updates, intermediate cache tensors, ephemeral locks |
| AI Intelligence Svc | LLM Provider (Local / API) | HTTPS REST (OpenAI/Anthropic compatible) | Structured System Prompt + Evidence JSON $\rightarrow$ Validated JSON schema response |
