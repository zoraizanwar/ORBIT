import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from shapely.geometry import shape
from geoalchemy2.shape import from_shape
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SensingModality, EpistemicLevel
from app.models.eo.dataset_registry import DatasetRegistry
from app.models.eo.imagery_scene import ImageryScene
from app.models.eo.imagery_asset import ImageryAsset
from app.services.eo.stac.models import (
    STACSearchRequest,
    STACSearchResponse,
    NormalizedImageryScene,
    RasterAssetReference,
)
from app.services.eo.stac.client import stac_client_manager
from app.services.eo.provenance.licensing import get_canonical_attribution, DEFAULT_DATASET_LICENSES


async def execute_scene_discovery(request: STACSearchRequest) -> STACSearchResponse:
    """
    Executes STAC discovery across configured providers.
    """
    return await stac_client_manager.search(request)


async def register_imagery_scene(
    session: AsyncSession,
    scene: NormalizedImageryScene,
) -> ImageryScene:
    """
    Idempotently persists a normalized STAC imagery scene and its assets into eo.imagery_scenes.
    """
    # 1. Ensure dataset exists in eo.dataset_registry
    ds_check = await session.execute(
        select(DatasetRegistry).where(DatasetRegistry.id == scene.dataset_id)
    )
    dataset = ds_check.scalar_one_or_none()
    if not dataset:
        license_meta = DEFAULT_DATASET_LICENSES.get(scene.dataset_id, {
            "dataset_name": f"{scene.platform} Observations",
            "provider": scene.provider,
            "license": scene.license,
            "attribution_template": scene.attribution,
        })
        dataset = DatasetRegistry(
            id=scene.dataset_id,
            provider=license_meta["provider"],
            dataset_name=license_meta["dataset_name"],
            modality=scene.modality,
            license=license_meta["license"],
            attribution=license_meta.get("attribution_template", scene.attribution),
        )
        session.add(dataset)
        await session.flush()

    # 2. Check if scene already registered
    existing_scene_res = await session.execute(
        select(ImageryScene).where(ImageryScene.provider_scene_id == scene.item_id)
    )
    existing_scene = existing_scene_res.scalar_one_or_none()

    geom_shape = shape(scene.geometry)
    wkb_geom = from_shape(geom_shape, srid=4326)

    if existing_scene:
        # Update mutable properties
        existing_scene.cloud_cover = scene.cloud_cover
        existing_scene.metadata_payload = scene.metadata_payload
        existing_scene.thumbnail_url = scene.thumbnail_url
        await session.flush()
        return existing_scene

    # Create new ImageryScene
    new_scene = ImageryScene(
        dataset_id=scene.dataset_id,
        provider_scene_id=scene.item_id,
        acquisition_datetime=scene.acquisition_datetime,
        platform=scene.platform,
        sensor=scene.sensor,
        modality=scene.modality,
        cloud_cover=scene.cloud_cover,
        processing_level=scene.processing_level,
        spatial_resolution=scene.spatial_resolution,
        geometry=wkb_geom,
        thumbnail_url=scene.thumbnail_url,
        metadata_payload=scene.metadata_payload,
    )
    session.add(new_scene)
    await session.flush()

    # 3. Create ImageryAssets
    for key, asset in scene.assets.items():
        db_asset = ImageryAsset(
            imagery_scene_id=new_scene.id,
            asset_key=asset.asset_key,
            href=asset.href,
            media_type=asset.media_type,
            roles=asset.roles,
            title=asset.title,
            band_metadata=asset.band.model_dump() if asset.band else {},
            gsd=asset.gsd,
            nodata=asset.nodata,
            file_size=asset.file_size_bytes,
            checksum=asset.checksum,
            is_cloud_optimized=asset.is_cloud_optimized,
        )
        session.add(db_asset)

    await session.flush()
    return new_scene


async def get_registered_scene_by_id(
    session: AsyncSession,
    scene_id: uuid.UUID,
) -> Optional[Dict[str, Any]]:
    """
    Retrieves registered scene and its GeoJSON footprint.
    """
    sql = """
        SELECT 
            s.id::text,
            s.dataset_id,
            s.provider_scene_id,
            s.acquisition_datetime,
            s.platform,
            s.sensor,
            s.modality,
            s.cloud_cover,
            s.processing_level,
            s.spatial_resolution,
            ST_AsGeoJSON(s.geometry) as geojson_geom,
            ARRAY[
                ST_XMin(s.geometry),
                ST_YMin(s.geometry),
                ST_XMax(s.geometry),
                ST_YMax(s.geometry)
            ] as bbox_arr,
            s.thumbnail_url,
            s.metadata_payload,
            s.created_at,
            d.provider,
            d.license,
            d.attribution
        FROM eo.imagery_scenes s
        JOIN eo.dataset_registry d ON d.id = s.dataset_id
        WHERE s.id = :scene_id
    """
    res = await session.execute(text(sql), {"scene_id": scene_id})
    row = res.fetchone()
    if not row:
        return None

    r = row._asdict()
    geom_json = json.loads(r["geojson_geom"]) if r["geojson_geom"] else None
    bbox_list = [float(v) for v in r["bbox_arr"]] if r["bbox_arr"] else None

    return {
        "id": r["id"],
        "dataset_id": r["dataset_id"],
        "provider_scene_id": r["provider_scene_id"],
        "acquisition_datetime": r["acquisition_datetime"].isoformat() if r["acquisition_datetime"] else None,
        "platform": r["platform"],
        "sensor": r["sensor"],
        "modality": r["modality"],
        "cloud_cover": r["cloud_cover"],
        "processing_level": r["processing_level"],
        "spatial_resolution": r["spatial_resolution"],
        "geometry": geom_json,
        "bbox": bbox_list,
        "thumbnail_url": r["thumbnail_url"],
        "metadata": r["metadata_payload"],
        "provider": r["provider"],
        "license": r["license"],
        "attribution": r["attribution"],
        "epistemic_level": "OBSERVED",
    }


async def list_scene_assets(
    session: AsyncSession,
    scene_id: uuid.UUID,
) -> List[Dict[str, Any]]:
    """
    Retrieves all asset references for a registered scene.
    """
    sql = """
        SELECT 
            id::text,
            imagery_scene_id::text,
            asset_key,
            href,
            media_type,
            roles,
            title,
            band_metadata,
            gsd,
            nodata,
            file_size,
            checksum,
            is_cloud_optimized,
            created_at
        FROM eo.imagery_assets
        WHERE imagery_scene_id = :scene_id
        ORDER BY asset_key ASC
    """
    res = await session.execute(text(sql), {"scene_id": scene_id})
    results = []
    for row in res.fetchall():
        r = row._asdict()
        results.append({
            "id": r["id"],
            "scene_id": r["imagery_scene_id"],
            "asset_key": r["asset_key"],
            "href": r["href"],
            "media_type": r["media_type"],
            "roles": r["roles"] or [],
            "title": r["title"],
            "band_metadata": r["band_metadata"] or {},
            "gsd": r["gsd"],
            "nodata": r["nodata"],
            "file_size": r["file_size"],
            "checksum": r["checksum"],
            "is_cloud_optimized": r["is_cloud_optimized"],
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
        })
    return results
