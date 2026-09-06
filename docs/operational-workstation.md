# ORBIT Operational Geospatial Workstation & Live Earth Observation Exploration

## 1. Overview & Operational Workstation Architecture

ORBIT Phase 16 delivers the Operational Geospatial Workstation layer, turning ORBIT from a set of modular backend analytical engines into a cohesive, interactive, local-first intelligence application.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       OPERATIONAL MAP WORKSPACE                             │
│       (MapLibre WebGL Engine: Vector Roads, AOI, Scene Overlays)           │
├──────────────────────────────┬──────────────────────────────────────────────┤
│      SCENE EXPLORER          │         T1/T2 PAIR SELECTOR                  │
│  - Real STAC Scene Queries   │  - Baseline vs Comparison Alignment          │
│  - Deterministic Ranking     │  - Strict Chronological Invariant (T1 < T2)  │
│  - Cloud & Resolution Filter │  - Band Mapping & Separation Interval        │
├──────────────────────────────┴──────────────────────────────────────────────┤
│                   8-TIER ANALYTICAL EXECUTION LIFECYCLE                     │
│  [1. Validation] -> [2. Spectral] -> [3. Change] -> [4. Rules Engine]       │
│  -> [5. TS Guard] -> [6. Evidence Graph] -> [7. AI] -> [8. Signed Dossier]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                         OPERATIONAL RESULTS PANEL                           │
│  - Epistemic Badges (OBSERVED, CALCULATED, DETECTED, PREDICTED, AI)         │
│  - Deforestation Perimeter & Biomass Delta                                  │
│  - Grounded AI Narrative with Claim-Level Citations                         │
│  - SHA-256 Provenance & Digital Sealing Verification                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Interactive Workstation Components

### A. Operational Map Workspace (`OperationalMapWorkspace.tsx`)
- High-performance MapLibre GL instance.
- Visual layers:
  1. Area of Interest boundary (cyan polygon outline).
  2. Earth Observation scene footprints (emerald coverage bounds).
  3. Change detection spatial difference masks (amber clusters).
  4. Vector road and transport infrastructure corridors (rose linear networks).
- Dynamic layer visibility toggle panel with persistent state.

### B. Live STAC Scene Explorer (`SceneExplorer.tsx`)
- Queries live STAC catalogs (Element84 / AWS Earth Search, Copernicus CDSE).
- Multi-dimensional filters: date intervals, cloud cover slider, sensing modality (Optical MSI vs SAR C-Band).
- Evaluates candidate scenes via `DeterministicSceneRanker` (temporal decay, cloud penalty, spatial IoU, GSD resolution).
- Displays explicit data origin badges: `REAL DATA` vs `[TEST FIXTURE - SIMULATED]`.

### C. Observation Pair Selector (`ObservationPairSelector.tsx`)
- Aligns T1 baseline and T2 comparison scenes.
- Enforces strict chronological validity: $T1 < T2$ (rejects reversed or identical timestamps).
- Displays temporal separation in days and checks required band availability (B04 Red, B08 NIR).

### D. 8-Tier Analytical Lifecycle Panel (`AnalysisExecutionPanel.tsx`)
- Real-time progress tracker across all 8 analytical stages:
  1. `RASTER_VALIDATION`: Header inspection, CRS check, dimension constraints ($\le 16384$).
  2. `SPECTRAL_ANALYSIS`: Sub-pixel NDVI/NDBI calculation on windowed arrays.
  3. `CHANGE_DETECTION`: Multi-temporal difference mask and Otsu thresholding.
  4. `GEOSPATIAL_INTELLIGENCE`: Rule-based correlation and road corridor proximity.
  5. `FORECASTING`: Strict historical observation check (requires $\ge 4$ observations; returns `INSUFFICIENT_DATA` otherwise).
  6. `EVIDENCE_GRAPH`: Canonical JSON serialization and SHA-256 digest hashing.
  7. `GROUNDED_AI`: Synthesis with claim-level evidence citations.
  8. `DOSSIER_GENERATION`: Signed intelligence report with provenance sealing.

### E. Operational Results & Dossier Inspector (`OperationalResultsPanel.tsx`)
- Displays classified canopy loss ($\Delta\text{NDVI} = -0.371$), affected surface area ($6.85\text{ km}^2$), rule inferences, and forecast guard notice.
- Presents grounded AI conclusions where every factual assertion references specific evidence IDs.
- Provides cryptographic SHA-256 verification seals.

## 3. Database Schema Migration: `0009_operational_workstation.py`

The additive migration introduces the `operational` schema:
- `operational.aoi_sessions`: Stores user-defined AOI geometries, bounding boxes, and geodesic areas.
- `operational.scene_selections`: Tracks candidate STAC scene evaluations and ranking provenance.
- `operational.analysis_jobs`: Tracks end-to-end execution lifecycle, statuses, and analytical outputs.

## 4. Epistemic Invariants & Provenance Guarantee

- `OBSERVED`: Raw sensor telemetry (Sentinel-2 MSI Level-2A GeoTIFFs, OSM road networks).
- `CALCULATED`: Mathematical index formulas and difference masks.
- `DETECTED`: Rule-based spatial events.
- `PREDICTED`: Statistical forecasts with confidence intervals.
- `AI_INTERPRETED`: Grounded reasoning only citing real evidence IDs.
- **Strict Boundary**: AI reasoning is never promoted to `OBSERVED` or `CALCULATED`. When empirical data is insufficient for forecasting, the engine returns an explicit guard notice rather than generating artificial data.
