import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class RoadClassMetric(BaseModel):
    highway_class: str
    count: int
    length_km: float
    percentage_of_network: float


class AoiRoadStatistics(BaseModel):
    aoi_id: str
    aoi_surface_area_km2: float
    total_road_count: int
    total_road_length_km: float
    road_density_km_per_km2: float
    metrics_by_class: List[RoadClassMetric]
    authoritative_spheroid: str = Field(default="WGS84 PostGIS ST_Length(geom::geography)")
    attribution: str = Field(default="© OpenStreetMap contributors • ODbL 1.0")


async def calculate_aoi_road_statistics(
    session: AsyncSession,
    aoi_id: uuid.UUID,
) -> Optional[AoiRoadStatistics]:
    """
    Calculate authoritative geodesic road network metrics within an Area of Interest.
    Uses PostGIS spatial intersection and ellipsoidal geography length calculations.
    """
    query = text("""
    WITH
    target_aoi AS (
      SELECT id, geometry, surface_area_km2
      FROM workspace.areas_of_interest
      WHERE id = :aoi_id
    ),
    clipped_roads AS (
      SELECT
        r.highway_class,
        ST_Length(ST_Intersection(r.geometry, a.geometry)::geography) / 1000.0 AS length_km
      FROM geo.road_features r
      JOIN target_aoi a ON ST_Intersects(r.geometry, a.geometry)
    )
    SELECT
      (SELECT surface_area_km2 FROM target_aoi) AS aoi_area_km2,
      highway_class,
      COUNT(*) AS feature_count,
      COALESCE(SUM(length_km), 0.0) AS total_class_length_km
    FROM clipped_roads
    GROUP BY highway_class;
    """)

    result = await session.execute(query, {"aoi_id": aoi_id})
    rows = result.fetchall()

    if not rows:
        # Check if AOI exists with 0 roads
        aoi_check = await session.execute(
            text("SELECT id, surface_area_km2 FROM workspace.areas_of_interest WHERE id = :aoi_id"),
            {"aoi_id": aoi_id},
        )
        aoi_row = aoi_check.fetchone()
        if not aoi_row:
            return None

        aoi_area = float(aoi_row.surface_area_km2 or 0.0)
        return AoiRoadStatistics(
            aoi_id=str(aoi_id),
            aoi_surface_area_km2=aoi_area,
            total_road_count=0,
            total_road_length_km=0.0,
            road_density_km_per_km2=0.0,
            metrics_by_class=[],
        )

    aoi_area_km2 = float(rows[0].aoi_area_km2 or 1.0)
    total_length_km = sum(float(r.total_class_length_km) for r in rows)
    total_count = sum(int(r.feature_count) for r in rows)

    metrics_by_class: List[RoadClassMetric] = []
    for r in rows:
        class_len = float(r.total_class_length_km)
        pct = (class_len / total_length_km * 100.0) if total_length_km > 0 else 0.0
        metrics_by_class.append(
            RoadClassMetric(
                highway_class=r.highway_class,
                count=int(r.feature_count),
                length_km=round(class_len, 3),
                percentage_of_network=round(pct, 2),
            )
        )

    # Sort metrics descending by length
    metrics_by_class.sort(key=lambda m: m.length_km, reverse=True)

    density = (total_length_km / aoi_area_km2) if aoi_area_km2 > 0 else 0.0

    return AoiRoadStatistics(
        aoi_id=str(aoi_id),
        aoi_surface_area_km2=round(aoi_area_km2, 2),
        total_road_count=total_count,
        total_road_length_km=round(total_length_km, 3),
        road_density_km_per_km2=round(density, 4),
        metrics_by_class=metrics_by_class,
    )
