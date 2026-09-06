import os
import tempfile
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def temporal_scene_rasters():
    """
    Creates temporary synthetic T1 and T2 GeoTIFFs for change endpoint testing.
    """
    temp_dir = tempfile.mkdtemp()
    transform = from_origin(-55.0, -11.0, 0.01, 0.01)

    t1_path = os.path.join(temp_dir, "t1_ndvi.tif")
    t2_path = os.path.join(temp_dir, "t2_ndvi.tif")

    # T1: 0.60 everywhere (NDVI * 10000 = 6000)
    # T2: 0.35 everywhere (loss episode -> 3500)
    d_t1 = np.full((30, 30), 6000, dtype=np.uint16)
    d_t2 = np.full((30, 30), 3500, dtype=np.uint16)

    for path, data in [(t1_path, d_t1), (t2_path, d_t2)]:
        with rasterio.open(
            path,
            "w",
            driver="GTiff",
            height=30,
            width=30,
            count=1,
            dtype=np.uint16,
            crs="EPSG:4326",
            transform=transform,
            nodata=0,
        ) as dst:
            dst.write(data, 1)

    yield {"t1": t1_path, "t2": t2_path}

    for p in [t1_path, t2_path]:
        if os.path.exists(p):
            os.remove(p)
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)


@pytest.mark.asyncio
async def test_compare_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "aoi_id": "aoi-01",
            "aoi_name": "Test Forest AOI",
            "measurement_t1": {
                "acquisition_datetime": "2023-06-01T00:00:00Z",
                "metric_name": "NDVI_MEAN",
                "value": 0.62,
                "unit": "index_value",
                "source_scene_id": "S2A_2023",
                "platform": "Sentinel-2A",
                "sensor": "MSI",
                "cloud_cover": 5.0,
            },
            "measurement_t2": {
                "acquisition_datetime": "2026-06-01T00:00:00Z",
                "metric_name": "NDVI_MEAN",
                "value": 0.40,
                "unit": "index_value",
                "source_scene_id": "S2B_2026",
                "platform": "Sentinel-2B",
                "sensor": "MSI",
                "cloud_cover": 7.0,
            },
        }
        resp = await client.post("/api/v1/eo/change/compare", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["metric"] == "NDVI"
        assert data["absolute_delta"] == -0.22
        assert data["classification"] == "SIGNIFICANT_DECREASE"
        assert data["epistemic_level"] == "CALCULATED"


@pytest.mark.asyncio
async def test_spatial_mask_endpoint(temporal_scene_rasters):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "t1_scene_id": "S2A_2023",
            "t2_scene_id": "S2B_2026",
            "t1_raster_uri": temporal_scene_rasters["t1"],
            "t2_raster_uri": temporal_scene_rasters["t2"],
            "aoi_geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-54.9, -11.2],
                        [-54.8, -11.2],
                        [-54.8, -11.1],
                        [-54.9, -11.1],
                        [-54.9, -11.2],
                    ]
                ],
            },
        }
        resp = await client.post("/api/v1/eo/change/mask", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["metric"] == "NDVI"
        assert data["statistics"]["valid_pixel_count"] > 0
        assert data["epistemic_level"] == "CALCULATED"


@pytest.mark.asyncio
async def test_compare_endpoint_error_handling_sanitized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # T1 >= T2 violation
        payload = {
            "aoi_id": "aoi-01",
            "aoi_name": "Test Forest AOI",
            "measurement_t1": {
                "acquisition_datetime": "2026-06-01T00:00:00Z",
                "metric_name": "NDVI_MEAN",
                "value": 0.62,
                "unit": "index_value",
                "source_scene_id": "S2A_2026",
                "platform": "Sentinel-2A",
                "sensor": "MSI",
            },
            "measurement_t2": {
                "acquisition_datetime": "2023-06-01T00:00:00Z",
                "metric_name": "NDVI_MEAN",
                "value": 0.40,
                "unit": "index_value",
                "source_scene_id": "S2B_2023",
                "platform": "Sentinel-2B",
                "sensor": "MSI",
            },
        }
        resp = await client.post("/api/v1/eo/change/compare", json=payload)
        assert resp.status_code == 422
        data = resp.json()
        assert "error" in data
        assert "Temporal comparison failed" in data["error"]["message"]
