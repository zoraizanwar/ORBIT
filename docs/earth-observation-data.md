# Earth Observation Data Infrastructure & STAC Discovery Subsystem

## 1. Executive Summary & Purpose

The **Earth Observation (EO) Data Infrastructure** in ORBIT provides a high-performance, provider-agnostic, metadata-first discovery subsystem grounded in the **SpatioTemporal Asset Catalog (STAC 1.0.0)** specification.

It enables analysts and automated spatial pipelines to discover, inspect, and register open satellite imagery across global archives—including the **Copernicus Programme (Sentinel-1 & Sentinel-2)**, **USGS/NASA Landsat (Landsat 4–9)**, and **AWS Open Data / Microsoft Planetary Computer**—while enforcing strict epistemic provenance, legal attribution, and architectural boundaries.

---

## 2. Epistemic Hierarchy & Strict Boundary Invariants

ORBIT classifies all incoming satellite telemetry according to strict epistemic constraints:

```
+-------------------------------------------------------------------------+
|                      EPISTEMIC SEPARATION MODEL                         |
+-------------------------------------------------------------------------+
|                                                                         |
|  [LEVEL 1: OBSERVED]                                                    |
|  - Raw STAC Item metadata from provider telemetry                       |
|  - Acquisition timestamps, platform, sensor, orbit path/row             |
|  - Direct asset URIs (HTTP/S3/GCS) & Cloud-Optimized GeoTIFF (COG) refs |
|  - Unaltered legal license & attribution text                           |
|                                                                         |
|  [LEVEL 2: CALCULATED]                                                  |
|  - Normalized cloud cover percentage (preserving NULL for SAR)          |
|  - Geodesic footprint area & polygon repair flags                       |
|  - Sensor suitability metrics (assess_modality_suitability)             |
|                                                                         |
|  [LEVEL 3: DETECTED]                                                    |
|  - Strictly reserved for Phase 9+ analytical engines                    |
|  - Raw STAC scenes are NEVER evidence of change                         |
|                                                                         |
|  [LEVEL 4: PREDICTED]                                                   |
|  - Future projections (2027–2050) requiring explicit scenario,          |
|    calibration baseline, and forecast model parameters                 |
|  - Satellite scenes NEVER masquerade as future projections              |
|                                                                         |
+-------------------------------------------------------------------------+
```

---

## 3. Supported Sensor Modalities & Normalization Architecture

| Sensing Modality | Constellation / Platform | Sensor / Instrument | Resolution | Bands / Polarizations | Cloud Handling |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OPTICAL_MULTISPECTRAL** | Sentinel-2A / Sentinel-2B | MSI (MultiSpectral Instrument) | 10m / 20m / 60m | B01–B12, B8A (Blue, Green, Red, NIR, SWIR) | Explicit `eo:cloud_cover` % (0.0–100.0%) |
| **OPTICAL_MULTISPECTRAL** | Landsat-8 / Landsat-9 | OLI-2 / TIRS-2 | 15m / 30m / 100m | B1–B11 (Coastal, Blue, Green, Red, NIR, SWIR, Thermal) | Explicit `eo:cloud_cover` % |
| **SAR_MICROWAVE** | Sentinel-1A / Sentinel-1B | C-SAR (C-band Synthetic Aperture Radar) | 10m–20m (GRD) | Dual polarization (`VV`, `VH`, `HH`, `HV`) | **Strictly `NULL`** (SAR penetrates clouds; never 0.0%) |
| **HYBRID_FUSION** | Multi-sensor Composite | Optical + SAR joint alignment | Dynamic | Fused bands | Derived in Phase 9+ analysis engines |

---

## 4. Relational Database Schema (`eo` Schema)

### `eo.dataset_registry`
Maintains legal provenance, redistributability, and commercial-use metadata.

```sql
CREATE TABLE eo.dataset_registry (
    id VARCHAR(50) PRIMARY KEY,
    provider VARCHAR(100) NOT NULL,
    dataset_name VARCHAR(255) NOT NULL,
    modality eo.sensing_modality NOT NULL,
    license VARCHAR(100) NOT NULL,
    attribution TEXT NOT NULL,
    terms_url VARCHAR(500),
    redistribution_allowed BOOLEAN NOT NULL DEFAULT TRUE,
    commercial_use_allowed BOOLEAN NOT NULL DEFAULT TRUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### `eo.imagery_scenes`
Records discovered satellite observations with authoritative EPSG:4326 polygon footprints and PostGIS GiST spatial indexing.

```sql
CREATE TABLE eo.imagery_scenes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id VARCHAR(50) NOT NULL REFERENCES eo.dataset_registry(id) ON DELETE CASCADE,
    provider_scene_id VARCHAR(255) UNIQUE NOT NULL,
    acquisition_datetime TIMESTAMPTZ NOT NULL,
    platform VARCHAR(100) NOT NULL,
    sensor VARCHAR(100) NOT NULL,
    modality eo.sensing_modality NOT NULL,
    cloud_cover FLOAT CHECK (cloud_cover IS NULL OR (cloud_cover >= 0.0 AND cloud_cover <= 100.0)),
    processing_level VARCHAR(50) NOT NULL,
    spatial_resolution FLOAT NOT NULL,
    geometry geometry(Polygon, 4326) NOT NULL,
    thumbnail_url VARCHAR(1000),
    metadata_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### `eo.imagery_assets`
Maintains references to individual spectral/radar bands and Cloud-Optimized GeoTIFFs (COGs).

```sql
CREATE TABLE eo.imagery_assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    imagery_scene_id UUID NOT NULL REFERENCES eo.imagery_scenes(id) ON DELETE CASCADE,
    asset_key VARCHAR(100) NOT NULL,
    href VARCHAR(1000) NOT NULL,
    media_type VARCHAR(100),
    roles JSONB DEFAULT '[]'::jsonb,
    title VARCHAR(255),
    band_metadata JSONB DEFAULT '{}'::jsonb,
    gsd FLOAT,
    nodata FLOAT,
    file_size BIGINT,
    checksum VARCHAR(128),
    is_cloud_optimized BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 5. API Reference (`/api/v1/eo`)

### 1. `GET /api/v1/eo/providers`
Returns metadata and endpoint URLs for configured STAC catalogs.

### 2. `GET /api/v1/eo/collections`
Returns supported satellite collections across open providers.

### 3. `POST /api/v1/eo/search`
Searches STAC catalogs by bounding box, intersects geometry, datetime range, modality, and cloud cover.
- **Request Body**: `STACSearchRequest`
- **Response**: `STACSearchResponse`

### 4. `POST /api/v1/eo/modality-assessment`
Calculates sensor suitability metrics for a candidate list of discovered scenes.
- **Epistemic Classification**: `CALCULATED`

### 5. `POST /api/v1/eo/scenes/register`
Idempotently registers a discovered STAC scene and its assets into `eo.imagery_scenes` and `eo.imagery_assets`.

### 6. `GET /api/v1/eo/scenes/{scene_id}`
Retrieves registered scene metadata and its GeoJSON footprint.

### 7. `GET /api/v1/eo/scenes/{scene_id}/assets`
Retrieves all asset references and COG metadata for a scene.

### 8. `GET /api/v1/eo/health`
Checks reachability of remote STAC provider endpoints.

---

## 6. Frontend Earth Observation Workstation Integration

The ORBIT frontend incorporates:
- **`ImageryDiscoveryPanel`**: A dedicated modal and side-panel in `MapWorkspace` allowing real-time searching by AOI, sensing modality, date range, and maximum cloud cover.
- **Footprint Canvas Rendering**: Real-time rendering of scene footprints (`scene-footprint-fill` & `scene-footprint-outline`) on MapLibre GL JS with automatic camera centering.
- **Unified Inspector**: Syncs selected scene telemetry directly into `IntelligencePanel` with explicit `OBSERVED` badge, platform/sensor metadata, and legal attribution notices.
