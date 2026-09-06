import math
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from shapely.geometry import shape, mapping
from shapely.validation import explain_validity
from app.services.eo.operational.models import OperationalAOIResponse


class OperationalAOIService:
    """
    Operational Area of Interest (AOI) Validation and Geodesic Management Service.
    Enforces WGS84 (EPSG:4326), valid closed polygons, bounding box containment,
    and geodesic surface area calculation using latitude cosine scaling.
    """

    # In-memory store for workstation sessions
    _sessions: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def validate_and_create_aoi(
        cls,
        name: str,
        geometry: Dict[str, Any],
        aoi_id: Optional[str] = None,
    ) -> OperationalAOIResponse:
        """
        Validates GeoJSON geometry structure, coordinates, non-degeneracy, and builds an AOI session.
        """
        if not geometry or not isinstance(geometry, dict):
            raise ValueError("Invalid AOI: Geometry must be a valid GeoJSON dictionary.")

        geom_type = geometry.get("type")
        if geom_type not in ["Polygon", "MultiPolygon"]:
            raise ValueError(f"Invalid AOI geometry type: '{geom_type}'. Must be 'Polygon' or 'MultiPolygon'.")

        coordinates = geometry.get("coordinates")
        if not coordinates or not isinstance(coordinates, list):
            raise ValueError("Invalid AOI: Coordinates array is empty or malformed.")

        try:
            shapely_geom = shape(geometry)
        except Exception as e:
            raise ValueError(f"Pathological or unparseable GeoJSON geometry: {str(e)}")

        if not shapely_geom.is_valid:
            reason = explain_validity(shapely_geom)
            # Attempt repair via buffer(0)
            repaired = shapely_geom.buffer(0)
            if not repaired.is_valid or repaired.is_empty:
                raise ValueError(f"Geometry invalid and unrepairable: {reason}")
            shapely_geom = repaired

        bounds = shapely_geom.bounds  # (minx, miny, maxx, maxy)
        min_lon, min_lat, max_lon, max_lat = bounds

        # Enforce WGS84 coordinate bounds
        if not (-180.0 <= min_lon <= 180.0 and -180.0 <= max_lon <= 180.0 and
                -90.0 <= min_lat <= 90.0 and -90.0 <= max_lat <= 90.0):
            raise ValueError(f"AOI bounds outside valid EPSG:4326 range: {bounds}")

        if min_lon == max_lon or min_lat == max_lat:
            raise ValueError(f"Degenerate zero-area bounding box: {bounds}")

        # Compute geodesic area (km²) using cosine latitude projection
        center_lat = (min_lat + max_lat) / 2.0
        lat_rad = math.radians(center_lat)
        deg_lat_km = 111.132
        deg_lon_km = 111.320 * math.cos(lat_rad)
        
        # Approximate geodesic area
        area_km2 = float(shapely_geom.area * deg_lat_km * deg_lon_km)
        area_km2 = max(0.001, round(area_km2, 4))

        session_id = aoi_id or str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        aoi_data = {
            "id": session_id,
            "name": name.strip(),
            "geometry": mapping(shapely_geom),
            "bbox": [float(min_lon), float(min_lat), float(max_lon), float(max_lat)],
            "area_km2": area_km2,
            "is_valid": True,
            "validation_message": "Valid WGS84 Polygon.",
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        cls._sessions[session_id] = aoi_data
        return OperationalAOIResponse(**aoi_data)

    @classmethod
    def get_aoi(cls, aoi_id: str) -> Optional[OperationalAOIResponse]:
        """Retrieves an active AOI session by ID."""
        data = cls._sessions.get(aoi_id)
        if not data:
            return None
        return OperationalAOIResponse(**data)
