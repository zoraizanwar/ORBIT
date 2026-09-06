import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.geo.vector_tiles import (
    validate_tile_coordinates,
    generate_road_vector_tile,
)
from app.services.geo.road_statistics import (
    calculate_aoi_road_statistics,
    AoiRoadStatistics,
)
from app.services.geo.osm_ingestion import (
    ingest_osm_road_batch,
    OsmFeaturePayload,
    IngestionSummary,
)
from app.services.geo.gazetteer_search import (
    search_geographic_entities,
    get_gazetteer_entity_by_id,
    reverse_geocode_lookup,
    SearchResponse,
    SearchResultItem,
    GazetteerEntityDetail,
)

router = APIRouter(prefix="/geo", tags=["Geospatial & Road Network"])


# =============================================================================
# 1. Global Gazetteer & Spatial Search Endpoints (Phase 7)
# =============================================================================

@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Global Gazetteer & Spatial Search Engine",
    description="Unified search resolving places, administrative regions, roads, AOIs, projects, and raw coordinates.",
)
async def search_locations(
    q: str = Query(..., min_length=1, description="Search query string or coordinate pair"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results to return"),
    entity_type: Optional[str] = Query(None, description="Filter by GeographicEntityType (e.g. CITY, COUNTRY, ROAD)"),
    country_code: Optional[str] = Query(None, description="Filter by ISO 3166-1 country code (e.g. PK, BR, US)"),
    bbox: Optional[str] = Query(
        None,
        description="Filter within bounding box (min_lng,min_lat,max_lng,max_lat)",
    ),
    session: AsyncSession = Depends(get_db),
) -> SearchResponse:
    parsed_bbox = None
    if bbox:
        try:
            parts = [float(p.strip()) for p in bbox.split(",")]
            if len(parts) == 4:
                parsed_bbox = parts
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bbox format. Expected 'min_lng,min_lat,max_lng,max_lat'",
            )

    return await search_geographic_entities(
        session=session,
        query=q,
        limit=limit,
        entity_type=entity_type,
        country_code=country_code,
        bbox=parsed_bbox,
    )


@router.get(
    "/entities/{entity_id}",
    response_model=GazetteerEntityDetail,
    summary="Get Resolved Gazetteer Entity Detail",
    description="Fetches full properties, geometry GeoJSON, and metadata for a resolved gazetteer entity.",
)
async def get_entity_detail(
    entity_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> GazetteerEntityDetail:
    detail = await get_gazetteer_entity_by_id(session, entity_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gazetteer entity with ID {entity_id} was not found",
        )
    return detail


@router.get(
    "/reverse",
    response_model=List[SearchResultItem],
    summary="Local Spatial Reverse Geocoder",
    description="Finds nearest geographic entities around a coordinate using PostGIS spheroid distance.",
)
async def reverse_geocode(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude in EPSG:4326"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude in EPSG:4326"),
    radius_km: float = Query(10.0, ge=0.1, le=100.0, description="Search radius in kilometers"),
    limit: int = Query(5, ge=1, le=20, description="Maximum results"),
    session: AsyncSession = Depends(get_db),
) -> List[SearchResultItem]:
    return await reverse_geocode_lookup(
        session=session,
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        limit=limit,
    )


# =============================================================================
# 2. Dynamic Vector Tile Endpoint (Phase 6)
# =============================================================================

@router.get(
    "/tiles/roads/{z}/{x}/{y}.pbf",
    summary="Dynamic Mapbox Vector Tile (MVT) Road Network",
    description="Returns PostGIS ST_AsMVT road vector tiles dynamically clipped for tile (z, x, y).",
    response_class=Response,
    responses={
        200: {
            "content": {"application/vnd.mapbox-vector-tile": {}},
            "description": "Binary Mapbox Vector Tile Protobuf",
        },
        204: {"description": "Tile contains no road features for current zoom level and bounding box."},
        400: {"description": "Invalid tile coordinates."},
    },
)
async def get_road_vector_tile(
    z: int,
    x: int,
    y: int,
    session: AsyncSession = Depends(get_db),
) -> Response:
    valid, err_msg = validate_tile_coordinates(z, x, y)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg,
        )

    try:
        tile_bytes = await generate_road_vector_tile(session, z, x, y)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate road vector tile: {type(e).__name__}: {e}",
        ) from e

    if not tile_bytes or len(tile_bytes) == 0:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return Response(
        content=tile_bytes,
        status_code=status.HTTP_200_OK,
        media_type="application/vnd.mapbox-vector-tile",
        headers={
            "Cache-Control": "public, max-age=3600, stale-while-revalidate=86400",
            "Content-Type": "application/vnd.mapbox-vector-tile",
        },
    )


# =============================================================================
# 3. AOI Road Statistics & Batch Ingestion Endpoints (Phase 6)
# =============================================================================

@router.get(
    "/roads/stats/{aoi_id}",
    response_model=AoiRoadStatistics,
    summary="Authoritative AOI Road Statistics",
    description="Calculates geodesic road lengths, class breakdowns, and density (km/km²) for a given AOI.",
)
async def get_aoi_road_statistics(
    aoi_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> AoiRoadStatistics:
    stats = await calculate_aoi_road_statistics(session, aoi_id)
    if stats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Area of Interest with ID {aoi_id} was not found",
        )
    return stats


@router.post(
    "/roads/ingest",
    response_model=IngestionSummary,
    summary="Ingest OpenStreetMap Road Batch",
    description="Streamingly ingests and normalizes OSM road features into geo.road_features with geometry repair.",
)
async def ingest_roads(
    payload: List[OsmFeaturePayload],
    session: AsyncSession = Depends(get_db),
) -> IngestionSummary:
    if not payload:
        return IngestionSummary()
    return await ingest_osm_road_batch(session, payload)
