import pytest
from app.services.geo.vector_tiles import (
    validate_tile_coordinates,
    get_zoom_highway_classes,
    build_vector_tile_query,
)


def test_validate_tile_coordinates():
    # Valid global overview tile (Z=0, X=0, Y=0)
    assert validate_tile_coordinates(0, 0, 0) == (True, None)

    # Valid regional tile at Z=10
    assert validate_tile_coordinates(10, 512, 512) == (True, None)

    # Negative zoom
    valid, err = validate_tile_coordinates(-1, 0, 0)
    assert not valid
    assert "out of bounds" in err

    # Out of bounds zoom (> 22)
    valid, err = validate_tile_coordinates(23, 0, 0)
    assert not valid
    assert "out of bounds" in err

    # Out of bounds X for Z=2 (max index is 3)
    valid, err = validate_tile_coordinates(2, 4, 1)
    assert not valid
    assert "out of bounds" in err


def test_get_zoom_highway_classes_lod_hierarchy():
    # Z <= 5: Continental only
    z2_classes = get_zoom_highway_classes(2)
    assert "motorway" in z2_classes
    assert "trunk" in z2_classes
    assert "track" not in z2_classes
    assert "residential" not in z2_classes

    # Z = 8: Primary corridors
    z8_classes = get_zoom_highway_classes(8)
    assert "primary" in z8_classes
    assert "tertiary" not in z8_classes

    # Z = 10: Secondary & Tertiary
    z10_classes = get_zoom_highway_classes(10)
    assert "secondary" in z10_classes
    assert "tertiary" in z10_classes

    # Z = 14: All local and unpaved tracks
    z15_classes = get_zoom_highway_classes(15)
    assert "residential" in z15_classes
    assert "track" in z15_classes
    assert "path" in z15_classes


def test_build_vector_tile_query():
    query_str, params = build_vector_tile_query(z=8, x=120, y=140)
    assert "ST_TileEnvelope(:z, :x, :y)" in query_str
    assert "ST_AsMVTGeom" in query_str
    assert "ST_AsMVT" in query_str
    assert "geo.road_features" in query_str
    assert params["z"] == 8
    assert params["x"] == 120
    assert params["y"] == 140
