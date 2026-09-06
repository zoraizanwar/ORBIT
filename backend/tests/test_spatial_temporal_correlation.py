from datetime import datetime, timezone
import pytest
from app.services.intelligence.exceptions import TemporalCorrelationError
from app.services.intelligence.spatial_correlator import SpatialCorrelator
from app.services.intelligence.temporal_correlator import TemporalCorrelator


def test_spatial_correlator_road_proximity():
    # Polygon around (-54.75, -11.52)
    target_geom = {
        "type": "Polygon",
        "coordinates": [
            [
                [-54.76, -11.53],
                [-54.74, -11.53],
                [-54.74, -11.51],
                [-54.76, -11.51],
                [-54.76, -11.53],
            ]
        ],
    }

    road_features = [
        {
            "properties": {
                "name": "Highway BR-163",
                "ref": "BR-163",
                "highway_class": "primary",
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [[-54.75, -12.0], [-54.75, -11.0]],
            },
        }
    ]

    res = SpatialCorrelator.evaluate_road_proximity(
        target_geometry=target_geom,
        road_features=road_features,
        corridor_buffer_m=500.0,
    )

    assert res.intersects_road_corridor is True
    assert res.closest_road_name == "Highway BR-163"
    assert res.closest_road_class == "primary"
    assert res.distance_to_closest_road_m == 0.0  # intersects linestring


def test_spatial_overlap_percentage():
    geom_a = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]],
    }
    # 50% overlap
    geom_b = {
        "type": "Polygon",
        "coordinates": [[[5, 0], [15, 0], [15, 10], [5, 10], [5, 0]]],
    }

    overlap = SpatialCorrelator.calculate_spatial_overlap_percentage(geom_a, geom_b)
    assert overlap == 50.0


def test_temporal_correlator_ordering_and_tolerance():
    t1 = datetime(2023, 7, 15, tzinfo=timezone.utc)
    t2 = datetime(2026, 7, 18, tzinfo=timezone.utc)

    # Valid interval
    res = TemporalCorrelator.evaluate_temporal_alignment(t1, t2)
    assert res.interval_days == 1099
    assert res.temporal_alignment == "AUTHORITATIVE_INTERVAL"

    # Start >= End violation
    with pytest.raises(TemporalCorrelationError):
        TemporalCorrelator.evaluate_temporal_alignment(t2, t1)
