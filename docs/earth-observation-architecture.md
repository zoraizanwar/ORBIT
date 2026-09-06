# ORBIT: Earth Observation Data Architecture & Multi-Modal Ingestion

## 1. Multi-Modal Sensing: Optical & SAR Modalities

ORBIT avoids modeling SAR (Synthetic Aperture Radar) as a mere cloud fallback for optical sensors. Instead, **Optical Radiometry** and **Synthetic Aperture Radar (SAR)** are treated as distinct sensing modalities, each with distinct physical interaction mechanisms, processing pipelines, and domain suitabilities.

```
                               +--------------------------------------------+
                               |        ANALYTICAL REQUIREMENT EVALUATION   |
                               +---------------------+----------------------+
                                                     |
             +---------------------------------------+---------------------------------------+
             |                                                                               |
+------------v-------------------------------+               +-------------------------------v------------+
| OPTICAL SENSING MODALITY                   |               | SAR SENSING MODALITY                       |
| - Physics: Reflected solar radiation       |               | - Physics: Active microwave backscatter    |
| - Spectral: Visible, NIR, SWIR, Red-Edge   |               | - Spectral: C-Band (5.405 GHz) VV, VH, Cross|
| - Strengths: Chlorophyll pigment, water    |               | - Strengths: Dielectric moisture, surface  |
|   clarity, soil mineralogy, colorimetry    |               |   roughness, structural geometry, day/night|
| - Limitations: Cloud-sensitive, daylight   |               | - Limitations: Speckle noise, layover in   |
|   dependent ($10\text{m} - 30\text{m}$)    |               |   steep terrain, geometric foreshortening  |
| - Target: Sentinel-2 MSI, Landsat 4-9 OLI  |               | - Target: Sentinel-1 C-Band SAR GRD / RTC  |
+--------------------------------------------+               +--------------------------------------------+
```

---

## 2. Modality Suitability Assessment Engine

Before querying or acquiring scene assets, the **Modality Suitability Engine** evaluates the analytical objective against sensor characteristics and environmental conditions:

```python
from enum import Enum
from pydantic import BaseModel

class SensingModality(str, Enum):
    OPTICAL_MULTISPECTRAL = "OPTICAL_MULTISPECTRAL"
    SAR_MICROWAVE = "SAR_MICROWAVE"
    HYBRID_FUSION = "HYBRID_FUSION"

class ModalityAssessment(BaseModel):
    recommended_modality: SensingModality
    optical_suitability_score: float # 0.0 to 1.0 (based on historical cloudiness & solar angle)
    sar_suitability_score: float     # 0.0 to 1.0 (based on terrain slope & structural targets)
    rationale: str

def evaluate_modality_suitability(analytical_goal: str, aoi_geometry, target_date) -> ModalityAssessment:
    """Evaluates whether Optical, SAR, or Hybrid fusion is optimal for the analytical task."""
    if analytical_goal in ["FLOOD_INUNDATION_RAPID_RESPONSE", "STRUCTURAL_COHERENCE_MONITORING"]:
        return ModalityAssessment(
            recommended_modality=SensingModality.SAR_MICROWAVE,
            optical_suitability_score=0.45,
            sar_suitability_score=0.95,
            rationale="SAR provides direct sensitivity to water surface dielectric contrast and structural backscatter regardless of weather."
        )
    elif analytical_goal in ["VEGETATION_HEALTH_NDVI", "ALGAL_BLOOM_DETECTION"]:
        return ModalityAssessment(
            recommended_modality=SensingModality.OPTICAL_MULTISPECTRAL,
            optical_suitability_score=0.90,
            sar_suitability_score=0.30,
            rationale="Optical Red and NIR absorption bands are required for chlorophyll quantification."
        )
    else:
        return ModalityAssessment(
            recommended_modality=SensingModality.HYBRID_FUSION,
            optical_suitability_score=0.80,
            sar_suitability_score=0.85,
            rationale="Dual-modality fusion combines multi-spectral land cover with structural roughness verification."
        )
```

---

## 3. Dataset Registry & Licensing Governance

> **"ORBIT is designed around free, open, and public data sources wherever practical. Each provider and dataset must have its own recorded licensing, attribution, access, redistribution, and commercial-use constraints."**

The platform maintains an explicit **Dataset & Licensing Registry** in PostgreSQL (`eo.dataset_registry`):

| Dataset Identifier | Primary Provider | Open Access Type | License & Terms | Attribution Text Required | Commercial Redistribution Rights |
|---|---|---|---|---|---|
| `copernicus-s2-l2a` | Copernicus CDSE / ESA | Open Access (No cost) | EU Copernicus Open Data Policy (Regulation EU 377/2014) | *"Contains modified Copernicus Sentinel data [Year]"* | Unrestricted commercial and non-commercial use with required attribution. |
| `copernicus-s1-grd` | Copernicus CDSE / ESA | Open Access (No cost) | EU Copernicus Open Data Policy | *"Contains modified Copernicus Sentinel data [Year]"* | Unrestricted commercial and non-commercial use with required attribution. |
| `usgs-landsat-c2l2` | USGS / NASA via AWS | Open Access (Public Domain) | USGS Public Domain (U.S. Government Work) | *"Landsat data courtesy of the U.S. Geological Survey"* | Unrestricted global public domain. |
| `copernicus-dem-30` | ESA / Airbus | Open Access (No cost) | Copernicus DEM Open Policy | *"Copernicus DEM data © DLR, Airbus, ESA"* | Free open distribution with attribution. |
| `osm-roads-planet` | OpenStreetMap Foundation | Open Database (No cost) | Open Database License (ODbL 1.0) | *"© OpenStreetMap contributors"* | Free use; derivative databases must remain under ODbL with attribution. |

---

## 4. Cloud-Optimized GeoTIFF (COG) Streaming Pipeline

To eliminate massive multi-gigabyte local file downloads:
1. **Windowed HTTP Range Requests**: Using `rasterio.windows.from_bounds`, the worker queries the remote COG header, fetches only the tile chunks overlapping the AOI polygon, and streams them into memory.
2. **Local Caching Layer**: Downloaded window arrays are cached locally in `/artifacts/rasters/{scene_id}_{aoi_hash}.tif` with Least-Recently-Used (LRU) disk eviction.
3. **Decoupled Reprojection**: Pixels are reprojected on the fly to the target local UTM coordinate system during ingestion.
