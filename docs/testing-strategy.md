# ORBIT: Comprehensive Testing Strategy & Quality Assurance

## 1. Testing Pyramid & Verification Tiers

To ensure commercial-grade reliability and mathematical precision, ORBIT enforces a rigorous multi-tier testing framework:

```
                  / \
                 / E2E \       Playwright automated browser workflows (12 critical user journeys)
                /-------\
               / Integr. \     FastAPI API tests + Celery worker task execution + PostgreSQL test DB
              /-----------\
             / Geospatial  \   Mathematical geodesic precision, PostGIS ST_Area validation, reprojection
            /---------------\
           /   Unit & AI     \ PyTest band math, SCL masking, Otsu thresholding, LLM anti-hallucination
          /-------------------\
```

---

## 2. Geospatial & Raster Mathematical Precision Tests

Geospatial computations are validated against analytical ground truth benchmarks:

1. **Geodesic Surface Area Verification**:
   - Test target: Equator $1^\circ \times 1^\circ$ square vs. $60^\circ\text{N}$ $1^\circ \times 1^\circ$ square.
   - Assert that `ST_Area(geom::geography)` matches WGS84 ellipsoidal formula within $0.001\%$ error, while planar area fails by expected distortion margins.
2. **Spectral Index Calculation Invariants**:
   - Pure NIR reflection ($NIR=1.0, RED=0.0$) $\rightarrow$ assert $NDVI == +1.0$.
   - Dense water absorption ($NIR=0.0, RED=1.0$) $\rightarrow$ assert $NDVI == -1.0$.
   - SCL Cloud Pixel ($SCL=9$) $\rightarrow$ assert mask yields `numpy.nan` across all derived indices.
3. **Change Detection Segmentation**:
   - Synthetic bi-temporal rasters with known injected change squares ($100\text{ pixels} \times 10\text{m resolution} = 10,000\text{ m}^2 = 0.01\text{ km}^2$).
   - Assert that vectorization polygon area returns $0.01\text{ km}^2 \pm 0.0001$.

---

## 3. AI Grounding & Anti-Hallucination Automated Verification Tests

Every LLM prompt template is tested with continuous automated validation against synthetic and historical fact sheets:

```python
import pytest
from orbit.services.ai_validator import verify_ai_briefing, AIOutputVerificationError

def test_ai_strict_numerical_grounding():
    fact_sheet = {
        "authoritative_measurements": [
            {"name": "affected_area_km2", "value": 14.23},
            {"name": "vegetation_loss_percent", "value": 31.4}
        ]
    }
    
    # Passing narrative citing exact grounded numbers
    valid_narrative = (
        "Satellite telemetry indicates an affected area of 14.23 km², representing a "
        "measured vegetation loss of 31.4% across the monitored corridor."
    )
    assert verify_ai_briefing(fact_sheet, valid_narrative) is True
    
    # Failing narrative with hallucinated metric (e.g. 19.85 km²)
    hallucinated_narrative = (
        "Satellite telemetry indicates an affected area of 19.85 km² representing severe loss."
    )
    with pytest.raises(AIOutputVerificationError):
        verify_ai_briefing(fact_sheet, hallucinated_narrative)
```

---

## 4. End-to-End Automated User-Flow Matrix (Playwright)

| E2E Test Flow ID | Description | Automated Verification Steps |
|---|---|---|
| `E2E-01` | User Registration & Login | Register new analyst $\rightarrow$ Verify Argon2id hash in DB $\rightarrow$ Log in $\rightarrow$ Receive JWT tokens in memory/cookie. |
| `E2E-02` | Global Location Search | Search "Suez Canal" $\rightarrow$ Verify gazetteer bounding box zoom $\rightarrow$ Assert map center coordinates. |
| `E2E-03` | Road Network Layer Toggle | Zoom into Cairo ($Z=14$) $\rightarrow$ Vector tiles load $\rightarrow$ Assert highway class labels and lane counts render. |
| `E2E-04` | AOI Polygon Drawing | Draw polygon over reservoir $\rightarrow$ PostGIS computes surface area $\rightarrow$ Displays live hectare counter. |
| `E2E-05` | Earth Observation Discovery | Select Sentinel-2 L2A (2020 vs 2024) $\rightarrow$ Filter cloud $< 10\%$ $\rightarrow$ Scene cards populate with thumbnails. |
| `E2E-06` | Analysis Execution & Progress | Click "Run Change Detection" $\rightarrow$ Celery worker picks up job $\rightarrow$ SSE stream logs progress $0\% \rightarrow 100\%$. |
| `E2E-07` | Change Visualization & Slider | Map loads bi-temporal split-screen swipe comparison $\rightarrow$ Change vector mask overlays in warning red/orange. |
| `E2E-08` | Evidence Audit Trace | Click change polygon $\rightarrow$ Evidence drawer opens $\rightarrow$ Verifies upstream Sentinel scene ID and SHA-256 hash. |
| `E2E-09` | Historical Yearly Profile | Open Historical Timeline $\rightarrow$ Chart renders mean annual NDVI 2018–2024 $\rightarrow$ Identifies drought anomaly year. |
| `E2E-10` | Report Dossier Generation | Click "Generate Intelligence Report" $\rightarrow$ PDF compiles with maps, charts, evidence $\rightarrow$ Download and verify PDF binary. |
