import math
from typing import List, Optional, Tuple, Union
from shapely.geometry import LineString, MultiLineString, Point
from shapely.validation import make_valid
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import from_shape, to_shape


WGS84_EARTH_RADIUS_METERS = 6371008.8  # IUGG standard mean Earth radius


def haversine_distance_meters(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate the great circle distance in meters between two points on the WGS84 spheroid.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return WGS84_EARTH_RADIUS_METERS * c


def calculate_geodesic_length_meters(geom: Union[LineString, MultiLineString]) -> float:
    """
    Calculate the true geodesic length in meters for a LineString or MultiLineString geometry
    defined in WGS84 decimal degrees (EPSG:4326).
    """
    total_length = 0.0
    if isinstance(geom, LineString):
        coords = list(geom.coords)
        for i in range(len(coords) - 1):
            lon1, lat1 = coords[i][:2]
            lon2, lat2 = coords[i + 1][:2]
            total_length += haversine_distance_meters(lon1, lat1, lon2, lat2)
    elif isinstance(geom, MultiLineString):
        for line in geom.geoms:
            total_length += calculate_geodesic_length_meters(line)
    return total_length


def sanitize_and_repair_linestring(
    coordinates: List[Tuple[float, float]]
) -> Optional[LineString]:
    """
    Validate, clean, and repair an ordered list of (longitude, latitude) coordinates
    into a valid 2D WGS84 LineString.

    Rules:
    1. Removes consecutive duplicate coordinates.
    2. Enforces valid WGS84 coordinate bounds: -180 <= lon <= 180, -90 <= lat <= 90.
    3. Rejects non-numeric, NaN, or infinite coordinates.
    4. Must contain at least 2 distinct points.
    5. Applies topological repair via shapely.make_valid if needed.
    """
    if not coordinates or len(coordinates) < 2:
        return None

    cleaned_coords: List[Tuple[float, float]] = []
    for pt in coordinates:
        if not pt or len(pt) < 2:
            continue
        lon, lat = float(pt[0]), float(pt[1])

        # Validate finiteness and coordinate ranges
        if not (math.isfinite(lon) and math.isfinite(lat)):
            continue
        if not (-180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0):
            continue

        # Filter sequential duplicate points
        if not cleaned_coords or (cleaned_coords[-1][0] != lon or cleaned_coords[-1][1] != lat):
            cleaned_coords.append((lon, lat))

    if len(cleaned_coords) < 2:
        return None

    raw_line = LineString(cleaned_coords)
    if raw_line.is_valid and not raw_line.is_empty:
        return raw_line

    # Attempt geometry repair
    repaired = make_valid(raw_line)
    if repaired.is_empty:
        return None

    if isinstance(repaired, LineString):
        return repaired
    elif isinstance(repaired, MultiLineString):
        # Extract longest contiguous constituent line segment
        longest_line = max(repaired.geoms, key=lambda l: l.length)
        if len(longest_line.coords) >= 2:
            return longest_line

    return None


def create_road_geometry_element(line: LineString) -> WKBElement:
    """
    Convert a validated Shapely LineString into a GeoAlchemy2 WKBElement with canonical SRID 4326.
    """
    return from_shape(line, srid=4326)
