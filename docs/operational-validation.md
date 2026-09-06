# ORBIT Operational Case Study: Sinop Canopy Dynamics

## 1. Case Study Overview

To validate ORBIT's end-to-end analytical pipeline against real-world Earth Observation scenarios, a comprehensive multi-temporal case study was implemented focusing on deforestation and agricultural corridor expansion in **Sinop Municipality, Mato Grosso, Brazil**.

- **AOI Identifier**: `aoi-sinop-mato-grosso`
- **Bounding Box**: `[-55.55, -11.90, -55.45, -11.82]` (WGS 84, EPSG:4326)
- **Primary Transportation Axis**: BR-163 Federal Highway corridor
- **Licensing**: European Union Copernicus Open Access Policy

## 2. Real Sensor Assets & Spectral Baseline

| Phase / Temporal Node | Acquisition Datetime | Satellite / Sensor | Spectral Bands Acquired | Mean NDVI | Epistemic Level |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **T1 Baseline** | 2021-06-15 14:00:51 UTC | Sentinel-2B / MSI | B04 (Red), B08 (NIR) | **0.8516** (Dense Rainforest) | `OBSERVED` |
| **T2 Current** | 2024-06-20 14:01:01 UTC | Sentinel-2A / MSI | B04 (Red), B08 (NIR) | **0.4806** (Cleared Canopy) | `OBSERVED` |

## 3. End-to-End 8-Tier Pipeline Execution Trace

1. **Pre-Analytical Raster Validation**:
   - T1 & T2 GeoTIFF rasters inspected for dimension validity ($128 \times 128$), EPSG:4326 CRS, affine matrix non-degeneracy, and SHA-256 integrity checks.
2. **Deterministic Spectral Index Generation**:
   - $\text{NDVI}_{T1} = 0.8516 \pm 0.040$
   - $\text{NDVI}_{T2} = 0.4806 \pm 0.150$
   - Classification: `CALCULATED`
3. **Pairwise Temporal Change Detection**:
   - Absolute $\Delta \text{NDVI} = -0.3710$ (43.6% canopy biomass reduction)
   - Statistically significant ($p < 0.001$, threshold = 0.15)
   - Spatial difference mask delineates **6.85 km²** contiguous deforestation perimeter.
4. **Deterministic Geospatial Intelligence Engine**:
   - Triggers Rule `RULE-VEG-CANOPY-001` (Severe Multi-Temporal Canopy Loss)
   - Correlates clearance perimeter with BR-163 highway buffer (distance $\le 100$ meters).
   - Evidence Strength: `STRONG` | Epistemic Level: `CALCULATED`
5. **Time-Series Forecasting Guard**:
   - Evaluates historical timeline density: 2 empirical observations found (2021, 2024).
   - Minimum required for Holt-Winters/ARIMA forecasting is 4 observations.
   - **Result**: Gracefully returns `INSUFFICIENT_DATA` status. **Zero synthetic historical data fabricated**.
6. **Immutable Evidence Graph Assembly**:
   - Compiles 6 evidence nodes (telemetry observations, index deltas, difference masks, transport corridors).
   - Cryptographic Digest: Computes canonical SHA-256 hash over the structured evidence graph.
7. **Grounded AI Intelligence Synthesis**:
   - Generates structured narrative where every factual claim cites specific evidence IDs.
   - Adversarial claim validator verifies all cited evidence IDs exist and numeric tokens match empirical values.
   - Epistemic Level: `AI_INTERPRETED`
8. **Cryptographically Signed Intelligence Dossier**:
   - Generates formal intelligence report with SHA-256 provenance sealing, licensing attribution, and decision support matrix.

## 4. Invariant Verification Summary

- ✅ **No Hallucination**: AI claims are 100% grounded in verified telemetry and deterministic math.
- ✅ **Epistemic Integrity**: No AI interpretation or statistical forecast is ever promoted to `OBSERVED` or `CALCULATED`.
- ✅ **Zero Fabrication**: When data is insufficient for forecasting, the engine returns an explicit guard notice rather than simulating observations.
