import os
import tempfile
from unittest.mock import patch
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def synthetic_scene_bands():
    """
    Creates temporary synthetic Red, Green, NIR, and SWIR GeoTIFFs for endpoint testing.
    """
    temp_dir = tempfile.mkdtemp()
    transform = from_origin(-55.0, -11.0, 0.01, 0.01)

    bands = {
        "B02": os.path.join(temp_dir, "B02.tif"),
        "B03": os.path.join(temp_dir, "B03.tif"),
        "B04": os.path.join(temp_dir, "B04.tif"),
        "B08": os.path.join(temp_dir, "B08.tif"),
        "B11": os.path.join(temp_dir, "B11.tif"),
    }

    # B02 (Blue): 1000, B03 (Green): 1500, B04 (Red): 1000, B08 (NIR): 4000, B11 (SWIR): 2000
    band_values = {"B02": 1000, "B03": 1500, "B04": 1000, "B08": 4000, "B11": 2000}

    for key, path in bands.items():
        val = band_values[key]
        data = np.full((50, 50), val, dtype=np.uint16)
        with rasterio.open(
            path,
            "w",
            driver="GTiff",
            height=50,
            width=50,
            count=1,
            dtype=np.uint16,
            crs="EPSG:4326",
            transform=transform,
            nodata=0,
        ) as dst:
            dst.write(data, 1)

    yield bands

    for path in bands.values():
        if os.path.exists(path):
            os.remove(path)
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)


@pytest.mark.asyncio
async def test_inspect_raster_endpoint(synthetic_scene_bands):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"source_uri": synthetic_scene_bands["B04"]}
        resp = await client.post("/api/v1/eo/raster/inspect", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["width"] == 50
        assert data["height"] == 50
        assert "4326" in data["crs"]


@pytest.mark.asyncio
async def test_ndvi_endpoint(synthetic_scene_bands):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "scene_id": "TEST_SCENE_01",
            "platform": "Sentinel-2B",
            "sensor": "MSI",
            "index_type": "NDVI",
            "aoi_geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-54.9, -11.4],
                        [-54.6, -11.4],
                        [-54.6, -11.1],
                        [-54.9, -11.1],
                        [-54.9, -11.4],
                    ]
                ],
            },
            "asset_urls": {
                "B04": synthetic_scene_bands["B04"],
                "B08": synthetic_scene_bands["B08"],
            },
        }
        resp = await client.post("/api/v1/eo/indices/ndvi", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["index_name"] == "NDVI"
        assert data["epistemic_level"] == "CALCULATED"
        # NIR: 4000, RED: 1000 -> (4000 - 1000) / (4000 + 1000) = 0.60
        assert data["statistics"]["mean"] == 0.60
        assert data["vegetation_summary"] is not None


@pytest.mark.asyncio
async def test_timeseries_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "aoi_id": "aoi-001",
            "aoi_name": "Test AOI",
            "measurements": [
                {
                    "acquisition_datetime": "2025-01-01T00:00:00Z",
                    "metric_name": "NDVI_MEAN",
                    "value": 0.45,
                    "unit": "index_value",
                    "source_scene_id": "S2_01",
                    "platform": "Sentinel-2A",
                    "sensor": "MSI",
                    "valid_pixel_percentage": 100.0,
                },
                {
                    "acquisition_datetime": "2025-06-01T00:00:00Z",
                    "metric_name": "NDVI_MEAN",
                    "value": 0.65,
                    "unit": "index_value",
                    "source_scene_id": "S2_02",
                    "platform": "Sentinel-2B",
                    "sensor": "MSI",
                    "valid_pixel_percentage": 100.0,
                },
            ],
        }
        resp = await client.post("/api/v1/eo/timeseries", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_observations"] == 2
        assert data["epistemic_level"] == "CALCULATED"
