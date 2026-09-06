# ORBIT Dataset Provenance & Cryptographic Lineage Model

## 1. Provenance Invariants

ORBIT implements an immutable, verifiable lineage model for all datasets, rasters, vector geometries, derived calculations, and AI intelligence artifacts.

```
                     ┌─────────────────────────────┐
                     │   Raw Sensor Telemetry      │
                     │ (STAC Level-2A GeoTIFFs)    │
                     └─────────────────────────────┘
                                    │
                         SHA-256 Checksum Verification
                                    │
                                    ▼
                     ┌─────────────────────────────┐
                     │  Calibrated Spectral Engine │
                     │  (Deterministic NDVI/NDBI)  │
                     └─────────────────────────────┘
                                    │
                         Algorithm Version Tagging
                                    │
                                    ▼
                     ┌─────────────────────────────┐
                     │   Evidence Graph Assembly   │
                     │  (Canonical JSON Digest)    │
                     └─────────────────────────────┘
                                    │
                         SHA-256 Provenance Seal
                                    │
                                    ▼
                     ┌─────────────────────────────┐
                     │    Intelligence Dossier     │
                     │ (Auditable Decision Report) │
                     └─────────────────────────────┘
```

## 2. RealDatasetProvenanceRecord Schema

Every acquired raster or analytical asset is cataloged with a structured provenance record:

| Field | Type | Description |
| :--- | :--- | :--- |
| `dataset_id` | `str` | Unique identifier (e.g. `copernicus-s2-l2a`) |
| `scene_id` | `str` | STAC scene identifier |
| `asset_key` | `str` | Band / asset key (e.g. `B04`, `B08`) |
| `source_url` | `str` | Origin STAC or S3/HTTP endpoint |
| `local_path` | `str` | Verified local cache location |
| `sha256_checksum` | `str` | 64-character hexadecimal SHA-256 digest |
| `file_size_bytes` | `int` | Exact file size in bytes |
| `acquisition_datetime` | `datetime` | Sensor acquisition timestamp |
| `platform` | `str` | Platform name (`Sentinel-2A`, `Sentinel-2B`, `Sentinel-1A`) |
| `sensor` | `str` | Instrument (`MSI`, `C-SAR`) |
| `spatial_resolution_m` | `float` | Ground sample distance (meters) |
| `crs` | `str` | Coordinate Reference System (e.g. `EPSG:4326`) |
| `license` | `str` | Upstream data license (e.g. `EU Copernicus Open Data Policy`) |
| `attribution` | `str` | Required legal copyright / attribution text |
| `is_test_fixture` | `bool` | Strict binary flag (`false` for real data, `true` for fixtures) |
| `provenance_hash_sha256` | `str` | Cryptographic digest across all normalized record fields |

## 3. Cryptographic Provenance Hashing Function

The provenance digest is computed deterministically over a canonical, sorted JSON dictionary:

```python
record_dict = {
    "dataset_id": self.dataset_id,
    "scene_id": self.scene_id,
    "asset_key": self.asset_key,
    "sha256_checksum": self.sha256_checksum,
    "file_size_bytes": self.file_size_bytes,
    "platform": self.platform,
    "sensor": self.sensor,
    "crs": self.crs,
    "is_test_fixture": self.is_test_fixture,
}
serialized = json.dumps(record_dict, sort_keys=True)
return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
```

## 4. Audit Trail & Lifecycle Tracking

Every operational analysis run emits structured JSON lifecycle events via `AnalysisLifecycleTracker`:
- `ANALYSIS_STARTED`: Records run ID, AOI ID, algorithm version (`ORBIT-RealPipeline-v1.5.0`), and sanitized parameters.
- `ANALYSIS_COMPLETED`: Records wall-clock duration in milliseconds, computed metrics, evidence package SHA-256 hash, report provenance hash, and status.
- `ANALYSIS_FAILED`: Records sanitized error reason with zero sensitive credential leakage.
