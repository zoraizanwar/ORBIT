from typing import List, Optional, Tuple
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def validate_tile_coordinates(z: int, x: int, y: int) -> Tuple[bool, Optional[str]]:
    """
    Validate vector tile coordinates (z, x, y) against standard Web Mercator quadtree bounds.
    """
    if z < 0 or z > 22:
        return False, f"Zoom level z={z} out of bounds [0, 22]"
    max_index = (1 << z) - 1
    if x < 0 or x > max_index:
        return False, f"Tile coordinate x={x} out of bounds [0, {max_index}] at zoom {z}"
    if y < 0 or y > max_index:
        return False, f"Tile coordinate y={y} out of bounds [0, {max_index}] at zoom {z}"
    return True, None


def get_zoom_highway_classes(zoom: int) -> List[str]:
    """
    Determine progressive Level of Detail (LoD) highway classes based on zoom level.
    """
    if zoom <= 5:
        # Continental / National Corridors
        return ["motorway", "trunk"]
    elif zoom <= 8:
        # Regional & Major Highways
        return ["motorway", "trunk", "primary"]
    elif zoom <= 11:
        # Primary, Secondary & Major Agricultural Corridors
        return ["motorway", "trunk", "primary", "secondary", "tertiary"]
    elif zoom <= 13:
        # Urban & Rural Settlement Networks
        return [
            "motorway",
            "trunk",
            "primary",
            "secondary",
            "tertiary",
            "unclassified",
            "residential",
            "service",
        ]
    else:
        # High Resolution: Full Infrastructure (including tracks and spurs)
        return [
            "motorway",
            "trunk",
            "primary",
            "secondary",
            "tertiary",
            "unclassified",
            "residential",
            "service",
            "track",
            "path",
        ]


def build_vector_tile_query(z: int, x: int, y: int) -> Tuple[str, dict]:
    """
    Construct optimized PostGIS ST_AsMVT parameterized SQL query for road vector tiles.
    """
    classes = get_zoom_highway_classes(z)
    
    # Format classes tuple for SQL IN clause
    classes_placeholders = ", ".join([f":cls_{i}" for i in range(len(classes))])
    params = {
        "z": z,
        "x": x,
        "y": y,
    }
    for i, cls_name in enumerate(classes):
        params[f"cls_{i}"] = cls_name

    query_str = f"""
    WITH
    bounds AS (
      SELECT
        ST_TileEnvelope(:z, :x, :y) AS geom_3857,
        ST_Transform(ST_TileEnvelope(:z, :x, :y), 4326) AS geom_4326
    ),
    mvtgeom AS (
      SELECT
        ST_AsMVTGeom(
          ST_Transform(r.geometry, 3857),
          bounds.geom_3857,
          4096,
          64,
          true
        ) AS geom,
        r.id::text AS id,
        r.osm_id,
        r.highway_class,
        r.name,
        r.ref,
        r.surface,
        r.lanes,
        r.bridge,
        r.tunnel,
        r.access,
        'OpenStreetMap' AS source
      FROM geo.road_features r, bounds
      WHERE r.geometry && bounds.geom_4326
        AND ST_Intersects(r.geometry, bounds.geom_4326)
        AND r.highway_class IN ({classes_placeholders})
    )
    SELECT ST_AsMVT(mvtgeom.*, 'roads', 4096, 'geom', 'id') AS mvt FROM mvtgeom;
    """
    return query_str, params


async def generate_road_vector_tile(
    session: AsyncSession,
    z: int,
    x: int,
    y: int,
) -> Optional[bytes]:
    """
    Fetch dynamically rendered MVT binary protobuf bytes from PostGIS for tile (z, x, y).
    """
    valid, err = validate_tile_coordinates(z, x, y)
    if not valid:
        raise ValueError(err)

    query_str, params = build_vector_tile_query(z, x, y)
    result = await session.execute(text(query_str), params)
    raw_tile = result.scalar_one_or_none()

    if raw_tile is None:
        return b""

    # asyncpg / postgres returns bytes or memoryview
    if isinstance(raw_tile, memoryview):
        return raw_tile.tobytes()
    elif isinstance(raw_tile, bytes):
        return raw_tile
    return bytes(raw_tile)
