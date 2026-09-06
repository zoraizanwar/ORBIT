import os
import site
import sys

# Ensure PROJ_LIB and PROJ_DATA point to rasterio's bundled proj_data before any GDAL/rasterio imports,
# preventing conflicts with external PostgreSQL/PostGIS installations on the host.
for _sp in site.getsitepackages() + [site.getusersitepackages()]:
    _rd = os.path.join(_sp, "rasterio", "proj_data")
    if os.path.isdir(_rd):
        os.environ["PROJ_LIB"] = _rd
        os.environ["PROJ_DATA"] = _rd
        break

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings


@pytest_asyncio.fixture
async def async_client():
    """Provides an asynchronous HTTP client for testing FastAPI endpoints."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client
