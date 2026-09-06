import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RealDatasetProvenanceRecord(BaseModel):
    """
    Comprehensive Provenance Record for Earth Observation Datasets & Derivatives.
    Survives throughout the entire analytical lifecycle.
    """
    source_provider: str
    catalog_id: str
    collection_id: str
    scene_id: str
    asset_key: str
    source_url: str
    license: str
    attribution: str
    acquisition_datetime: str
    download_datetime: str
    local_file_size: int
    sha256: str
    crs: str
    resolution: float
    bounds: List[float]
    platform: str
    instrument: str
    processing_level: str
    software_version: str = "ORBIT-EO-v1.5.0"
    algorithm_version: str = "ORBIT-Analytical-v1.5.0"
    is_test_fixture: bool = False
    epistemic_level: str = "OBSERVED"
    metadata_digest: Optional[str] = None

    def compute_provenance_digest(self) -> str:
        """Computes deterministic SHA-256 fingerprint over the canonical provenance payload."""
        payload = {
            "source_provider": self.source_provider,
            "catalog_id": self.catalog_id,
            "collection_id": self.collection_id,
            "scene_id": self.scene_id,
            "asset_key": self.asset_key,
            "source_url": self.source_url,
            "license": self.license,
            "acquisition_datetime": self.acquisition_datetime,
            "sha256": self.sha256,
            "crs": self.crs,
            "platform": self.platform,
            "is_test_fixture": self.is_test_fixture,
            "epistemic_level": self.epistemic_level,
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_evidence_item_dict(self) -> Dict[str, Any]:
        """Formats the provenance record for integration into an EvidencePackage node."""
        return {
            "id": f"ev-prov-{self.scene_id[:16]}-{self.asset_key}",
            "type": "OBSERVATION",
            "epistemic_level": self.epistemic_level,
            "source_id": f"{self.platform}:{self.scene_id}",
            "value": self.local_file_size,
            "unit": "bytes",
            "timestamp": self.acquisition_datetime,
            "properties": {
                "sha256": self.sha256,
                "provenance_digest": self.compute_provenance_digest(),
                "license": self.license,
                "attribution": self.attribution,
                "resolution_m": self.resolution,
                "crs": self.crs,
                "is_test_fixture": self.is_test_fixture,
            },
        }
