# ORBIT Phase 9: Local-First Raster Processing & Spectral Intelligence Foundation

## 1. Overview & Architectural Purpose

ORBIT Phase 9 implements the **local-first raster processing and spectral intelligence foundation**. The system progresses along the authoritative Earth Observation intelligence pipeline:

$$\text{STAC Discovery} \longrightarrow \text{Scene Registration} \longrightarrow \text{Asset Resolution} \longrightarrow \text{Windowed Band Reading} \longrightarrow \text{Spectral Math} \longrightarrow \text{Deterministic Statistics} \longrightarrow \text{Time-Series Intelligence}$$

ORBIT performs all raster operations locally using standard open-source scientific libraries (`rasterio`, `GDAL`, `numpy`, `pyproj`, `shapely`) without dependency on paid commercial cloud APIs or Google Earth Engine.

---

## 2. Epistemic Classification Invariants

ORBIT enforces strict epistemic classification across all raster and measurement outputs:

| Tier | Classification | Applied To | Description |
| :--- | :--- | :--- | :--- |
| **Level 1** | `OBSERVED` | Raw Sensor Assets / Telemetry | Unprocessed optical reflectance / SAR radar amplitude |
| **Level 2** | `CALCULATED` | Normalized Indices (NDVI, NDWI, NDBI) | Deterministic algebraic band transformations |
| **Level 2** | `CALCULATED` | Rule-Based Stratification | Deterministic threshold canopy / surface cover |
| **Level 3** | `DETECTED` | Multi-Temporal Differential Signals | Statistical change and threshold deviations |
| **Level 4** | `AI_INTERPRETATION`| Synthetic Intelligence Reports | Natural language intelligence summaries |
| **Level 5** | `PREDICTED` | Future Scenario Projections (2027–2050) | Calibrated forecasting models ($\text{Target Year} > \text{Baseline}$) |

> [!IMPORTANT]
> A computed spectral index (e.g., NDVI = 0.62) is **CALCULATED**, never raw `OBSERVED`.
> A rule-based threshold classification is **CALCULATED**, not a direct physical observation.
> Future projections are strictly **PREDICTED** and visually and semantically quarantined from empirical observations.

---

## 3. Windowed Reading & Spatial Windowing

To maintain a low memory footprint and support massive Cloud-Optimized GeoTIFFs (COGs), ORBIT never reads entire multi-gigabyte scenes into memory:

1. **Reprojection**: The user's Area of Interest (AOI) polygon (stored in `EPSG:4326`) is reprojected to the raster's native coordinate reference system (e.g., UTM Zone 21S `EPSG:32621`) using `pyproj.Transformer`.
2. **Intersection Check**: The reprojected AOI is verified against the raster bounding box in native coordinates. If no intersection exists, a `RasterOutOfBoundsError` is thrown.
3. **Window Clamping**: A pixel window (`rasterio.windows.Window`) is computed from bounds and clamped to $[0, \text{width}]$ and $[0, \text{height}]$ with a configurable safety buffer.
4. **Targeted Read**: Only the pixel rectangle corresponding to the AOI is transferred and loaded into a 2D `numpy.ndarray`.

---

## 4. Deterministic Spectral Index Formulas

All spectral indices are calculated with strict divide-by-zero protection, invalid/infinity masking, and nodata value propagation:

### 4.1 Normalized Difference Vegetation Index (NDVI)
$$\text{NDVI} = \frac{\text{NIR} - \text{RED}}{\text{NIR} + \text{RED}} \quad [-1.0, 1.0]$$
- **Sensor Mapping**: Sentinel-2 (B08, B04), Landsat 8/9 (SR_B5, SR_B4).
- **Stratified Canopy Cover**:
  - **Dense Canopy**: $\text{NDVI} \ge 0.60$
  - **Moderate Canopy**: $0.40 \le \text{NDVI} < 0.60$
  - **Low / Sparse Vegetation**: $0.20 \le \text{NDVI} < 0.40$
  - **Non-Vegetated / Bare Soil**: $\text{NDVI} < 0.20$

### 4.2 Normalized Difference Water Index (NDWI)
$$\text{NDWI}_{\text{McFeeters}} = \frac{\text{GREEN} - \text{NIR}}{\text{GREEN} + \text{NIR}} \quad [-1.0, 1.0]$$
- **Sensor Mapping**: Sentinel-2 (B03, B08), Landsat 8/9 (SR_B3, SR_B5).
- **Threshold**: $\text{NDWI} \ge 0.0$ identifies candidate open water bodies.

### 4.3 Normalized Difference Built-Up Index (NDBI)
$$\text{NDBI} = \frac{\text{SWIR}_1 - \text{NIR}}{\text{SWIR}_1 + \text{NIR}} \quad [-1.0, 1.0]$$
- **Sensor Mapping**: Sentinel-2 (B11, B08), Landsat 8/9 (SR_B6, SR_B5).
- **Threshold**: $\text{NDBI} > 0.0$ identifies impervious surfaces, urban structures, and bare dry ground.

### 4.4 Soil-Adjusted Vegetation Index (SAVI)
$$\text{SAVI} = \frac{\text{NIR} - \text{RED}}{\text{NIR} + \text{RED} + L} \times (1 + L) \quad (L = 0.5)$$

---

## 5. Geodesic Surface Area Calculation

To guarantee geographic accuracy without distorting high-latitude or equatorial regions:
- For **Projected Coordinate Reference Systems** (e.g. UTM `EPSG:32621`), pixel area is:
  $$\text{Area}_{\text{pixel}} = |res_x \times res_y| \quad (\text{m}^2)$$
- For **Geographic Coordinate Reference Systems** (`EPSG:4326`), degrees are **never** treated as planar meters. Ellipsoidal cosine latitude scaling is applied:
  $$\Delta x = res_x \times 111320.0 \times \cos(\text{lat}_{\text{center}})$$
  $$\Delta y = res_y \times 110540.0$$
  $$\text{Area}_{\text{pixel}} = |\Delta x \times \Delta y| \quad (\text{m}^2)$$

---

## 6. Time-Series & Future Prediction Boundary Contract

Multi-temporal observation series are assembled and sorted chronologically:
- **Observation Gaps**: Intervals exceeding 60 days without a cloud-free observation are flagged with `OBSERVATION_INTERVAL_GAP`.
- **Trend Slope**: Empirical annualized ordinary least squares slope is computed across historical points.
- **Strict Future Prediction Horizon**:
  - Historical empirical points are bounded strictly between 1972 and 2026.
  - Future projections (2027–2050) require explicit baseline training ranges, model versions (e.g. `ARIMA_v1`), and named IPCC/SSP climate scenarios (`SSP2-4.5_BUSINESS_AS_USUAL`).
