import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.models.geo.road_feature import RoadFeature
from app.services.geo.road_normalization import normalize_osm_road_properties
from app.services.geo.road_geometry import (
    sanitize_and_repair_linestring,
    calculate_geodesic_length_meters,
    create_road_geometry_element,
)

logger = logging.getLogger("orbit.geo.osm_ingestion")


class IngestionSummary(BaseModel):
    total_processed: int = 0
    successfully_ingested: int = 0
    quarantined_invalid_geometry: int = 0
    skipped_non_road: int = 0
    total_road_length_km: float = 0.0
    attribution: str = Field(default="© OpenStreetMap contributors (ODbL 1.0)")


class OsmFeaturePayload(BaseModel):
    osm_id: int
    coordinates: List[Tuple[float, float]]  # List of [lon, lat]
    tags: Dict[str, Any]


async def ingest_osm_road_batch(
    session: AsyncSession,
    features: List[OsmFeaturePayload],
    chunk_size: int = 500,
) -> IngestionSummary:
    """
    Ingest a batch of OSM road feature payloads into geo.road_features.
    Processes features in streaming chunks, normalizes classifications, validates/repairs geometries,
    and performs upserts on osm_id conflict.
    """
    summary = IngestionSummary()
    summary.total_processed = len(features)

    records_to_upsert: List[Dict[str, Any]] = []

    for item in features:
        # 1. Check if feature contains valid highway tags
        if not item.tags.get("highway"):
            summary.skipped_non_road += 1
            continue

        # 2. Validate and repair LineString geometry
        line_geom = sanitize_and_repair_linestring(item.coordinates)
        if line_geom is None:
            logger.warning(f"Quarantining invalid OSM way {item.osm_id}: geometry repair returned None.")
            summary.quarantined_invalid_geometry += 1
            continue

        # 3. Calculate authoritative geodesic length on WGS84 spheroid
        length_meters = calculate_geodesic_length_meters(line_geom)
        geom_elem = create_road_geometry_element(line_geom)

        # 4. Normalize properties
        props = normalize_osm_road_properties(item.tags)

        record = {
            "id": uuid.uuid4(),
            "osm_id": item.osm_id,
            "geometry": geom_elem,
            "highway_class": props["highway_class"],
            "name": props["name"],
            "ref": props["ref"],
            "surface": props["surface"],
            "lanes": props["lanes"],
            "maxspeed": props["maxspeed"],
            "oneway": props["oneway"],
            "bridge": props["bridge"],
            "tunnel": props["tunnel"],
            "access": props["access"],
            "source": props["source"],
            "source_version": props["source_version"],
            "length_m": length_meters,
        }
        records_to_upsert.append(record)
        summary.total_road_length_km += length_meters / 1000.0

    # Execute chunked database upserts
    for i in range(0, len(records_to_upsert), chunk_size):
        chunk = records_to_upsert[i : i + chunk_size]
        if not chunk:
            continue

        stmt = insert(RoadFeature).values(chunk)
        # Update fields on conflict
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=["osm_id"],
            set_={
                "geometry": stmt.excluded.geometry,
                "highway_class": stmt.excluded.highway_class,
                "name": stmt.excluded.name,
                "ref": stmt.excluded.ref,
                "surface": stmt.excluded.surface,
                "lanes": stmt.excluded.lanes,
                "maxspeed": stmt.excluded.maxspeed,
                "oneway": stmt.excluded.oneway,
                "bridge": stmt.excluded.bridge,
                "tunnel": stmt.excluded.tunnel,
                "access": stmt.excluded.access,
                "source": stmt.excluded.source,
                "source_version": stmt.excluded.source_version,
                "length_m": stmt.excluded.length_m,
                "updated_at": stmt.excluded.updated_at,
            },
        )
        await session.execute(upsert_stmt)

    await session.commit()
    summary.successfully_ingested = len(records_to_upsert)
    summary.total_road_length_km = round(summary.total_road_length_km, 3)

    logger.info(
        f"OSM Ingestion Batch Completed: {summary.successfully_ingested} inserted/updated, "
        f"{summary.quarantined_invalid_geometry} quarantined, {summary.skipped_non_road} skipped."
    )
    return summary
