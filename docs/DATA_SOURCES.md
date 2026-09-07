# ORBIT Data Sources, Provenance & Licensing

## 1. Authoritative Data Sources Inventory

ORBIT integrates authoritative Earth Observation (EO) satellite constellations, open geospatial vector infrastructure, and cartographic tile services. All data ingestion strictly respects upstream intellectual property, open access licenses, and attribution guidelines.

| Source / Constellation | Operator / Provider | Modality & Resolution | Primary Role in ORBIT | License / Terms | Authentication |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Copernicus Sentinel-2** | European Space Agency (ESA) / European Commission | Optical Multi-Spectral (10m, 20m, 60m GSD, 13 bands) | Vegetation (NDVI), Water (NDWI), Urban (NDBI), Soil (SAVI) band math | [Copernicus Open Access Policy](https://sentinels.copernicus.eu/web/sentinel/terms-conditions) (Free, full, open) | No API key required for public AWS STAC assets |
| **Copernicus Sentinel-1** | European Space Agency (ESA) / European Commission | C-Band Synthetic Aperture Radar (SAR GRD, 10m GSD) | Cloud-penetrating all-weather structural validation, surface roughness | [Copernicus Open Access Policy](https://sentinels.copernicus.eu/web/sentinel/terms-conditions) (Free, full, open) | No API key required for public AWS STAC assets |
| **Landsat 8 & 9** | USGS / NASA | Optical & Thermal Multi-Spectral (30m GSD, 11 bands) | Decadal multi-year baseline comparisons (1984–present) | [USGS Landsat Policy](https://www.usgs.gov/landsat-missions/landsat-data-policy) (Public Domain / CC0 equivalent) | No API key required for public AWS STAC assets |
| **OpenStreetMap (OSM)** | OpenStreetMap Foundation & Contributors | Vector Geometries (Lines, Polygons, Points) | Transport corridor proximity, road spur detection, spatial buffering | [Open Database License (ODbL 1.0)](https://opendatacommons.org/licenses/odbl/) | No API key required |
| **AWS Earth Search STAC** | Element84 / Amazon Web Services | SpatioTemporal Asset Catalog (STAC API v1.0.0) | Standardized satellite scene discovery, spatial querying, footprint filtering | Open STAC API Service | No credentials required for metadata search |
| **MapTiler Cloud** | MapTiler AG | Vector & Raster Map Tiles (MapLibre style specification) | Interactive basemaps (Tactical Dark, Scientific Light, Satellite Hybrid) | [MapTiler Terms of Service](https://www.maptiler.com/terms/) | Requires free API key configured in `.env` (`VITE_MAPTILER_API_KEY`) |

---

## 2. Granular Data Specifications & Sensor Properties

### 2.1 Copernicus Sentinel-2 Multi-Spectral Instrument (MSI)
- **Product Type**: Level-2A Bottom-of-Atmosphere (BOA) surface reflectance.
- **Spectral Bands Used**:
  - `B02` (Blue, 490 nm, 10m): Atmospheric baseline and water body classification.
  - `B03` (Green, 560 nm, 10m): NDWI calculation and water delineation.
  - `B04` (Red, 665 nm, 10m): Chlorophyll absorption and NDVI calculation.
  - `B08` (NIR, 842 nm, 10m): Cellular canopy reflection for biomass estimation.
  - `B11` (SWIR-1, 1610 nm, 20m): Moisture sensitivity and built-up index (NDBI).
  - `SCL` (Scene Classification Layer, 20m): Algorithmic cloud, cloud shadow, and snow masking.
- **Revisit Frequency**: 5 days at the equator (constellation Sentinel-2A + Sentinel-2B).
- **Attribution Statement**: *"Contains modified Copernicus Sentinel data (2024–2026), processed by ORBIT."*

### 2.2 Copernicus Sentinel-1 Synthetic Aperture Radar (SAR)
- **Product Type**: Level-1 Ground Range Detected (GRD) in Interferometric Wide (IW) swath mode.
- **Polarizations Used**:
  - `VV` (Vertical Transmit / Vertical Receive): Co-polarized backscatter for roughness and moisture estimation.
  - `VH` (Vertical Transmit / Horizontal Receive): Cross-polarized backscatter sensitive to volume scattering from volumetric tree canopies.
- **Role**: Validates physical tree trunk and canopy removal regardless of cloud cover, smoke, or nocturnal conditions.
- **Attribution Statement**: *"Contains modified Copernicus Sentinel-1 data (2024–2026), processed by ORBIT."*

### 2.3 USGS / NASA Landsat-8 & Landsat-9 (OLI/TIRS)
- **Product Type**: Collection 2 Level-2 Surface Reflectance.
- **Role**: Provides long-term multi-decadal historical reference frames to corroborate whether recent changes deviate from 10-to-40-year natural seasonal baselines.
- **Attribution Statement**: *"USGS/NASA Landsat data courtesy of the U.S. Geological Survey."*

### 2.4 OpenStreetMap Infrastructure Networks
- **Data Layers**: Highways, motorways, trunk roads, primary/secondary transit corridors, and unpaved logging spurs (`highway=*`, `surface=*`, `tracktype=*`).
- **Spatial Analysis**: Geodesic buffer generation ($< 2.5\text{ km}$ and $< 5.0\text{ km}$) correlating deforestation clusters with human accessibility corridors.
- **Attribution Statement**: *"(c) OpenStreetMap contributors, licensed under ODbL 1.0."*

---

## 3. Cryptographic Provenance & Lineage Architecture

To guarantee the reproducibility and integrity of intelligence dossiers, ORBIT enforces immutable provenance records:

```json
{
  "dataset_id": "copernicus-s2-l2a",
  "scene_id": "S2B_MSIL2A_20260718T140049_N0512_R067_T21LYJ_20260718T173012",
  "asset_key": "B04",
  "sha256_checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "platform": "Sentinel-2B",
  "sensor": "MSI",
  "spatial_resolution_m": 10.0,
  "crs": "EPSG:32721",
  "is_test_fixture": false,
  "provenance_hash_sha256": "9a3f5c7e2b1d40889cf611e0e84b2319c52df89401768bbec3820984920df441"
}
```

### Invariants:
1. **Zero Silent Modification**: Every raster read, intermediate index array, and extracted vector geometry is tagged with its origin scene ID and calculation algorithm version.
2. **Explicit Test Fixture Flagging**: Synthetic testing fixtures are strictly flagged with `is_test_fixture: true` and cannot be commingled with real operational sensor streams.
3. **Deterministic Digest Signing**: Final intelligence reports contain a SHA-256 digital fingerprint calculated over the canonical JSON representation of all cited evidence.
