from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.services.eo.stac.models import NormalizedImageryScene


class SceneProvenanceRecord(BaseModel):
    provider: str
    collection_id: str
    item_id: str
    dataset_id: str
    platform: str
    sensor: str
    modality: str
    acquisition_datetime: str
    cloud_cover: Optional[float]
    spatial_resolution_meters: float
    license: str
    attribution: str
    epistemic_level: str = "OBSERVED"
    lineage_path: List[str]


def construct_scene_lineage(scene: NormalizedImageryScene) -> SceneProvenanceRecord:
    """
    Constructs an immutable provenance trace from provider STAC Item to ORBIT ImageryScene.
    """
    return SceneProvenanceRecord(
        provider=scene.provider,
        collection_id=scene.collection_id,
        item_id=scene.item_id,
        dataset_id=scene.dataset_id,
        platform=scene.platform,
        sensor=scene.sensor,
        modality=scene.modality.value,
        acquisition_datetime=scene.acquisition_datetime.isoformat(),
        cloud_cover=scene.cloud_cover,
        spatial_resolution_meters=scene.spatial_resolution,
        license=scene.license,
        attribution=scene.attribution,
        epistemic_level=scene.epistemic_level.value,
        lineage_path=[
            f"Provider:{scene.provider}",
            f"STAC_Collection:{scene.collection_id}",
            f"STAC_Item:{scene.item_id}",
            f"Dataset:{scene.dataset_id}",
            f"ORBIT_ImageryScene:{scene.item_id}",
        ],
    )
