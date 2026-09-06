from typing import Any, Dict, List, Optional
from shapely.geometry import shape, Point, LineString, Polygon, MultiPolygon
from app.services.intelligence.models import SpatialContextResult


class SpatialCorrelator:
    """
    Deterministic spatial correlation engine evaluating geometric predicates and infrastructure proximity.
    """

    @classmethod
    def evaluate_road_proximity(
        cls,
        target_geometry: Dict[str, Any],
        road_features: Optional[List[Dict[str, Any]]] = None,
        corridor_buffer_m: float = 500.0,
    ) -> SpatialContextResult:
        """
        Calculates distance to closest road feature and tests corridor intersection.
        """
        if not road_features:
            return SpatialContextResult(
                nearby_roads_count=0,
                closest_road_name=None,
                closest_road_class=None,
                distance_to_closest_road_m=None,
                intersects_road_corridor=False,
                road_corridor_buffer_m=corridor_buffer_m,
                spatial_relationship="DISJOINT",
            )

        geom = shape(target_geometry)

        min_dist_m = float("inf")
        closest_name = None
        closest_class = None
        nearby_count = 0
        intersects_corridor = False

        # Conversion factor for lat/lon deg to approx meters at mid-latitudes
        # ~111,320m per degree lat
        for r_feat in road_features:
            r_geom = shape(r_feat.get("geometry", {}))
            props = r_feat.get("properties", {})
            name = props.get("name") or props.get("ref") or "Unclassified Road"
            h_class = props.get("highway_class", "unclassified")

            # Degree distance
            deg_dist = geom.distance(r_geom)
            approx_dist_m = deg_dist * 111320.0

            if approx_dist_m < min_dist_m:
                min_dist_m = approx_dist_m
                closest_name = name
                closest_class = h_class

            if approx_dist_m <= corridor_buffer_m:
                nearby_count += 1
                intersects_corridor = True

        rel = "INTERSECTS_CORRIDOR" if intersects_corridor else "NEAR" if min_dist_m <= 2000.0 else "DISJOINT"

        return SpatialContextResult(
            nearby_roads_count=nearby_count,
            closest_road_name=closest_name,
            closest_road_class=closest_class,
            distance_to_closest_road_m=round(min_dist_m, 1) if min_dist_m != float("inf") else None,
            intersects_road_corridor=intersects_corridor,
            road_corridor_buffer_m=corridor_buffer_m,
            spatial_relationship=rel,
        )

    @classmethod
    def calculate_spatial_overlap_percentage(
        cls,
        geom_a_dict: Dict[str, Any],
        geom_b_dict: Dict[str, Any],
    ) -> float:
        """
        Calculates area of intersection divided by area of Geom A.
        """
        geom_a = shape(geom_a_dict)
        geom_b = shape(geom_b_dict)

        if geom_a.area == 0:
            return 0.0

        intersection_area = geom_a.intersection(geom_b).area
        return round((intersection_area / geom_a.area) * 100.0, 2)
