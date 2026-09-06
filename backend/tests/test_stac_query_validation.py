from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from app.services.eo.stac.models import STACSearchRequest


def test_valid_stac_search_request():
    req = STACSearchRequest(
        collections=["sentinel-2-l2a"],
        bbox=[-55.4, -12.1, -54.1, -10.9],
        datetime_start=datetime(2026, 1, 1, tzinfo=timezone.utc),
        datetime_end=datetime(2026, 8, 1, tzinfo=timezone.utc),
        cloud_cover_max=30.0,
        limit=25,
    )
    assert req.collections == ["sentinel-2-l2a"]
    assert req.cloud_cover_max == 30.0
    assert req.limit == 25


def test_invalid_bbox_coordinates():
    # Longitude > 180
    with pytest.raises(ValidationError):
        STACSearchRequest(bbox=[-185.0, -10.0, 50.0, 10.0])

    # Latitude > 90
    with pytest.raises(ValidationError):
        STACSearchRequest(bbox=[-50.0, -10.0, 50.0, 95.0])

    # min_lon > max_lon
    with pytest.raises(ValidationError):
        STACSearchRequest(bbox=[50.0, -10.0, -50.0, 10.0])

    # Length != 4
    with pytest.raises(ValidationError):
        STACSearchRequest(bbox=[-50.0, -10.0, 50.0])


def test_invalid_datetime_range():
    # start > end
    with pytest.raises(ValidationError):
        STACSearchRequest(
            datetime_start=datetime(2026, 8, 1, tzinfo=timezone.utc),
            datetime_end=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )


def test_invalid_cloud_cover():
    # Cloud cover < 0
    with pytest.raises(ValidationError):
        STACSearchRequest(cloud_cover_max=-5.0)

    # Cloud cover > 100
    with pytest.raises(ValidationError):
        STACSearchRequest(cloud_cover_max=105.0)


def test_limit_bounds():
    # Limit < 1
    with pytest.raises(ValidationError):
        STACSearchRequest(limit=0)

    # Limit > 100
    with pytest.raises(ValidationError):
        STACSearchRequest(limit=150)
