# ORBIT Phase 12 — Forecasting & Future Prediction System

## 1. Executive Summary & Epistemic Separation

ORBIT (Geospatial Intelligence & Earth Monitoring Platform) Phase 12 establishes a scientifically disciplined, deterministic forecasting foundation. The engine extrapolates multi-temporal Earth observation measurements into future projection horizons (up to 2050) with analytical uncertainty intervals, out-of-sample backtesting diagnostics, and cryptographic provenance tracing.

```
+-----------------------------------------------------------------------------+
|                           ORBIT Epistemic Hierarchy                         |
+-----------------------------------------------------------------------------+
| Level 1: OBSERVED           | Raw sensor telemetry, Sentinel/Landsat scenes |
| Level 2: CALCULATED         | Spectral indices (NDVI, NDWI, NDBI), aggregates|
| Level 3: DETECTED           | Discrete change events, corridor clearings    |
| Level 4: HISTORICAL         | Multi-decadal empirical summaries (1984-2024) |
| Level 5: PREDICTED          | Scenario-bounded future models (2027-2050)    |
+-----------------------------------------------------------------------------+
```

### Core Invariants:
1. **Strict Epistemic Separation**: All future projection values are strictly classified as `epistemic_level = PREDICTED`. Under no circumstances are future predictions stored, displayed, or mixed with historical observations (`OBSERVED` or `CALCULATED`).
2. **Zero-Fabrication Policy**: If an Area of Interest (AOI) has fewer than the required calibrated historical observations ($\min = 4$ observations spanning $\ge 2.0$ years), the engine returns an explicit `INSUFFICIENT_DATA` status. No synthetic or guessed values are ever generated.
3. **No-AI Phase Boundary**: Phase 12 implements pure statistical trend models and temporal holdout validation. It does NOT invoke large language models (LLMs) or generative AI for numerical forecasting.

---

## 2. End-to-End Forecasting Pipeline

```
Raw Measurements (Phase 9/10/11)
  │
  ▼
Quality Filtering Pipeline (Filter NaN, Inf, timestamp duplicates, cloud cover >30%, prevent PREDICTED leakage)
  │
  ▼
Temporal Aggregator (Annual / Quarterly / Monthly with Median / Mean)
  │
  ▼
Feature Engineering Layer (Normalized time coordinates t_i, rolling statistics, temporal span check)
  │
  ▼
Baseline Regression Model (Ordinary / Robust Linear Trend Fitting: y = β₀ + β₁·t)
  │
  ▼
Prediction Interval Calculation (Analytical Standard Error of Prediction: 95% Confidence Bounds)
  │
  ▼
Expanding-Window Temporal Backtesting (Out-of-sample holdout validation: MAE, RMSE, R²)
  │
  ▼
Cryptographic Provenance Fingerprinting (SHA-256 digest of input IDs, parameters, and model versions)
  │
  ▼
Persistence & API Response (Link to analysis.runs and history_deep.future_predictions)
```

---

## 3. Mathematical Formulation & Uncertainty

### 3.1 Linear Trend Model (`ORBIT-LT-v1`)
For historical observations $(t_1, y_1), (t_2, y_2), \dots, (t_n, y_n)$ where $t_i = \text{year}_i - \text{year}_0$:

$$\bar{t} = \frac{1}{n}\sum_{i=1}^{n} t_i, \quad \bar{y} = \frac{1}{n}\sum_{i=1}^{n} y_i$$

$$\beta_1 = \frac{\sum_{i=1}^{n} (t_i - \bar{t})(y_i - \bar{y})}{\sum_{i=1}^{n} (t_i - \bar{t})^2}, \quad \beta_0 = \bar{y} - \beta_1 \bar{t}$$

Point forecast for target year $t_0$:
$$\hat{y}(t_0) = \beta_0 + \beta_1 t_0$$

### 3.2 Analytical Prediction Intervals ($95\%$ Confidence)
The residual standard error is computed as:
$$s_e = \sqrt{\frac{\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}{n - 2}}$$

The standard error of prediction for future coordinate $t_0$:
$$\text{SE}_{\text{pred}}(t_0) = s_e \sqrt{1 + \frac{1}{n} + \frac{(t_0 - \bar{t})^2}{\sum_{i=1}^{n} (t_i - \bar{t})^2}}$$

Prediction bounds:
$$\text{Lower} = \hat{y}(t_0) - t_{\text{crit}} \cdot \text{SE}_{\text{pred}}(t_0), \quad \text{Upper} = \hat{y}(t_0) + t_{\text{crit}} \cdot \text{SE}_{\text{pred}}(t_0)$$

---

## 4. Expanding-Window Out-of-Sample Backtesting

To communicate predictive validity honestly without data snooping or future leakage:
1. For minimum training window $k \in [3, n-1]$:
   - Fit model on $t_0 \dots t_{k-1}$
   - Predict out-of-sample holdout $t_k$
   - Record actual $y_k$, predicted $\hat{y}_k$, error $e_k = y_k - \hat{y}_k$
2. Compute aggregate diagnostics:
   - **Mean Absolute Error (MAE)**: $\frac{1}{K}\sum |e_k|$
   - **Root Mean Squared Error (RMSE)**: $\sqrt{\frac{1}{K}\sum e_k^2}$
   - **Coefficient of Determination ($R^2$)**: $1 - \frac{\sum e_k^2}{\sum (y_k - \bar{y})^2}$

---

## 5. Scenario Support & Assumptions

| Scenario Type | Identifier | Meaning / Description |
| :--- | :--- | :--- |
| **Baseline Trend** | `BASELINE_TREND` | Unaltered continuation of historical deforestation, urban expansion, and climatic trends. |
| **Conservation Policy** | `CONSERVATION_POLICY` | Model assumption incorporating protected buffer enforcement and riparian canopy restoration (+0.02 index bonus). |
| **Middle of Road** | `SSP2-4.5_BUSINESS_AS_USUAL` | Standardized socioeconomic pathway assumption identifier. |
| **User Defined** | `USER_DEFINED` | Custom analyst parameter overrides. |

---

## 6. Database Schema & Migration 0007

### Additive Migration (`0007_forecasting_foundation.py`):
Enhances `history_deep.future_predictions` with:
- `analysis_run_id`: UUID (Foreign Key to `analysis.runs.id` on delete `SET NULL`)
- `metric`: VARCHAR(100) default `'NDVI'` (indexes continuous metrics like `NDVI`, `NDWI`, `NDBI`, `SAVI`, `BUILT_UP_AREA`)
- `provenance`: JSONB default `'{}'` (cryptographic trace and calculation fingerprint)
- Indexes: `idx_predictions_analysis_run`, `idx_predictions_metric`

---

## 7. REST API Endpoints

- `POST /api/v1/forecast/prepare`: Quality filtering and temporal aggregation.
- `POST /api/v1/forecast/run`: Executes statistical model fitting, future horizon projection, backtesting, and persistence.
- `POST /api/v1/forecast/backtest`: Evaluates out-of-sample temporal holdout metrics.
- `GET /api/v1/forecast/series`: Queries predictions filtered by AOI, metric, and target year range.
- `GET /api/v1/forecast/{prediction_id}`: Retrieves single prediction object.
- `GET /api/v1/forecast/{prediction_id}/provenance`: Retrieves cryptographic provenance digest.

---

## 8. Frontend Workstation Shell Integration

- **`ForecastPanel`**: Main workstation panel with tabs for Overview, Historical Series, Model Diagnostics, Future Projections, Scenarios, Backtest, and Provenance.
- **`ForecastChart`**: Visual SVG trajectory separating historical line (`CALCULATED`/`OBSERVED`) from dashed future projections (`PREDICTED`) with shaded $95\%$ confidence envelopes.
- **`PredictionCard`**: Modular prediction display with target year, confidence interval, and scenario tag.
- **`BacktestDiagnosticsCard`**: Displays out-of-sample MAE, RMSE, $R^2$, and individual split errors.
