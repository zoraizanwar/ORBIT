# ORBIT Real-World Earth Observation Data Integration

## 1. Overview & Operational Principles

ORBIT Phase 15 proves that the analytical architecture developed across Phases 9–14 functions end-to-end on real, properly licensed Earth-observation and STAC assets, and not solely on synthetic test fixtures.

```
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│     STAC Discovery      │ ──> │    Secure Acquisition   │ ──> │  Pre-Analytical Raster  │
│ (Multi-Criteria Ranker) │     │ (SSRF Guard & SHA-256)  │     │       Validation        │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
                                                                             │
                                                                             ▼
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│  Cryptographic Dossier  │ <── │  Grounded AI Synthesis  │ <── │  8-Tier Real Pipeline   │
│   (Signed Provenance)   │     │ (Claim-Level Citations) │     │  (NDVI/Change/Rules/TS) │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

## 2. Deterministic STAC Scene Ranking

The `DeterministicSceneRanker` evaluates candidate satellite scenes against multi-dimensional criteria without heuristic bias:

$$\text{Rank Score} = w_{\text{temp}} \cdot S_{\text{temporal}} + w_{\text{cloud}} \cdot S_{\text{cloud}} + w_{\text{spatial}} \cdot S_{\text{spatial}} + w_{\text{res}} \cdot S_{\text{resolution}}$$

- **Temporal Proximity Score ($S_{\text{temporal}}$)**: Exponential decay based on distance from target acquisition date:
  $$S_{\text{temporal}} = \exp\left(-\frac{\Delta t_{\text{days}}}{30}\right)$$
- **Cloud Cover Score ($S_{\text{cloud}}$)**: Linear penalty on optical cloud percentage:
  $$S_{\text{cloud}} = \max\left(0, \frac{100 - \text{cloud\_cover}}{100}\right)$$
  *(For SAR microwave sensors where clouds are penetrated, $S_{\text{cloud}} = 1.0$)*
- **Spatial Coverage Score ($S_{\text{spatial}}$)**: Intersection over Union (IoU) between scene bounding box and target AOI.
- **Resolution Score ($S_{\text{resolution}}$)**: Normalized against 10-meter ground sample distance.
- **Tie-Breaking Determinism**: Sorted descending by `(rank_score, item_id)` for stable, reproducible rank ordering.

## 3. Secure Asset Acquisition & Local Caching

All remote satellite assets undergo strict security validation before local caching:
- **SSRF Hardening**: Rejects loopback (`127.0.0.0/8`), RFC 1918 private ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), and cloud metadata endpoints (`169.254.169.254`).
- **Path Traversal Protection**: Enforces canonical path containment inside configured data directories (`./data/cache/eo_assets/`).
- **Memory & Ingestion Safety**: Limits downloads to a maximum of 256 MB per raster asset with chunked streaming.
- **Cryptographic Hashing**: Computes SHA-256 digests on stream completion and stores cache metadata for deduplication.

## 4. Pre-Analytical Raster Validation

Before any spectral calculation occurs, `RealRasterValidator` inspects GeoTIFF headers:
1. **Magic Bytes**: Checks for valid TIFF headers (`II*\0` or `MM\0*`).
2. **Dimension Constraints**: $1 \le \text{width}, \text{height} \le 16384$ pixels.
3. **Coordinate Reference System**: Validates EPSG/WKT presence and non-degeneracy of affine transformation matrices.
4. **Bounding Box Sanity**: Ensures bounds fall within standard geographic limits.
5. **Tile Structure & Checksum**: Verifies block/tile configuration and file integrity without allocating large memory arrays.

## 5. Explicit Data Segregation

Every dataset, scene, asset, and intelligence artifact maintains explicit segregation:
- **Real Operational Data**: `is_test_fixture: false` with complete sensor provenance (Sentinel-2 L2A surface reflectance, EU Copernicus Open Data licensing).
- **Simulated Test Data**: `is_test_fixture: true` with prominent `[TEST FIXTURE - SIMULATED]` labels. No test fixture is ever silently presented as empirical observation.
