# ORBIT Architecture: End-to-End Data Flow & Interaction Sequences

## 1. Complete End-to-End Pipeline Sequence

This diagram details the full lifecycle of an investigation from user location query to final intelligence report generation:

```mermaid
sequenceDiagram
    autonumber
    actor Analyst as Geospatial Analyst
    participant UI as ORBIT Frontend (React / MapLibre)
    participant API as FastAPI Core Service
    participant Redis as Redis Queue & Cache
    participant Worker as Celery Analytical Worker
    participant STAC as Public STAC Providers (CDSE / PC)
    participant PostGIS as PostgreSQL / PostGIS DB
    participant Artifact as Local Artifact Store
    participant LLM as Grounded LLM Synthesizer

    Analyst->>UI: 1. Searches location & draws AOI polygon
    UI->>API: POST /api/v1/workspace/aoi (GeoJSON Polygon)
    API->>PostGIS: ST_Area(geom::geography) $\rightarrow$ calculates surface area
    PostGIS-->>API: Surface area (e.g., 250.4 km²)
    API-->>UI: Returns AOI entity & live bounding box

    Analyst->>UI: 2. Selects time interval (2020 vs 2024), indices (NDVI, NDBI), clicks "Execute Analysis"
    UI->>API: POST /api/v1/analysis/runs (AOI_ID, Dates, Algorithms)
    API->>PostGIS: Insert analysis.runs (Status: 'QUEUED')
    API->>Redis: Enqueue Task `tasks.execute_analysis(run_id)`
    API-->>UI: Returns `run_id` & connects SSE stream `/api/v1/analysis/runs/{run_id}/stream`

    Redis->>Worker: Dequeue `execute_analysis`
    Worker->>API: Update Status: 'INGESTING', Progress: 15%
    Worker->>STAC: Query STAC API for cloud-free (<10%) Sentinel-2 scenes
    STAC-->>Worker: Return Scene Metadata & Asset COG URLs (B02, B03, B04, B08, B11, SCL)
    Worker->>PostGIS: Insert eo.imagery_scenes records

    Worker->>API: Update Status: 'PROCESSING', Progress: 40%
    Worker->>STAC: Windowed HTTP Range Read on AOI bounding box
    Worker->>Worker: Decode SCL Cloud Mask $\rightarrow$ Compute NDVI & NDBI arrays via NumPy
    Worker->>Artifact: Save Float32 Derived COGs (/artifacts/rasters/{run_id}_ndvi.tif)

    Worker->>API: Update Status: 'ANALYZING', Progress: 65%
    Worker->>Worker: Compute dNDVI matrix $\rightarrow$ Adaptive Otsu Thresholding $\rightarrow$ Morphological Filter
    Worker->>Worker: Vectorize change mask to GeoJSON polygons via `rasterio.features.shapes`
    Worker->>PostGIS: Execute ST_ClusterDBSCAN to group contiguous change features
    Worker->>PostGIS: Calculate Geodesic ST_Area(geom::geography) for all change polygons
    Worker->>PostGIS: Intersect change polygons with geo.road_features to flag corridor development
    Worker->>PostGIS: Insert intelligence.measurements, detected_changes, geographic_events, evidence_records

    Worker->>API: Update Status: 'SYNTHESIZING', Progress: 85%
    Worker->>Worker: Compile immutable JSON Fact Sheet containing authoritative measurements & evidence DAG
    Worker->>LLM: Post strict prompt + Fact Sheet with Temperature=0.0
    LLM-->>Worker: Return Structured JSON Briefing
    Worker->>Worker: Execute Anti-Hallucination Gate (verify all numbers against Fact Sheet)
    Worker->>Artifact: Render and compile ISO-grade PDF report via WeasyPrint
    Worker->>PostGIS: Insert intelligence.reports & update analysis.runs (Status: 'COMPLETED', Progress: 100%)

    API-->>UI: SSE Event: 'COMPLETED' (Payload: Measurements, Events, Artifact URIs)
    UI->>Analyst: Renders bi-temporal swipe map, vector change overlays, interactive evidence drawer, and PDF download button
```
