# ORBIT End-to-End Demonstration Workflow
## Case Study: Multi-Decadal Deforestation & Infrastructure Expansion (Sinop, Mato Grosso)

This guide walks through the end-to-end intelligence cycle executed by ORBIT across all 8 pipeline stages.

---

## 1. Pipeline Stages Overview

```
1. Discovery & Ingestion  ──► 2. Spectral Indices  ──► 3. Temporal Comparison  ──► 4. Rule Inference
                                                                                         │
8. Dossier Generation    ◄── 7. Grounded AI       ◄── 6. Evidence Packaging   ◄── 5. Forecasting
```

---

## 2. Step-by-Step Execution

### Step 1: Area of Interest & Scene Discovery
1. Search the gazetteer for **"Sinop, Brazil"** (Coordinates: `-11.864`, `-55.505`).
2. Discover Sentinel-2 Level-2A imagery for two temporal baseline epochs:
   - **Epoch 1 (Baseline)**: June 2021 (Intact dense tropical canopy)
   - **Epoch 2 (Current)**: June 2024 (Land clearing / built-up expansion)

### Step 2: Calibrated Spectral Processing
1. Compute **Normalized Difference Vegetation Index (NDVI)**:
   $$\text{NDVI} = \frac{\text{NIR} - \text{RED}}{\text{NIR} + \text{RED}}$$
   - T1 Mean NDVI: **0.714** (Healthy closed canopy)
   - T2 Mean NDVI: **0.167** (Bare earth / clearcut clearing)
2. Compute **Normalized Difference Built-up Index (NDBI)** to detect constructed structures and roads.

### Step 3: Multi-Temporal Change Detection
1. Calculate spatial difference mask ($\Delta\text{NDVI} = -0.5476$).
2. Classify pixel loss categories using Otsu dynamic thresholding:
   - Significant vegetation loss: **6.85 km²**
   - Spatial change cluster detection via PostGIS `ST_ClusterDBSCAN`.

### Step 4: Deterministic Geospatial Rule Evaluation
1. Spatial correlator computes road proximity (85m from primary unpaved logging corridor).
2. Rule engine evaluates `RULE_MULTI_URBAN_EXPANSION_v1`:
   - Confirms multi-indicator signal ($\Delta\text{NDVI} \le -0.10$ and $\Delta\text{NDBI} \ge 0.08$).
   - Creates root intelligence event object with `CALCULATED` epistemic classification.

### Step 5: Predictive Modeling & Time-Series Forecasting
1. Extract annual median historical observations (2018–2024).
2. Project canopy trend forward to **2026–2030** with 95% confidence intervals.
3. Compute out-of-sample backtesting metrics ($R^2 = 0.94$, $\text{RMSE} = 0.028$).

### Step 6: Immutable Evidence Graph Packaging
1. Assemble all raw observations, calculated indices, and forecast models into an `EvidencePackage`.
2. Compute SHA-256 digital fingerprint across all nodes and edges.

### Step 7: Grounded AI Intelligence Synthesis
1. The `GroundedReasoner` produces structured executive findings, claim-by-claim citations, and policy recommendations.
2. Every claim links to verifiable evidence IDs. Epistemic level is strictly tagged as `AI_INTERPRETED`.

### Step 8: Signed Cryptographic Intelligence Dossier
1. The `ReportGenerator` compiles a publication-ready Markdown and PDF report embedding the SHA-256 evidence package digest.
2. Ready for distribution to analysts, monitoring agencies, or decision makers.
