# ORBIT Data Provenance & Cryptographic Lineage

## 1. Overview & Core Invariants

ORBIT enforces strict, verifiable cryptographic data provenance across every stage of geospatial data analysis, temporal change detection, predictive modeling, and grounded AI intelligence synthesis.

Every intermediate and final artifact in the ORBIT pipeline carries an immutable SHA-256 digital fingerprint and machine-readable execution metadata that guarantees:
- **Zero Fabrication**: No Earth Observation measurement or telemetry point can be generated without traceable sensor origins.
- **Reproducibility**: Identical raw inputs and algorithm parameters yield identical deterministic transformations.
- **Traceability**: Every AI-synthesized claim links directly to parent evidence nodes in the Evidence Graph.
- **Auditability**: Evidence packages and final intelligence dossiers can be verified independently via SHA-256 cryptographic digests.

---

## 2. Cryptographic Digest Calculation

### Evidence Package Digest
The `EvidenceRetriever` generates a deterministic SHA-256 hash across all constituent evidence items, their epistemic classifications, values, source identifiers, and directional graph relationships:

```json
{
  "aoi_id": "aoi-sinop-deforestation",
  "aoi_name": "Sinop Municipality, Mato Grosso",
  "analysis_run_id": "99b26991-4ca8-416a-9677-0759677363f6",
  "items": [
    {
      "id": "ev-item-001",
      "type": "OBSERVATION",
      "epistemic_level": "OBSERVED",
      "source_id": "S2B_MSIL2A_20230615T140051",
      "value": 0.78,
      "unit": "surface_reflectance",
      "timestamp": "2023-06-15T14:00:51Z"
    }
  ],
  "relationships": [
    {
      "source_id": "ev-item-001",
      "target_id": "ev-item-002",
      "type": "SUPPORTS"
    }
  ]
}
```

$$\text{package\_hash\_sha256} = \text{SHA256}(\text{CanonicalJSON}(\text{digest\_payload}))$$

---

## 3. Provenance Chain Through the 8-Stage Pipeline

```
[ STAGE 1: RAW TELEMETRY ] (OBSERVED)
  │  Source: Sentinel-2 / Landsat-8 STAC Asset ID & Checksum
  ▼
[ STAGE 2: SPECTRAL INDEX TRANSFORM ] (CALCULATED)
  │  SHA-256 of band inputs + formula ("(B08-B04)/(B08+B04)") + window bounds
  ▼
[ STAGE 3: TEMPORAL COMPARATOR ] (CALCULATED)
  │  Timestamp ordering check (T1 < T2) + delta calculation
  ▼
[ STAGE 4: DETERMINISTIC RULE INFERENCE ] (CALCULATED / DETECTED)
  │  Rule version tag + spatial buffer calculation + contradiction check
  ▼
[ STAGE 5: TIME-SERIES FORECASTING ] (PREDICTED)
  │  Historical backtest metrics (RMSE, MAE, R²) + prediction bounds
  ▼
[ STAGE 6: EVIDENCE PACKAGE ASSEMBLY ] (EVIDENCE GRAPH)
  │  Consolidated package SHA-256 digest calculated
  ▼
[ STAGE 7: GROUNDED AI REASONING ] (AI_INTERPRETED)
  │  Strict citation verification + anti-upgrade enforcement
  ▼
[ STAGE 8: SIGNED DOSSIER GENERATION ] (FINAL REPORT)
  └─ Embeds evidence package SHA-256 hash + author attribution + timestamp
```

---

## 4. Test Fixture Provenance Rules

When operating in simulated or offline demonstration environments:
1. All generated data MUST be explicitly tagged with `[TEST FIXTURE - SIMULATED]` in the `aoi_name` or scene metadata.
2. The `is_test_fixture: true` boolean attribute must be present in telemetry headers.
3. Real satellite scene IDs (`S2A_*`, `LC08_*`) must NEVER be forged or assigned synthetic values.
