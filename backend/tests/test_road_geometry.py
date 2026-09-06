import math
import pytest
from shapely.geometry import LineString, MultiLineString
from app.services.geo.road_geometry import (
    haversine_distance_meters,
    calculate_geodesic_length_meters,
    sanitize_and_repair_linestring,
    create_road_geometry_element,
)


def test_haversine_distance_calculation():
    # 1 degree of latitude is approximately 111.139 km
    dist = haversine_distance_meters(0.0, 0.0, 0.0, 1.0)
    assert 111000 < dist < 111500

    # Distance between identical points is 0
    zero_dist = haversine_distance_meters(-54.78, -11.52, -54.78, -11.52)
    assert zero_dist == 0.0


def test_calculate_geodesic_length_meters():
    line = LineString([(-54.78, -12.1), (-54.76, -11.8), (-54.75, -11.52)])
    length_m = calculate_geodesic_length_meters(line)
    assert length_m > 60000  # ~64 km

    multi_line = MultiLineString([line, line])
    multi_length_m = calculate_geodesic_length_meters(multi_line)
    assert math.isclose(multi_length_m, length_m * 2, rel_tol=1e-5)


def test_sanitize_and_repair_linestring():
    # Valid coordinates
    valid_coords = [(-54.78, -12.1), (-54.76, -11.8), (-54.75, -11.52)]
    repaired = sanitize_and_repair_linestring(valid_coords)
    assert repaired is not None
    assert repaired.is_valid
    assert len(repaired.coords) == 3

    # Coordinates with consecutive duplicates
    dup_coords = [(-54.78, -12.1), (-54.78, -12.1), (-54.76, -11.8)]
    deduped = sanitize_and_repair_linestring(dup_coords)
    assert deduped is not None
    assert len(deduped.coords) == 2

    # Coordinates with out-of-bounds latitude
    invalid_bounds = [(-54.78, -12.1), (-54.76, 95.0), (-54.75, -11.52)]
    filtered = sanitize_and_repair_linestring(invalid_bounds)
    assert filtered is not None
    assert len(filtered.coords) == 2

    # Insufficient coordinates
    insufficient = [(-54.78, -12.1)]
    assert sanitize_and_repair_linestring(insufficient) is None


def test_create_road_geometry_element():
    line = LineString([(-54.78, -12.1), (-54.75, -11.52)])
    wkb_elem = create_road_geometry_element(line)
    assert wkb_elem.srid == 4326
