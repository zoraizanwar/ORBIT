# ORBIT: Geospatial Intelligence & Earth Monitoring Platform

[![Backend Tests](https://img.shields.io/badge/Backend%20Tests-205%2F205%20Passed-emerald?style=flat-square)](./backend/tests)
[![Frontend Tests](https://img.shields.io/badge/Frontend%20Tests-54%2F54%20Passed-emerald?style=flat-square)](./frontend/src/tests)
[![Production Build](https://img.shields.io/badge/Production%20Build-Verified-blue?style=flat-square)](./frontend)
[![Platform Status](https://img.shields.io/badge/Phase%2017-Multi--Source%20Fusion-purple?style=flat-square)](./docs/development-roadmap.md)
[![License](https://img.shields.io/badge/License-Proprietary%20%2F%20Open%20Data-amber?style=flat-square)](./docs/dataset-strategy.md)

ORBIT is a local-first, enterprise-grade geospatial intelligence and Earth observation monitoring platform. It combines calibrated multi-spectral satellite imagery (Sentinel-2), SAR microwave data (Sentinel-1), OpenStreetMap road networks, PostGIS spatiotemporal clustering, time-series forecasting, and an anti-hallucination Grounded AI reasoner to produce verifiable, cryptographically signed intelligence dossiers.

---

## 1. Core Architectural Invariants

ORBIT strictly separates software logic across an inviolable **Epistemological Ladder**:

```
[ LEVEL 4: AI_INTERPRETED ]
  └── Grounded LLM reasoning, claim-by-claim citations, uncertainty statements.
      STRICT PROHIBITION: Can NEVER upgrade findings to OBSERVED or CALCULATED.
[ LEVEL 3: PREDICTED ]
  └── Statistical forecasting (CCDC, Ridge regression) with 95% uncertainty bounds.
[ LEVEL 2: DETECTED ]
  └── Multi-sensor corroboration/contradiction, persistent change, DBSCAN clusters.
[ LEVEL 1: CALCULATED ]
  └── Deterministic spectral indices (NDVI, NDWI, NDBI), multi-temporal trajectories, alignments.
[ LEVEL 0: OBSERVED ]
  └── Raw sensor telemetry (Sentinel-1 SAR, Sentinel-2 Optical, Landsat-8/9) and OSM road vectors.
```

---

## 2. Platform Capabilities

- **Multi-Source Earth Observation Fusion**: Multi-modal alignment (Optical MSI, SAR C-band, OSM vector networks), pairwise spatial IoU/temporal tolerance checks, and GSD resolution matching.
- **Multi-Temporal Change Series & Persistence**: Sequential $T_1 \to T_2 \to \dots \to T_n$ trajectory analysis, directional persistence across multiple epochs, recovery rebound detection, and oscillation analysis.
- **Cross-Sensor Contradiction Engine**: Evaluates optical canopy shifts against SAR structural backscatter and infrastructure context without erasing or consensus-averaging conflicting evidence.
- **Deterministic Evidence Strength Scoring**: Multi-criteria evidence scoring function integrating observation quality, cadence regularity, spatial overlap, corroboration bonus, and contradiction penalties.
- **Operational Geospatial Workstation**: Interactive MapLibre GL workspace with AOI session management, multi-temporal footprint overlays, difference masks, and road corridors.
- **Real Earth Observation Discovery & Ingestion**: Direct STAC queries to Element84 / AWS Earth Search with deterministic multi-criteria scene ranking.
- **Secure Asset Acquisition & Local Caching**: Streaming downloader with SSRF protection (rejecting loopback, RFC 1918, cloud metadata IPs), path traversal guards, 256MB size cap, and SHA-256 integrity verification.
- **Pre-Analytical Raster Validation**: GeoTIFF/COG header inspection validating TIFF magic bytes, dimensions ($1 \le w, h \le 16384$), CRS, affine transformation non-degeneracy, and checksum verification without loading entire pixel arrays into memory.
- **Calibrated Spectral Processing Engine**: Efficient windowed COG reads, sub-pixel NDVI/NDWI/NDBI calculation, dynamic masking of clouds and nodata.
- **Forward-Looking Time-Series Forecasting**: Annual and quarterly aggregation, trend projection with confidence bounds, historical out-of-sample backtesting diagnostics, and strict data guards preventing synthetic observation fabrication.
- **Grounded AI Intelligence Synthesis**: Citation-grounded executive summaries, epistemic validation gates, and uncertainty disclosure.
- **Cryptographic Provenance**: Immutable SHA-256 digital fingerprinting of evidence packages and final intelligence dossiers.

---

## 3. Technology Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic, SQLAlchemy 2.0 (Async), GeoAlchemy2, Rasterio, NumPy, Shapely.
- **Database**: PostgreSQL 16 + PostGIS 3.4 Spatial Database (WGS84 Geodesics).
- **Background Tasks & Cache**: Celery 5.3 + Redis 7.2 (Queue Broker & Vector Tile Cache).
- **Frontend Workstation**: React 18, TypeScript, Vite, MapLibre GL, Tailwind CSS, Lucide Icons.
- **Reporting & Dossiers**: Structured Markdown & ISO-grade Base64-encoded PDF documents.

---

## 4. Local Development Quickstart (Windows PowerShell)

### 1. Prerequisites
- Python 3.11+ (`py --version`)
- Node.js 18+ (`node --version`)
- Docker Desktop with Compose (`docker --version`)

### 2. Environment Setup
```powershell
# In project root
Copy-Item .env.example .env
```

### 3. Start Infrastructure (PostgreSQL/PostGIS & Redis)
```powershell
docker compose up -d
```

### 4. Start Backend Service
```powershell
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Documentation: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/api/v1/health`

### 5. Start Celery Worker (in a new terminal)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
celery -A app.celery_app.celery_app worker --loglevel=info --pool=solo
```

### 6. Start Frontend Workstation (in a new terminal)
```powershell
cd frontend
npm install
npm run dev
```
- Web Workstation: `http://127.0.0.1:5173`

---

## 5. Verification & Test Execution

Run the complete regression suites:

```powershell
# Backend Regression Suite (205 tests)
cd backend
py -m pytest -v

# Frontend Regression Suite (54 tests)
cd ../frontend
npm test

# Frontend Production Build
npm run build
```

---

## 6. Real-World Case Studies & Architectural Documentation

- [Multi-Source Earth Observation Fusion](./docs/multi-source-fusion.md)
- [Operational Workstation Architecture](./docs/operational-workstation.md)
- [Real-World EO Data Integration](./docs/real-data-integration.md)
- [Operational Case Study: Sinop Canopy Dynamics](./docs/operational-validation.md)
- [Dataset Provenance & Cryptographic Lineage](./docs/dataset-provenance.md)
- [Epistemic Model Invariants](./docs/epistemic-model.md)
- [Grounded AI Architecture](./docs/ai-architecture.md)
- [Security & Defensive Hardening](./docs/security.md)
- [End-to-End Demo Workflow](./docs/demo-workflow.md)
