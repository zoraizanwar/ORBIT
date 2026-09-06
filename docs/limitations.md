# ORBIT: Physical Limitations, Sensor Boundaries & Detectability Scope

## 1. Product Capability Scope & Inherent Sensor Boundaries

ORBIT defines its core capability transparently:

> **"ORBIT detects observable geographic changes supported by available spatial resolution, temporal coverage, sensor characteristics, data quality, and analytical methodology."**

### Detectable vs. Potentially Undetectable Changes Matrix:

| Domain | Detectable Changes (Supported) | Potentially Undetectable Changes (Physical Constraints) |
|---|---|---|
| **Vegetation & Forestry** | Broadscale clear-cutting ($> 0.5\text{ ha}$), wildfire burn scars, seasonal agricultural harvests, large canopy die-offs. | Selective logging of single trees beneath closed canopy, subtle understory thinning, small shrub clearing $< 10\text{m}$. |
| **Water Bodies & Hydrology** | Multi-hectare reservoir drying, major river course migration, coastal land reclamation, large flood inundation zones ($> 20\text{m}$). | Narrow drainage ditches ($< 5\text{m}$), ephemeral puddles, sub-surface water table depletion, culverted underground streams. |
| **Urban & Built-Up** | New residential subdivisions, commercial logistics centers, highway corridor paving, industrial quarry expansions ($> 400\text{ m}^2$). | Interior building renovations, residential rooftop alterations, single-story room additions, unpaved footpath creation. |
| **Infrastructure & Roads** | Multi-lane highway construction, major bridge erection, new arterial bypasses, railway corridor clearing. | Minor pothole repairs, unmapped rural dirt tracks beneath forest canopy, underground utility trenching with restored turf. |

---

## 2. Sensor Physical Characteristics & Spatial Resolving Limits

| Sensor Platform | Ground Sample Distance (GSD) | Minimum Resolving Target | Physical Limitations |
|---|---|---|---|
| **Sentinel-2 MSI** | $10\text{m}$ (VIS/NIR), $20\text{m}$ (SWIR/Red-Edge) | Features $\ge 20\text{m} \times 20\text{m}$ ($400\text{ m}^2$) | Completely blocked by optical clouds, fog, and heavy cirrus; daylight dependent. |
| **Sentinel-1 SAR** | $10\text{m} \times 10\text{m}$ (GRD High-Res) | Radar reflective targets $\ge 15\text{m}$ | Foreshortening and layover in mountainous terrain; sensitive to speckle noise and soil moisture fluctuations. |
| **Landsat 8/9 OLI** | $30\text{m}$ Multi-spectral, $15\text{m}$ Pan | Features $\ge 60\text{m} \times 60\text{m}$ ($0.36\text{ ha}$) | Coarse for street-level urban changes; excellent for regional multi-spectral baselines. |
| **Landsat 4-5 TM / 7 ETM+**| $30\text{m}$ Optical | Features $\ge 60\text{m} \times 60\text{m}$ | 16-day temporal revisit; Landsat 7 suffers from Scan Line Corrector (SLC) failure post-2003 (data gaps). |
| **OpenStreetMap Vectors** | Variable vector geometry | Mapped nodes and ways | Community-contributed completeness varies globally; unmapped features in remote regions cannot be assumed non-existent. |

---

## 3. Historical Epoch Limitations (1972 vs 2026)

Analytical capabilities cannot be treated as uniform across historical time:
1. **1972–1981 (Landsat 1–3 MSS)**: $60\text{m} \times 80\text{m}$ resolution, 4 broad bands. Sub-hectare change detection and urban road analysis are physically `UNAVAILABLE`.
2. **1982–1998 (Landsat 4–5 TM)**: $30\text{m}$ resolution, 7 bands. High-resolution street-level change is `UNAVAILABLE`; regional vegetation and water are `MODERATE`.
3. **1999–2014 (Landsat 7 ETM+ / MODIS)**: Enhanced multi-spectral; SLC-off gaps post-2003 require gap-masking.
4. **2015–Present (Sentinel-1/2 & Landsat 8/9)**: Full $10\text{m}$ multi-modal constellation capability; `STRONGLY_SUPPORTED`.

---

## 4. Formal "Insufficient Evidence" Protocol

When physical telemetry is obscured by clouds ($> 30\%$), corrupted, or absent:
- The measurement scalar is assigned `NULL` with status `INSUFFICIENT_EVIDENCE`.
- Evidence Strength is set to `INSUFFICIENT`.
- Confidence score is set to `0.0`.
- The system and AI narrative are strictly forbidden from fabricating synthetic findings.
