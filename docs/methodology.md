# ORBIT: Mathematical & Algorithmic Methodology

## 1. Five-Tiered Change Detection Architecture

ORBIT structures change detection and geospatial intelligence across **5 distinct analytical tiers**, explicitly cataloging the mathematical and computational nature of each method:

```
+---------------------------------------------------------------------------------------------------+
| TIER 5: EVIDENCE-GROUNDED AI INTERPRETATION (AI-Generated / LLM Synthesis)                         |
| - Synthesis of natural language executive briefs from verified Level 1-4 facts                    |
| - Method Nature: Generative LLM with Strict JSON Schema & Anti-Hallucination Regex Verification    |
+---------------------------------------------------------------------------------------------------+
                                                 ↑
+---------------------------------------------------------------------------------------------------+
| TIER 4: TEMPORAL EVENT DETECTION & SPATIOTEMPORAL CLUSTERING (Deterministic & Statistical Graph)   |
| - PostGIS ST_ClusterDBSCAN spatiotemporal clustering of contiguous change zones                    |
| - Event lifecycle state machines (EMERGING $\rightarrow$ EXPANDING $\rightarrow$ STABILIZED)      |
| - Road infrastructure buffer correlation (PostGIS ST_DWithin / ST_Intersects)                     |
| - Method Nature: Deterministic Spatial Clustering & Graph State Modeling                          |
+---------------------------------------------------------------------------------------------------+
                                                 ↑
+---------------------------------------------------------------------------------------------------+
| TIER 3: LAND-COVER, SEGMENTATION & OBJECT-LEVEL ANALYSIS (Statistical & Machine Learning)          |
| - Random Forest / U-Net semantic segmentation for land-use classification (LULC)                  |
| - Morphological object extraction, patch geometry, and landscape fragmentation metrics            |
| - Method Nature: Supervised Machine Learning / Mathematical Morphology                            |
+---------------------------------------------------------------------------------------------------+
                                                 ↑
+---------------------------------------------------------------------------------------------------+
| TIER 2: STATISTICAL & TEMPORAL CHANGE DETECTION (Statistical & Signal Processing)                 |
| - Baseline Method: Pixel Differencing ($\Delta I$) + Adaptive Otsu Thresholding + Morphological 3x3|
| - Advanced Method: Continuous Change Detection and Classification (CCDC) harmonic time-series     |
| - SAR Coherence Differencing ($\gamma$) & Ratio Metric ($R = \sigma^0_{t_2} / \sigma^0_{t_1}$)    |
| - Method Nature: Statistical Inference & Time-Series Signal Decomposition                         |
+---------------------------------------------------------------------------------------------------+
                                                 ↑
+---------------------------------------------------------------------------------------------------+
| TIER 1: DETERMINISTIC SPECTRAL INDICES & CALIBRATED DERIVATIVES (Deterministic Mathematics)       |
| - Band Math: NDVI, NDWI, NDBI, MNDWI, SAVI, BSI, EVI                                              |
| - SCL / QA_PIXEL bitmask decoding (Zero-tolerance cloud/shadow exclusion)                         |
| - Radiometric calibration to surface reflectance ($\rho$) and SAR backscatter ($\sigma^0$ in dB)  |
| - Method Nature: Deterministic Radiometric Physics & Arithmetic Formulations                      |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Mathematical Formulations by Tier

### Tier 1: Deterministic Spectral Indices (Deterministic)
Calculated directly from Surface Reflectance ($\rho$) bands:

- **Normalized Difference Vegetation Index (NDVI)**:
  $$NDVI = \frac{\rho_{NIR} - \rho_{RED}}{\rho_{NIR} + \rho_{RED}}$$
- **Modified Normalized Difference Water Index (MNDWI)**:
  $$MNDWI = \frac{\rho_{GREEN} - \rho_{SWIR1}}{\rho_{GREEN} + \rho_{SWIR1}}$$
- **Normalized Difference Built-Up Index (NDBI)**:
  $$NDBI = \frac{\rho_{SWIR1} - \rho_{NIR}}{\rho_{SWIR1} + \rho_{NIR}}$$
- **Soil-Adjusted Vegetation Index (SAVI)** ($L = 0.5$):
  $$SAVI = \frac{\rho_{NIR} - \rho_{RED}}{\rho_{NIR} + \rho_{RED} + L} \times (1 + L)$$
- **Bare Soil Index (BSI)**:
  $$BSI = \frac{(\rho_{SWIR1} + \rho_{RED}) - (\rho_{NIR} + \rho_{BLUE})}{(\rho_{SWIR1} + \rho_{RED}) + (\rho_{NIR} + \rho_{BLUE})}$$
- **Calibrated SAR Backscatter ($\sigma^0$) in Decibels (dB)**:
  $$\sigma^0_{\text{dB}} = 10 \cdot \log_{10}(\text{DN}^2) - K_{\text{cal}}$$

---

### Tier 2: Statistical Change Detection (Statistical / Baseline)
- **Bi-Temporal Spectral Delta**:
  $$\Delta I(x, y) = I_{t_2}(x, y) - I_{t_1}(x, y)$$
- **Baseline Adaptive Otsu Thresholding**:
  Maximizes between-class variance $\sigma_B^2(T)$ across the pixel difference histogram to segment change vs. stable pixels:
  $$\sigma_B^2(T) = \omega_0(T) \omega_1(T) \left[ \mu_0(T) - \mu_1(T) \right]^2$$
- **Baseline Morphological Filtering**:
  Removes isolated salt-and-pepper noise via opening ($3 \times 3$ kernel $K$):
  $$M_{\text{clean}} = (M \ominus K) \oplus K$$
- **Continuous Change Detection and Classification (CCDC) Harmonic Model**:
  Fits seasonal and trend harmonics to multi-year time-series to detect structural breaks:
  $$\hat{\rho}(t) = a_0 + a_1 t + b_1 \cos\left(\frac{2\pi t}{T}\right) + c_1 \sin\left(\frac{2\pi t}{T}\right) + b_2 \cos\left(\frac{4\pi t}{T}\right) + c_2 \sin\left(\frac{4\pi t}{T}\right)$$
  A change is flagged when residual exceeds $3 \times \text{RMSE}$ over 3 consecutive observations.

---

### Tier 3: Object-Level Analysis & Landscape Metrics (Machine Learning & Geodesics)
- **Patch Area & Perimeter**:
  Geodesic polygon boundary evaluation on WGS84 spheroid via PostGIS `ST_Area(geom::geography)` and `ST_Length(geom::geography)`.
- **Landscape Fragmentation Index (Shape Complexity)**:
  $$\text{Shape Complexity} = \frac{\text{Perimeter}_{\text{geodesic}}}{2 \sqrt{\pi \cdot \text{Area}_{\text{geodesic}}}}$$

---

### Tier 4: Spatiotemporal Event Clustering (Deterministic Graph)
- **PostGIS DBSCAN Density Clustering**:
  $$\text{ST\_ClusterDBSCAN}(\text{geometry}, \text{eps} = 50\text{ meters}, \text{minpoints} = 10)$$
- **Road Corridor Interaction**:
  $$\text{ST\_DWithin}(\text{cluster\_geom}::\text{geography}, \text{road\_geom}::\text{geography}, 100\text{ meters})$$

---

### Tier 5: Evidence-Grounded AI Interpretation (Generative LLM with Validation)
- Synthesizes narrative context using an immutable JSON fact sheet containing only Level 1–4 verified numbers.
- Automated AST/Regex validation verifies zero ungrounded numeric hallucination before presentation.
