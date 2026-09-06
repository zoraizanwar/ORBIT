# ORBIT Multi-Source Earth Observation Fusion & Advanced Change Analysis

## 1. Overview & Multi-Sensor Fusion Architecture

ORBIT Phase 17 introduces the Multi-Source Earth Observation Fusion & Advanced Change Analysis layer, advancing the platform from pairwise T1/T2 comparisons to multi-epoch, multi-modal evidence synthesis.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MULTI-SOURCE OBSERVATION REGISTRY                      │
│   [Sentinel-2 Optical (MSI)]   [Sentinel-1 SAR (C-Band)]   [OSM Vectors]    │
├─────────────────────────────────────────────────────────────────────────────┤
│                       MULTI-SENSOR ALIGNMENT ENGINE                         │
│  - Spatial IoU Overlap (%)           - Configurable Temporal Windows (±14d) │
│  - CRS Normalization (EPSG:4326)     - GSD Resolution Matching & Resampling │
├─────────────────────────────────────────────────────────────────────────────┤
│                    MULTI-TEMPORAL CHANGE SERIES ANALYZER                    │
│                     (T1 -> T2 -> T3 -> ... -> Tn Trajectories)              │
│  - Absolute & Relative Deltas        - Trajectory Persistence Analysis      │
│  - Recovery Rebound Detection        - Multi-Epoch Directional Oscillation  │
├─────────────────────────────────────────────────────────────────────────────┤
│                  CROSS-SENSOR CONTRADICTION & CORROBORATION                 │
│  - Optical Veg Loss vs SAR Roughness - Optical Water vs SAR Specular Refl.  │
│  - NDBI Built-Up vs Road Proximity   - Epistemic Contradiction Disclosure   │
├─────────────────────────────────────────────────────────────────────────────┤
│                     DETERMINISTIC EVIDENCE FUSION SCORER                    │
│   Score = f(Quality, Observation Count, Cadence, Overlap, Corroboration)    │
│                        SHA-256 Provenance Digital Seal                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Multi-Source Alignment Protocols

The `ObservationAlignmentService` evaluates compatibility across four strict dimensions without silently modifying data:
1. **Spatial Alignment**: Computes bounding box Intersection over Union (IoU). Threshold $\ge 10\%$ required for partial alignment; $\ge 80\%$ for full alignment.
2. **Temporal Proximity**: Configurable windows ($\pm 3, \pm 7, \pm 14, \pm 30$ days). Mismatches beyond threshold are flagged as `INCOMPATIBLE`.
3. **CRS Compatibility**: Canonical EPSG:4326 geometry validation.
4. **GSD Resolution**:
   - $\text{ratio} \le 1.05$: Identical resolution (no resampling required).
   - $1.05 < \text{ratio} \le 4.0$: Compatible resolution (bilinear area-weighted resampling applied and explicitly logged in provenance).
   - $\text{ratio} > 4.0$: Incompatible resolution mismatch.

## 3. Multi-Temporal Change Series & Persistence

The `MultiTemporalChangeAnalyzer` evaluates sequential epochs $T_1 \to T_2 \to \dots \to T_n$:
- **States**:
  - `NO_CHANGE`: $|\Delta| < 0.05$ across all steps.
  - `DECREASING`: Consistent downward trajectory.
  - `INCREASING`: Consistent upward trajectory.
  - `PERSISTENT_CHANGE`: Downward/upward steps persisting across $\ge 2$ consecutive intervals.
  - `RECOVERY`: Significant decline followed by $\ge 50\%$ rebound toward baseline.
  - `OSCILLATING`: $\ge 2$ directional reversals across sequential epochs.
  - `INSUFFICIENT_DATA`: $< 2$ valid observations.
- Versioned metadata: Rule `RULE-MULTI-TEMPORAL-SERIES-001`, Threshold `v1.0`, Algorithm `ORBIT-MultiTemporal-v1.0.0`.

## 4. Cross-Sensor Contradiction & Corroboration Engine

The `CrossSensorContradictionEngine` cross-references physical signals across modalities:
- **Corroborated**:
  - Optical canopy decline ($\Delta\text{NDVI} \le -0.25$) + SAR structural backscatter loss ($\Delta\text{VV} \le -2.0\text{ dB}$).
  - Built-up index expansion ($\Delta\text{NDBI} \ge +0.20$) + Road corridor proximity ($\le 1.5\text{ km}$).
- **Contradicted**:
  - Optical canopy decline ($\Delta\text{NDVI} \le -0.25$) + SAR structural stability ($|\Delta\text{VV}| < 0.5\text{ dB}$).
  - Optical water loss ($\Delta\text{NDWI} \le -0.30$) + SAR persistent smooth water reflection ($\text{VV} < -18.0\text{ dB}$).
  - Optical built-up signal ($\Delta\text{NDBI} \ge +0.20$) without road infrastructure ($> 5.0\text{ km}$).
- **Invariant**: Contradictory evidence is never erased or averaged into fake consensus.

## 5. Deterministic Evidence Strength Scoring

`EvidenceFusionScorer` computes a composite score $\in [0.0, 1.0]$:
$$\text{Score} = \text{clamp}(0.25 \cdot Q + 0.25 \cdot N + 0.20 \cdot T + 0.15 \cdot S + K_{\text{bonus}} - P_{\text{penalty}}, 0.0, 1.0)$$
- $Q$: Observation quality (valid pixels, low cloud cover).
- $N$: Independent epoch count ($\min(1.0, N / 4.0)$).
- $T$: Temporal regularity.
- $S$: Spatial overlap IoU.
- $K_{\text{bonus}}$: $+0.15$ for cross-sensor corroboration.
- $P_{\text{penalty}}$: $-0.30$ per contradiction finding.

## 6. Database Migration: `0010_multi_source_fusion.py`

Additive migration attached to `0009_operational_workstation`:
- `eo.observation_alignments`: Pairwise alignment reports, temporal offsets, GSD ratios, resampling metadata.
- `eo.fusion_results`: End-to-end multi-source fusion runs, evidence scores, and SHA-256 digests.
- `eo.temporal_change_series`: Multi-epoch metric trajectories and persistence statistics.

## 7. Epistemic Invariants & Data Integrity

- `OBSERVED`: Raw sensor acquisitions (Sentinel-1 SAR, Sentinel-2 Optical, OSM vectors).
- `CALCULATED`: Multi-temporal trajectories, alignments, and difference metrics.
- `DETECTED`: Rule-based corroboration / contradiction classifications and persistent change events.
- `PREDICTED`: Statistical forecasts only (strictly separated from historical calculations).
- `AI_INTERPRETED`: Explanations strictly referencing explicit evidence IDs.
