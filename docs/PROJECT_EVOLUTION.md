# ORBIT Platform Engineering Evolution

This document chronicles the sequential technical progression of the ORBIT platform from initial architectural specifications to a fully operational, multi-source Earth Observation and Grounded AI geospatial intelligence system.

---

## Evolution Summary Matrix

| Phase | Milestone Name | Primary Technical Scope | Key Verification Artifacts |
| :--- | :--- | :--- | :--- |
| **Phases 1–4** | **Foundational Architecture & Database** | PostgreSQL 16 + PostGIS 3.4 spatial schemas, FastAPI async engine, React 18 frontend shell | Alembic Revisions 0001–0004, 7 core schemas (auth, geo, eo, etc.) |
| **Phase 5** | **MapLibre Geospatial Engine** | MapLibre GL JS 4.7 WebGL map engine, MapTiler & OSM basemap integration, geodesic math | Interactive workstation, EPSG:4326/EPSG:3857 coordinate transformations |
| **Phase 9** | **Raster Processing & Spectral Engine** | Windowed COG reads via rasterio, deterministic band math (NDVI, NDWI, NDBI, SAVI) | Cloud/NoData masking, memory-bounded sub-pixel calculations |
| **Phase 10** | **Multi-Temporal Change Detection** | Sequential T1 -> Tn trajectory analysis, directional persistence, recovery rebound | PostGIS geodesic area calculation (ST_Area on spheroid) |
| **Phase 11** | **Advanced Geospatial Evidence System** | Evidence DAG assembly, spatial buffering, proximity analysis to road infrastructure | Multi-criteria evidence scoring, Alembic Revision 0006 |
| **Phase 12** | **Forecasting & Predictive Analytics** | Time-series forecasting (trend, harmonic decomposition), 95% confidence intervals | Strict epistemic separation of historical observations vs. future projections |
| **Phase 13** | **Grounded AI Intelligence Synthesis** | Anti-hallucination validation gate, claim-by-claim citations, uncertainty disclosure | Zero ungrounded statements, SHA-256 evidence package signing |
| **Phase 14** | **Defensive Hardening & Security** | SSRF defense, path traversal jails, 256MB decompression caps, credential redaction | Security test suite (test_security_hardening.py), sanitized error envelopes |
| **Phase 15** | **Real-World EO Data Integration** | AWS Earth Search STAC API querying, deterministic multi-criteria scene ranking | Pre-analytical GeoTIFF validation, SHA-256 asset checksums |
| **Phase 16** | **Operational Workstation & Live EO** | Full-screen MapLibre workstation, AOI lifecycle tracking, difference overlays | Dual-mode UI (Analyst / Executive), interactive report generation modal |
| **Phase 17** | **Multi-Source EO Fusion** | Optical (Sentinel-2) + SAR (Sentinel-1) + OSM vector road fusion, contradiction engine | Pairwise alignment, cross-sensor contradiction detection without data erasure |

---

## Detailed Technical Evolution

### Phases 1–4: Architecture, Local Setup, PostGIS Foundation & UI Shell
- Established the foundational monorepo structure separating backend/ (FastAPI, Python 3.11+, SQLAlchemy 2.0 Async, GeoAlchemy2) and frontend/ (React 18, TypeScript, Vite, Tailwind CSS).
- Designed the master relational and spatial database schema across 7 dedicated PostgreSQL schemas: auth, workspace, geo, eo, analysis, intelligence, and history_deep.
- Deployed initial transactional Alembic migrations configuring spatial GiST indices and PostGIS WGS84 geodesic geometry columns.

### Phase 5: MapLibre Map Rendering Engine
- Replaced static placeholder views with an interactive, WebGL-accelerated MapLibre GL JS engine.
- Configured dynamic vector and raster basemap streaming using MapTiler Cloud with graceful offline/fallback capabilities to OpenStreetMap tiles.
- Implemented client-side geodesic scale bars, cardinal coordinate parsers, and interactive bounding-box AOI selection tools.

### Phase 9: Raster Processing & Spectral Analytics Engine
- Developed windowed raster reading routines using rasterio and GDAL to enable sub-region Cloud-Optimized GeoTIFF (COG) extraction without loading entire multi-gigabyte satellite scenes into RAM.
- Implemented deterministic band mathematics for four authoritative spectral indices:
  - **NDVI** (Normalized Difference Vegetation Index) for canopy health and biomass tracking.
  - **NDWI** (Normalized Difference Water Index) for open water body and shoreline delineation.
  - **NDBI** (Normalized Difference Built-up Index) for artificial impervious surface and urban construction detection.
  - **SAVI** (Soil-Adjusted Vegetation Index) with L=0.5 correction factor for arid and semi-arid terrain.
- Added dynamic pixel masking for cloud confidence, shadow flags, and NoData boundary values.

### Phase 10: Multi-Temporal Change Detection & Trajectory Persistence
- Created the bi-temporal and sequential change detection engine to evaluate environmental shifts between baseline (T1) and target (T2, ..., Tn) satellite acquisitions.
- Engineered trajectory persistence algorithms that classify whether observed spectral changes represent permanent land-use transitions (e.g., clear-cut deforestation), seasonal agricultural cycles, or post-disturbance vegetation rebound.
- Integrated PostGIS spatial spheroid geometry functions (ST_Area(geog, true)) for accurate surface area measurements in square kilometers and hectares.

### Phase 11: Advanced Geospatial Intelligence & Evidence Engine
- Formulated the 4-tier Epistemic Evidence Strength scoring function, calculating confidence scores based on spatial resolution, cloud coverage, temporal proximity, and multi-sensor agreement.
- Implemented spatial buffering and corridor proximity analytics correlating detected canopy disturbances with transport infrastructure (such as highway corridors and unpaved logging access spurs).

### Phase 12: Forecasting & Predictive Modeling
- Built forward-looking predictive models leveraging trend regression and harmonic time-series decomposition over historical observation baselines.
- Enforced strict +/- 95% confidence interval envelopes (p < 0.01) alongside historical out-of-sample backtesting metrics (RMSE, R^2).
- Implemented hard epistemic boundary rules preventing future projections from being labeled or queried as historical observed facts.

### Phase 13: Grounded AI Intelligence Synthesis & Decision Support
- Engineered the Grounded AI reasoner responsible for synthesizing complex multi-sensor observations into human-readable, executive intelligence briefings.
- Established an automated anti-hallucination validation gate: any declarative claim generated by the reasoner must explicitly link to an underlying deterministic evidence record.
- Attached immutable SHA-256 cryptographic fingerprints to every evidence package and intelligence dossier.

### Phase 14: Defensive Hardening & Production Reliability
- Hardened external HTTP clients against Server-Side Request Forgery (SSRF) by blocking internal loopback (127.0.0.0/8), private RFC 1918 addresses, and link-local cloud metadata endpoints (169.254.169.254).
- Implemented strict path traversal defenses, 256 MB memory allocation limits, and automatic credential scrubbing in logs and API error envelopes.

### Phase 15: Real-World Earth Observation Integration
- Connected ORBIT to the live AWS Earth Search (Element84) STAC endpoint for on-demand scene discovery across Sentinel-2, Sentinel-1, and Landsat catalogs.
- Built a deterministic multi-criteria scene ranking algorithm prioritizing scenes with minimum cloud cover, optimal spatial coverage, and ground sample distance (GSD).
- Added pre-analytical GeoTIFF header verification validating TIFF magic bytes, CRS non-degeneracy, and affine transform parameters.

### Phase 16: Operational Geospatial Workstation
- Integrated visual analysis tools directly into the MapLibre frontend: interactive AOI management, multi-temporal footprint overlays, difference masks, and road corridor analysis.
- Designed a dual-audience user experience: intuitive plain-language summaries for executives and deep telemetry tables for technical analysts.
- Built a multi-format report export engine supporting on-screen dossier reading, standalone printable HTML/PDF generation with @media print styling, and structured Markdown export.

### Phase 17: Multi-Source EO Fusion & Cross-Sensor Contradiction Engine
- Enabled true multi-modal sensor fusion: combining multi-spectral optical imagery (Sentinel-2), all-weather Synthetic Aperture Radar (Sentinel-1 SAR C-band), and OpenStreetMap vector road data.
- Implemented pairwise spatial and temporal alignment checking Ground Sample Distances (GSD) and intersection metrics.
- Developed the Cross-Sensor Contradiction Engine: detects when optical signals conflict with radar backscatter (e.g., cloud shadow vs. true deforestation) and preserves both perspectives with adjusted evidence strength scores rather than averaging out discrepancies.
