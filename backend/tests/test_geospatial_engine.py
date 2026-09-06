import math
import pytest
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
from shapely.validation import explain_validity
from geoalchemy2.elements import WKTElement, WKBElement
from geoalchemy2.shape import from_shape, to_shape


def test_shapely_to_geoalchemy_conversion():
    """Verify that Shapely geometry converts accurately to GeoAlchemy2 WKT/WKB elements."""
    poly = Polygon([
        (-55.0, -12.0),
        (-54.0, -12.0),
        (-54.0, -11.0),
        (-55.0, -11.0),
        (-55.0, -12.0),
    ])
    multi_poly = MultiPolygon([poly])
    
    wkb_elem = from_shape(multi_poly, srid=4326)
    assert wkb_elem.srid == 4326
    
    recovered_geom = to_shape(wkb_elem)
    assert recovered_geom.geom_type == "MultiPolygon"
    assert len(recovered_geom.geoms) == 1
    assert recovered_geom.geoms[0].is_valid


def test_road_line_intersection_with_aoi_polygon():
    """Verify spatial intersection testing between a road LineString and an AOI Polygon."""
    aoi_box = box(-55.0, -12.0, -54.0, -11.0)
    
    # Road that crosses the AOI
    intersecting_road = LineString([(-56.0, -11.5), (-53.0, -11.5)])
    assert aoi_box.intersects(intersecting_road) is True
    
    intersection = aoi_box.intersection(intersecting_road)
    assert intersection.geom_type == "LineString"
    assert intersection.bounds == (-55.0, -11.5, -54.0, -11.5)
    
    # Road outside the AOI
    non_intersecting_road = LineString([(-56.0, -10.0), (-53.0, -10.0)])
    assert aoi_box.intersects(non_intersecting_road) is False


def test_geometry_validity_and_repair():
    """Verify that invalid self-intersecting geometries (e.g. bowtie polygons) are flagged."""
    # Self-intersecting bowtie polygon
    bowtie_coords = [(-55.0, -12.0), (-54.0, -11.0), (-54.0, -12.0), (-55.0, -11.0), (-55.0, -12.0)]
    invalid_poly = Polygon(bowtie_coords)
    assert invalid_poly.is_valid is False
    assert "Self-intersection" in explain_validity(invalid_poly)
    
    # Valid convex polygon
    valid_coords = [(-55.0, -12.0), (-54.0, -12.0), (-54.0, -11.0), (-55.0, -11.0), (-55.0, -12.0)]
    valid_poly = Polygon(valid_coords)
    assert valid_poly.is_valid is True


def test_geodesic_area_calculation_precision():
    """
    Verify the fundamental mathematical distortion of Mercator/planar degrees
    vs. ellipsoidal spherical surface calculations on WGS84.
    """
    # 1 degree x 1 degree square at Equator (lat 0 to 1, lon 0 to 1)
    # True geodesic area on WGS84 ~ 12,308 km2
    # At 60 deg North (lat 60 to 61, lon 0 to 1), true area is ~ 6,170 km2 (half as wide due to cos(60) = 0.5)
    
    def calculate_spherical_area_km2(min_lon, min_lat, max_lon, max_lat):
        R = 6371.0  # Earth mean radius in km
        d_lon_rad = math.radians(max_lon - min_lon)
        sin_lat_diff = math.sin(math.radians(max_lat)) - math.sin(math.radians(min_lat))
        return (R ** 2) * d_lon_rad * sin_lat_diff

    equator_area = calculate_spherical_area_km2(0.0, 0.0, 1.0, 1.0)
    high_lat_area = calculate_spherical_area_km2(0.0, 60.0, 1.0, 61.0)
    
    assert 12200 < equator_area < 12400
    assert 6000 < high_lat_area < 6200
    
    # The high latitude area must be approximately 50% of the equatorial area
    ratio = high_lat_area / equator_area
    assert 0.49 < ratio < 0.51
