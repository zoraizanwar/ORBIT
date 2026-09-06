# ORBIT Architecture: System Context & Container Specifications (C4 Model)

## 1. System Context Diagram (C4 Level 1)

The System Context diagram illustrates how ORBIT interacts with external users, planetary satellite archives, and vector map registries:

```mermaid
graph TD
    User["Geospatial / Intelligence Analyst<br/>(Human User)"]
    
    subgraph ORBIT_System["ORBIT Platform<br/>(Geospatial Intelligence & Earth Monitoring System)"]
        Workstation["ORBIT Geospatial Workstation<br/>& Analytical Engine"]
    end
    
    OSM["OpenStreetMap Planet Registry<br/>(Geofabrik PBF / Overpass API)"]
    CDSE["Copernicus Data Space Ecosystem (CDSE)<br/>(Sentinel-1 SAR, Sentinel-2 MSI STAC API)"]
    PC["Microsoft Planetary Computer<br/>(Sentinel / Landsat / DEM STAC API)"]
    USGS["USGS / AWS Open Data<br/>(Landsat 4-9 Collection 2 STAC)"]
    LLM_Engine["Local / Hosted LLM Provider<br/>(Ollama Llama-3 / Gemini / Anthropic API)"]

    User -->|"Explores map, defines AOI, initiates analyses, inspects evidence, downloads reports"| Workstation
    Workstation -->|"Pulls global road network extracts & administrative nodes"| OSM
    Workstation -->|"Queries STAC metadata & windowed COG rasters"| CDSE
    Workstation -->|"Queries multi-temporal STAC assets & DEM grids"| PC
    Workstation -->|"Queries historical Landsat (1982-present) assets"| USGS
    Workstation -->|"Sends structured JSON fact sheet for grounded narrative synthesis"| LLM_Engine
```

---

## 2. Container Diagram (C4 Level 2)

The Container diagram decomposes ORBIT into deployable application units, storage repositories, and background queues:

```mermaid
graph TD
    subgraph Client_Tier["Client Tier"]
        BrowserApp["Single Page Application (SPA)<br/>[React, TypeScript, Vite, MapLibre GL, Tailwind]<br/>Interactive Geospatial Workstation"]
    end

    subgraph Application_Tier["Application & Compute Tier"]
        FastAPI_Core["ORBIT API Gateway & Core Service<br/>[Python 3.11, FastAPI, SQLAlchemy 2.0]<br/>REST API, MVT Tile Server, Auth, SSE Progress Dispatcher"]
        Celery_Workers["Distributed Task Workers<br/>[Python 3.11, Celery, Rasterio, NumPy, Shapely]<br/>Band Math, Change Detection, DBSCAN Clustering, PDF Generation"]
    end

    subgraph Infrastructure_Tier["Storage & Middleware Tier"]
        Redis_Broker["Message Broker & Cache<br/>[Redis 7.2]<br/>Celery Queue, MVT Tile Cache, Live Run State"]
        PostgreSQL_DB["Relational & Spatial Database<br/>[PostgreSQL 16 + PostGIS 3.4]<br/>Road Vectors, Scene Metadata, Measurements, Events, Evidence"]
        Artifact_Store["Local Artifact Storage Tier<br/>[Local Filesystem / MinIO S3 API]<br/>GeoTIFF COGs, Change Masks, PDF Dossiers"]
    end

    BrowserApp -->|"HTTPS / REST / SSE"| FastAPI_Core
    BrowserApp -->|"Direct Vector Tile Fetch (PBF)"| FastAPI_Core
    FastAPI_Core -->|"Dispatches Tasks (AMQP)"| Redis_Broker
    FastAPI_Core -->|"Async SQL / PostGIS Queries"| PostgreSQL_DB
    FastAPI_Core -->|"Reads / Writes Cache"| Redis_Broker
    FastAPI_Core -->|"Serves Reports / Assets"| Artifact_Store

    Celery_Workers -->|"Consumes Tasks"| Redis_Broker
    Celery_Workers -->|"Reads / Writes Spatial Results & Evidence"| PostgreSQL_DB
    Celery_Workers -->|"Saves Derived COGs & PDF Reports"| Artifact_Store
    Celery_Workers -->|"HTTP Range Windowed Reads"| CDSE
    Celery_Workers -->|"HTTP Range Windowed Reads"| PC
```
