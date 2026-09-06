# ORBIT Phase 10: Multi-Temporal Change Detection Foundation

## 1. Overview & Architectural Purpose

ORBIT Phase 10 establishes the **multi-temporal change detection foundation**, converting empirical Phase 9 raster measurements into deterministic change intelligence. The operational pipeline functions as follows:

$$\text{Phase 9 Measurements} \longrightarrow \text{Temporal Pairing} \longrightarrow \text{Measurement Comparison} \longrightarrow \text{Change Magnitude} \longrightarrow \text{Change Classification} \longrightarrow \text{Spatial Change Masks} \longrightarrow \text{Change Events}$$

All change calculations are **deterministic**, **reproducible**, **explainable**, and **provenance-tracked**.

---

## 2. Temporal Comparison Engine

### 2.1 Inputs & Pre-Conditions
For any two measurements $M(T_1)$ and $M(T_2)$:
- **Temporal Order**: $T_1$ acquisition timestamp must be strictly earlier than $T_2$ ($T_1 < T_2$).
- **Metric Compatibility**: Must represent the same underlying index or physical metric (e.g. `NDVI`, `NDWI`, `NDBI`, `VEGETATED_AREA`).
- **Unit Compatibility**: Units must match (e.g. `index_value`, `km2`, `percent`).
- **Sensor Compatibility**: Cross-modality comparisons (such as optical multispectral vs SAR radar) are rejected to prevent physically invalid comparisons.
- **Quality Assurance**: Minimum valid pixel percentage ($\ge 70.0\%$) and cloud cover threshold ($\le 25.0\%$).

### 2.2 Mathematical Formulas
1. **Absolute Change ($\Delta$)**:
   $$\Delta = V_{T2} - V_{T1}$$
2. **Relative Change**:
   $$\text{relative\_change} = \frac{V_{T2} - V_{T1}}{|V_{T1}|} \quad (\text{if } |V_{T1}| > 10^{-5}, \text{ else } \text{null})$$
3. **Percentage Change**:
   $$\text{percentage\_change} = \text{relative\_change} \times 100.0$$

---

## 3. Change Classification Hierarchy

Change classifications are evaluated against explicit, versioned, configurable thresholds (never hidden magic numbers):

| Classification | Condition (NDVI Default) | Semantic Meaning |
| :--- | :--- | :--- |
| `SIGNIFICANT_INCREASE` | $\Delta \ge +0.15$ | Major canopy growth / greening episode |
| `INCREASE` | $+0.05 \le \Delta < +0.15$ | Moderate vegetation improvement |
| `NO_CHANGE` | $-0.05 < \Delta < +0.05$ | Stable baseline / within sensor noise |
| `DECREASE` | $-0.15 < \Delta \le -0.05$ | Moderate canopy thinning / stress |
| `SIGNIFICANT_DECREASE` | $\Delta \le -0.15$ | Severe clear-cut / deforestation / loss event |
| `INSUFFICIENT_DATA` | Cloud $> 25\%$ or Valid Pixels $< 70\%$ | Telemetry contaminated / unreliable |
| `INVALID` | Incompatible units or sensors | Calculation physically inadmissible |

---

## 4. Spatial Raster Difference & Change Masks

For compatible raster pairs $R_{T1}$ and $R_{T2}$:
1. **Pixel Difference Array**:
   $$\Delta_{\text{raster}}(x, y) = R_{T2}(x, y) - R_{T1}(x, y)$$
2. **Nodata Propagation**: Pixels with nodata in either $T_1$ or $T_2$ are preserved as nodata (never classified as `NO_CHANGE`).
3. **Geodesic Surface Statistics**:
   - For Projected CRS (`EPSG:32621`), $\text{Area} = |res_x \times res_y| \times \text{pixel\_count}$.
   - For Geographic CRS (`EPSG:4326`), pixel area scales by ellipsoidal cosine latitude: $\text{Area} = |(res_x \times 111320 \times \cos(\text{lat})) \times (res_y \times 110540)| \times \text{pixel\_count}$.

---

## 5. Epistemic Hierarchy & Future Prediction Boundary

ORBIT enforces strict epistemic quarantine:
- **`OBSERVED`**: Raw sensor asset reflectance and radar amplitude.
- **`CALCULATED`**: Deterministic band indices (NDVI), pairwise $\Delta$, and spatial difference masks.
- **`DETECTED`**: Discrete rule-based change events (`intelligence.detected_changes`).
- **`PREDICTED`**: Future forecasting scenario projections (2027–2050).

> [!IMPORTANT]
> Change detection results are **CALCULATED**, never raw `OBSERVED`.
> Historical change events cannot be merged with future prediction models. Future predictions consume historical measurements and change features as training baselines while remaining quarantined under `PREDICTED`.

---

## 6. REST API Endpoints

All multi-temporal change endpoints are under `/api/v1/eo/change/`:

- `POST /api/v1/eo/change/compare`: Pairwise temporal measurement comparison.
- `POST /api/v1/eo/change/mask`: Raster-level spatial difference & change mask extraction.
- `POST /api/v1/eo/change/events`: Store validated change event in `intelligence.detected_changes`.
- `GET /api/v1/eo/change/{change_id}`: Retrieve change event.
- `GET /api/v1/eo/change/{change_id}/provenance`: Retrieve complete calculation trace.

---

## 7. Database Migration

- Alembic migration `backend/alembic/versions/0005_change_detection_foundation.py` establishes multi-temporal indexing (`idx_changes_before_date`, `idx_changes_after_date`, `idx_changes_confidence`) on `intelligence.detected_changes`.
