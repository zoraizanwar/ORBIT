# ORBIT: Product Vision & Strategic Specification

## 1. Executive Summary

**ORBIT** (Geospatial Intelligence & Earth Monitoring Platform) is an enterprise-grade, planetary-scale geospatial intelligence workstation. It enables analysts, researchers, institutions, and decision-makers to investigate locations across Earth across multi-decadal time horizons (1972–Present and deep geological/historical synthesis).

ORBIT provides an end-to-end analytical pipeline that transforms public Earth Observation (EO) telemetry, vector road and urban infrastructure registries, environmental sensor arrays, and historical records into **auditable, mathematically reproducible, evidence-grounded intelligence reports**.

---

## 2. Core Philosophy & The Epistemological Ladder

Commercial geospatial intelligence requires an inviolable boundary between empirical telemetry, deterministic spatial computations, statistical inferences, machine learning segmentation, and generative narrative synthesis. ORBIT strictly rejects the conflation of generative AI outputs with authoritative spatial measurements.

The platform operates on the **ORBIT Epistemological Ladder**:

```
[ LEVEL 5: AI NARRATIVE & SYNTHESIS ]
  ↑ Explains, contextualizes, and structures evidence into intelligence briefings strictly grounded in Levels 1–4
[ LEVEL 4: SPATIOTEMPORAL EVENT DETECTION & CLUSTERING ]
  ↑ Spatiotemporal clustering (DBSCAN), event lifecycle tracking, infrastructure correlation
[ LEVEL 3: LAND-COVER, SEGMENTATION & OBJECT-LEVEL ANALYSIS ]
  ↑ Multi-spectral classification, morphological segmentation, object extraction, patch metrics
[ LEVEL 2: STATISTICAL & TEMPORAL CHANGE DETECTION ]
  ↑ Pixel differencing (dNDVI, dNDBI, dMNDWI), baseline Otsu thresholding, CCDC time-series harmonic modeling, SAR coherence
[ LEVEL 1: DETERMINISTIC SPECTRAL INDICES & CALIBRATED DERIVATIVES ]
  ↑ Level-2A Surface Reflectance, SCL/QA_PIXEL cloud masks, calibrated SAR backscatter (σ°), geometric corrections
[ LEVEL 0: RAW SENSOR TELEMETRY & AUTHORITATIVE REGISTRIES ]
  ↑ Copernicus Sentinel-1/2 SAFE archives, USGS Landsat Collection 2 Level-1/2, OpenStreetMap PBF extracts
```

### Inviolable Invariant Rules
1. **Measurement Immutability**: If the analytical engine calculates an affected deforestation area of $14.23\text{ km}^2$, downstream AI systems are strictly forbidden from altering, rounding inconsistently, or inventing a competing metric. The calculated scalar is injected into the AI context as an authoritative, read-only assertion.
2. **Epistemic Classification**: Every data point, attribute, table row, chart node, and UI label must explicitly declare its Epistemic Classification:
   - `OBSERVED`: Raw or calibrated sensor telemetry directly registered from physical sensors.
   - `CALCULATED`: Deterministic mathematical or geometric outputs computed from observed data without statistical optimization (e.g., geodesic surface area, spectral indices).
   - `DETECTED`: Algorithmic spatial/temporal segmentation identifying categorical state transitions (e.g., baseline thresholding, CCDC change mask).
   - `ESTIMATED`: Statistical approximations or probabilistic spatial models (e.g., kriging interpolation, regression estimates).
   - `PREDICTED`: Machine learning or time-series forecast models projecting future states.
   - `AI_INTERPRETATION`: Natural language contextualization and hypothesis generation synthesized by Large Language Models grounded strictly in Levels 0–4.
3. **No Hallucinated Evidence**: When evidence is missing, noisy, cloud-obscured, or sensor-limited, the system must formally assert `INSUFFICIENT_EVIDENCE` and catalog the sensor limitations rather than interpolate fabricated findings.

---

## 3. Product Capability & Detectability Scope

ORBIT does **not** claim to detect every physical change on Earth. The formal product capability is defined as:

> **"ORBIT detects observable geographic changes supported by available spatial resolution, temporal coverage, sensor characteristics, data quality, and analytical methodology."**

### Detectable vs. Undetectable Changes Matrix:

| Category | Detectable Changes (Supported by Telemetry & Methods) | Potentially Undetectable Changes (Physical & Sensor Limitations) |
|---|---|---|
| **Vegetation & Forestry** | Broadscale clear-cutting, wildfire burn scars ($> 0.5\text{ ha}$), canopy loss in optical sensors, major seasonal agricultural cycles. | Selective logging of individual trees under closed canopy, understory thinning without canopy breach, small shrub clearing $< 10\text{m}$. |
| **Water Bodies & Hydrology** | Multi-hectare reservoir shrinkage, major river course shifts, flood inundations ($> 20\text{m}$ width), coastal land reclamation. | Narrow irrigation ditches ($< 5\text{m}$ width), ephemeral puddles, sub-surface water table fluctuations, culverted streams. |
| **Urban & Built-Up** | New industrial subdivisions, highway corridor paving, large building complex construction ($> 400\text{ m}^2$), major quarry expansions. | Interior architectural renovations, single residential room additions, unpaved footpath creation, repaving without spectral change. |
| **Infrastructure & Roads** | Multi-lane highway construction, bridge erection over water, major railway alignment clearing, newly paved arterial roads. | Minor pothole repairs, narrow dirt tracks obscured by forest canopy, underground pipelines with restored surface vegetation. |

---

## 4. Multi-Modal Sensing: Optical vs. SAR Modalities

ORBIT does **not** treat Sentinel-1 SAR as a mere fallback for cloudy Sentinel-2 optical imagery. Optical and Synthetic Aperture Radar (SAR) represent fundamentally distinct sensing physics:

```
                  +----------------------------------------------+
                  |           ANALYTICAL QUESTION                |
                  +----------------------+-----------------------+
                                         |
            +----------------------------+----------------------------+
            |                                                         |
+-----------v--------------------------+    +-------------------------v--------------------------+
|      OPTICAL SUITABILITY CHECK       |    |          SAR SUITABILITY CHECK                     |
| - Multispectral reflectance          |    | - Dielectric properties & moisture                 |
| - Chlorophyll & pigment absorption   |    | - Surface roughness & structural geometry          |
| - Water clarity & shallow bathymetry |    | - All-weather, day/night penetration               |
| - Urban building contrast            |    | - Coherence change detection for structural shifts |
| Target Sensors: Sentinel-2, Landsat  |    | Target Sensor: Sentinel-1 (C-Band SAR GRD / RTC)   |
+--------------------------------------+    +----------------------------------------------------+
```

---

## 5. First-Class Evidence Strength Framework

ORBIT establishes **Evidence Strength** as an independent, deterministic quality metric distinct from machine learning confidence scores, measurement uncertainty, or AI interpretation confidence:

```
ORBIT Evidence Strength = f(Source Quality, Spatial Resolution, Temporal Coverage, Obstruction Level, Algorithm Reliability, Cross-Source Agreement)
```

| Evidence Strength Level | Definition & Criteria | Analytical Status |
|---|---|---|
| **`STRONG`** | High-resolution telemetry ($10\text{m}$), cloud cover $< 5\%$, anniversary date match within 15 days, multi-sensor/SAR cross-validation, verified by Level 3 segmentation. | Authoritative; suitable for formal intelligence briefings and compliance audits. |
| **`MODERATE`** | Standard resolution ($20\text{m} - 30\text{m}$), cloud cover $5\% - 15\%$, single-sensor telemetry, baseline statistical change detection. | Reliable; standard analytical confidence with minor atmospheric noise margins. |
| **`LIMITED`** | Coarse resolution ($> 30\text{m}$), partial cloud/shadow proximity ($15\% - 30\%$), temporal gap $> 60\text{ days}$, or historical archive data (Landsat 4-5). | Indicative only; requires explicit limitation disclaimers in UI and reports. |
| **`INSUFFICIENT`** | Heavy cloud cover ($> 30\%$), sensor data missing/corrupted, or feature size below sensor resolving limit ($< 2 \times \text{pixel size}$). | Formally masked; analytical engine returns `INSUFFICIENT_EVIDENCE`. Zero fabrication. |

---

## 6. Historical Data Capability Model

ORBIT recognizes that Earth Observation telemetry across 1972–Present is heterogeneous. Analytical capabilities vary by historical sensor epoch:

| Epoch | Primary Sensors | Spatial Resolution | Spectral Capabilities | Temporal Cadence | Analytical Capability Profile |
|---|---|---|---|---|---|
| **1972–1981** | Landsat 1–3 MSS | $60\text{m} \times 80\text{m}$ | 4 Broad Optical Bands | 18 days | Coarse macro-scale land/water changes; no fine urban analysis. Results: `LIMITED` or `ESTIMATED`. |
| **1982–1998** | Landsat 4–5 TM | $30\text{m}$ Optical, $120\text{m}$ Thermal | 7 Bands (Visible, NIR, SWIR, TIR) | 16 days | Multi-spectral regional vegetation, water, and major urban footprint analysis. Results: `MODERATE`. |
| **1999–2014** | Landsat 7 ETM+, MODIS | $30\text{m}$ ($15\text{m}$ Pan), $250\text{m}$ | Enhanced thermal, Pan sharpening | 16 days (SLC-off gaps post-2003) | Improved regional change tracking; SLC-off gap interpolation required. Results: `MODERATE`. |
| **2015–Present** | Sentinel-2A/B, Sentinel-1A/C, Landsat 8/9 | $10\text{m} - 20\text{m}$ MSI, $10\text{m}$ SAR | 13 Optical Bands + C-Band SAR Dual Pol | $5\text{ days}$ (S2 constellation) | High-resolution multi-modal change detection, infrastructure tracking. Results: `STRONG`. |

---

## 7. Data Cost, Licensing & Commercial Posture

> **"ORBIT is designed around free, open, and public data sources wherever practical. Each provider and dataset must have its own recorded licensing, attribution, access, redistribution, and commercial-use constraints."**

The platform is engineered as **Local-First** for development and zero-cost baseline operation, while maintaining clean architectural boundaries to support future deployment as an Enterprise Geospatial Intelligence Workstation, Research Platform, or Commercial SaaS.
