import pytest
from app.services.geo.road_normalization import (
    normalize_highway_class,
    normalize_surface,
    parse_lane_count,
    parse_speed_limit,
    parse_boolean_tag,
    normalize_osm_road_properties,
)


def test_normalize_highway_class_hierarchy():
    assert normalize_highway_class("motorway") == "motorway"
    assert normalize_highway_class("motorway_link") == "motorway"
    assert normalize_highway_class("trunk") == "trunk"
    assert normalize_highway_class("primary") == "primary"
    assert normalize_highway_class("secondary") == "secondary"
    assert normalize_highway_class("tertiary") == "tertiary"
    assert normalize_highway_class("residential") == "residential"
    assert normalize_highway_class("living_street") == "residential"
    assert normalize_highway_class("service") == "service"
    assert normalize_highway_class("track") == "track"
    assert normalize_highway_class("path") == "path"
    assert normalize_highway_class("unknown_tag") == "unclassified"
    assert normalize_highway_class(None) is None


def test_normalize_surface_types():
    assert normalize_surface("asphalt") == "paved"
    assert normalize_surface("concrete") == "paved"
    assert normalize_surface("gravel") == "unpaved"
    assert normalize_surface("dirt") == "ground"
    assert normalize_surface("earth") == "ground"
    # Default inferences based on highway class
    assert normalize_surface(None, highway_class="motorway") == "paved"
    assert normalize_surface(None, highway_class="track") == "ground"


def test_parse_lane_count():
    assert parse_lane_count(2) == 2
    assert parse_lane_count("4") == 4
    assert parse_lane_count("2;3") == 2
    assert parse_lane_count("2|1") == 2
    assert parse_lane_count(None, default_lanes=1) == 1
    assert parse_lane_count("invalid_str", default_lanes=1) == 1


def test_parse_speed_limit():
    assert parse_speed_limit(110) == 110
    assert parse_speed_limit("80") == 80
    assert parse_speed_limit("60 km/h") == 60
    assert parse_speed_limit("50 mph") == 80  # 50 * 1.60934 ~ 80 km/h
    assert parse_speed_limit(None) is None
    assert parse_speed_limit("variable") is None


def test_parse_boolean_flags():
    assert parse_boolean_tag("yes") is True
    assert parse_boolean_tag("true") is True
    assert parse_boolean_tag("1") is True
    assert parse_boolean_tag("no") is False
    assert parse_boolean_tag("false") is False
    assert parse_boolean_tag(None) is False


def test_normalize_osm_road_properties_complete():
    raw_tags = {
        "highway": "primary",
        "name": "Rodovia Transamazonica",
        "ref": "BR-230",
        "surface": "asphalt",
        "lanes": "2",
        "maxspeed": "80",
        "oneway": "no",
        "bridge": "yes",
        "tunnel": "no",
        "access": "yes",
        "version": "14",
    }
    props = normalize_osm_road_properties(raw_tags)
    assert props["highway_class"] == "primary"
    assert props["name"] == "Rodovia Transamazonica"
    assert props["ref"] == "BR-230"
    assert props["surface"] == "paved"
    assert props["lanes"] == 2
    assert props["maxspeed"] == 80
    assert props["oneway"] is False
    assert props["bridge"] is True
    assert props["tunnel"] is False
    assert props["source"] == "OpenStreetMap"
