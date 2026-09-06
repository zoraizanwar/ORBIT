# ORBIT: Dataset Evaluation & Licensing Strategy

## 1. Core Data Strategy & Licensing Philosophy

> **"ORBIT is designed around free, open, and public data sources wherever practical. Each provider and dataset must have its own recorded licensing, attribution, access, redistribution, and commercial-use constraints."**

The platform operates on a **Local-First Zero-Cost Baseline** for local research and development, utilizing open scientific and governmental archives, while explicitly tracking legal provenance and distribution rights.

---

## 2. Comprehensive Dataset Evaluation & Licensing Registry

| Dataset / Source | Coverage & Epochs | Spatial Resolution | Access Protocols | License & Commercial Terms | Mandatory Attribution Text | Commercial Redistribution Rights |
|---|---|---|---|---|---|---|
| **Copernicus Sentinel-2 (MSI)** | Global landmass; 2015–Present | $10\text{m}, 20\text{m}, 60\text{m}$ | CDSE STAC, Planetary Computer, AWS S3 | EU Copernicus Open Data Policy (Regulation EU 377/2014) | *"Contains modified Copernicus Sentinel data [Year]"* | Unrestricted commercial and academic use; derivative works allowed. |
| **Copernicus Sentinel-1 (C-Band SAR)** | Global; 2014–Present | $10\text{m} \times 10\text{m}$ (GRD High-Res) | CDSE STAC, Planetary Computer (RTC COG) | EU Copernicus Open Data Policy | *"Contains modified Copernicus Sentinel data [Year]"* | Unrestricted commercial and academic use; all-weather radar. |
| **USGS Landsat 8/9 (OLI/TIRS)** | Global; 2013–Present | $30\text{m}$ ($15\text{m}$ Pan) | USGS M2M API, AWS Open Data STAC | Public Domain (U.S. Government Work) | *"Landsat data courtesy of the U.S. Geological Survey"* | Unrestricted global public domain without copyright restrictions. |
| **USGS Landsat 4-5 TM & 7 ETM+** | Global; 1982–2012 (TM), 1999–2022 (ETM+) | $30\text{m}$ Optical | USGS Landsat Collection 2 on AWS S3 | Public Domain (U.S. Government Work) | *"Landsat data courtesy of the U.S. Geological Survey"* | Unrestricted global public domain for multi-decadal baselines. |
| **Copernicus DEM (GLO-30)** | Global landmass; 2020 baseline | $30\text{m}$ elevation grid | Planetary Computer STAC, OpenTopography | Copernicus DEM Policy | *"Copernicus DEM data © DLR, Airbus, ESA"* | Free distribution with attribution for elevation & terrain modeling. |
| **OpenStreetMap (OSM)** | Global; 2004–Present | Sub-meter vector topology | Geofabrik PBF extracts, Overpass API | Open Database License (ODbL 1.0) | *"© OpenStreetMap contributors"* | Free use; derivative database modifications must remain under ODbL with attribution. |
| **HydroRIVERS & HydroLAKES** | Global hydrography | Global vector drainage | WWF / HydroSHEDS | Creative Commons BY 4.0 | *"HydroSHEDS database © WWF"* | Free commercial and non-commercial use with attribution. |
| **EM-DAT Disaster Database** | Global; 1900–Present | Tabular disaster events | CRED / EM-DAT API | Academic / Non-commercial free; Commercial requires license | *"EM-DAT, CRED / UCLouvain"* | Commercial use requires separate enterprise license from CRED. |

---

## 3. Local Ingestion & Progressive Expansion Architecture

1. **On-Demand Windowed COG Ingestion**: Remote multi-spectral bands are accessed via HTTP Range requests without downloading full scenes ($1\text{GB}+$).
2. **Regional Bounding Seeds**: Initial development uses targeted bounding boxes and regional OSM extracts (imported via `osm2pgsql` or `osmium`) without downloading the entire planet.
3. **Automated License Tracking**: Every generated intelligence dossier, PDF report, or GeoJSON export automatically bundles the required attribution texts matching the ingested scene IDs.
