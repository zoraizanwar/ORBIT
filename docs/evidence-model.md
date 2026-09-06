# ORBIT: Evidence & Provenance Model

## 1. ORBIT Evidence Strength Framework

In ORBIT, **Evidence Strength** is a first-class, deterministic metric assessing the physical, sensory, and procedural grounding of an analytical finding. It is strictly distinguished from probabilistic model confidence or generative AI certainty.

```
+-----------------------------------------------------------------------------------+
|                        ORBIT EVIDENCE STRENGTH EVALUATION                         |
+-----------------------------------------------------------------------------------+
| Inputs:                                                                           |
| 1. Source Quality Index ($S_q \in [0, 1]$): Radiometric Tier-1 / Level-2A rating  |
| 2. Spatial Resolution Factor ($R_s \in [0, 1]$): Pixel size vs. Target feature     |
| 3. Temporal Coverage ($T_c \in [0, 1]$): Anniversary window proximity (< 15 days) |
| 4. Obstruction Score ($O_b \in [0, 1]$): Cloud/shadow proximity & SCL reliability |
| 5. Algorithm Tier Score ($A_t \in [0, 1]$): Level 1 (0.95) to Level 4 (0.85)     |
| 6. Multi-Source Agreement ($M_a \in [0, 1]$): Cross-sensor (Optical + SAR) check  |
+-----------------------------------------------------------------------------------+
                                         | Computed Deterministic Composite Score
                                         v
+-----------------------------------------------------------------------------------+
| Evidence Strength Index ($ESI$):                                                  |
| ESI = 0.25 S_q + 0.20 R_s + 0.15 T_c + 0.20 O_b + 0.10 A_t + 0.10 M_a            |
+-----------------------------------------------------------------------------------+
```

### Evidence Strength Classification Tiers:

| Classification | Score Range | Definition & Criteria | Downstream Impact |
|---|---|---|---|
| **`STRONG`** | $ESI \ge 0.85$ | High-resolution telemetry ($10\text{m}$), cloud cover $< 5\%$, tight anniversary window, multi-sensor/SAR cross-validation. | Authoritative; suitable for formal intelligence briefings and legal/compliance dossiers. |
| **`MODERATE`** | $0.65 \le ESI < 0.85$ | Standard resolution ($20\text{m}-30\text{m}$), cloud cover $5\%-15\%$, single-sensor telemetry, baseline statistical change detection. | Reliable; standard analytical confidence with documented atmospheric noise bounds. |
| **`LIMITED`** | $0.40 \le ESI < 0.65$ | Coarse resolution ($> 30\text{m}$), cloud proximity ($15\%-30\%$), temporal gap $> 60\text{ days}$, or historical archive data (Landsat 4-5). | Indicative only; requires explicit limitation disclaimers in UI, charts, and reports. |
| **`INSUFFICIENT`** | $ESI < 0.40$ | Heavy cloud cover ($> 30\%$), sensor data missing/corrupted, or feature size below sensor resolving limit. | Masked; analytical engine returns `INSUFFICIENT_EVIDENCE`. Zero output fabrication. |

---

## 2. Distinguishing Evidence Strength from Other Metrics

ORBIT enforces strict conceptual clarity across four distinct uncertainty metrics:

```
+----------------------------------------------------------------------------------------------------+
| 1. EVIDENCE STRENGTH (Deterministic Data/Sensor/Lineage Pedigree)                                   |
|    - Measures: "Is the underlying empirical data sufficiently high-quality and uncorrupted?"       |
|    - Scale: Categorical (`STRONG`, `MODERATE`, `LIMITED`, `INSUFFICIENT`) based on ESI calculation. |
+----------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------+
| 2. MEASUREMENT UNCERTAINTY (Physical Error Bounds)                                                  |
|    - Measures: "What is the physical plus/minus tolerance of the spatial measurement?"             |
|    - Scale: Scalar $\pm \delta$ (e.g., $14.23 \pm 0.45\text{ km}^2$ based on raster pixel GSD).     |
+----------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------+
| 3. MODEL CONFIDENCE (Statistical Classification Probability)                                       |
|    - Measures: "How confident is the machine learning / segmentation model in this class label?"   |
|    - Scale: Float $[0.0, 1.0]$ (e.g., Random Forest class probability $p = 0.92$).                |
+----------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------+
| 4. AI INTERPRETATION CONFIDENCE (Generative Synthesis Certainty)                                   |
|    - Measures: "How well do the verified facts constrain the generated narrative explanation?"     |
|    - Scale: Injected qualitative constraint based strictly on Evidence Strength Levels.            |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Cryptographic Evidence Record & Lineage DAG

Every finding links to an immutable Lineage Directed Acyclic Graph (DAG) persisted in PostgreSQL:

```json
{
  "evidence_id": "ev-9a8b7c6d-5e4f-3a2b-1c0d-e9f8a7b6c5d4",
  "analysis_run_id": "ar-11223344-5566-7788-99aa-bbccddeeff00",
  "claim_identifier": "CLAIM_URBAN_EXPANSION_MAGNITUDE",
  "epistemic_level": "CALCULATED",
  "evidence_strength": "STRONG",
  "evidence_strength_score": 0.89,
  "measurement_uncertainty": {
    "nominal_value_km2": 4.12,
    "margin_error_km2": 0.18,
    "confidence_interval_percent": 95.0
  },
  "source_telemetry": {
    "provider": "Copernicus CDSE",
    "dataset": "Sentinel-2 MSI Level-2A",
    "scene_identifier": "S2A_MSIL2A_20230715T140051_N0509_R067_T21LYJ",
    "sha256_checksum": "8a3f81e...912a",
    "sun_elevation_deg": 62.4,
    "cloud_cover_percent": 0.8
  },
  "processing_provenance": {
    "software_version": "ORBIT-Engine-v1.0.0",
    "git_commit": "4f8a29b",
    "algorithm_tier": "LEVEL_2_STATISTICAL",
    "algorithm_name": "Adaptive_Otsu_dNDBI"
  }
}
```
