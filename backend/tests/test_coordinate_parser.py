import pytest
from app.services.geo.coordinate_parser import parse_coordinate_query


def test_parse_decimal_coordinate_pairs():
    # Standard comma separated
    res = parse_coordinate_query("31.5204, 74.3587")
    assert res is not None
    assert res.latitude == 31.5204
    assert res.longitude == 74.3587
    assert "31.5204° N, 74.3587° E" in res.formatted_coordinate

    # Space separated
    res2 = parse_coordinate_query("-12.1 54.78")
    assert res2 is not None
    assert res2.latitude == -12.1
    assert res2.longitude == 54.78
    assert "12.1000° S, 54.7800° E" in res2.formatted_coordinate


def test_parse_cardinal_coordinates():
    res = parse_coordinate_query("31.5204 N, 74.3587 E")
    assert res is not None
    assert res.latitude == 31.5204
    assert res.longitude == 74.3587

    res_south = parse_coordinate_query("12.1 S, 54.78 W")
    assert res_south is not None
    assert res_south.latitude == -12.1
    assert res_south.longitude == -54.78


def test_parse_labeled_coordinates():
    res = parse_coordinate_query("lat: 31.5204, lon: 74.3587")
    assert res is not None
    assert res.latitude == 31.5204
    assert res.longitude == 74.3587

    res_lng = parse_coordinate_query("latitude: -11.52, longitude: -54.75")
    assert res_lng is not None
    assert res_lng.latitude == -11.52
    assert res_lng.longitude == -54.75


def test_reject_invalid_coordinate_ranges():
    # Latitude > 90
    assert parse_coordinate_query("95.0, 74.3587") is None
    # Latitude < -90
    assert parse_coordinate_query("-91.0, 74.3587") is None
    # Longitude > 180
    assert parse_coordinate_query("31.5204, 185.0") is None
    # Longitude < -180
    assert parse_coordinate_query("31.5204, -185.0") is None


def test_reject_arbitrary_text_queries():
    assert parse_coordinate_query("Lahore") is None
    assert parse_coordinate_query("Highway BR-163") is None
    assert parse_coordinate_query("") is None
    assert parse_coordinate_query("   ") is None
