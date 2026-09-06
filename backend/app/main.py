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

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.core.errors import (
    OrbitException,
    orbit_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    logger.info(f"Starting {settings.ORBIT_APP_NAME} in [{settings.ORBIT_ENV}] mode...")
    logger.info(f"CORS Allowed Origins: {settings.ORBIT_CORS_ORIGINS}")
    yield
    logger.info(f"Shutting down {settings.ORBIT_APP_NAME}...")


def create_application() -> FastAPI:
    """FastAPI application factory for ORBIT."""
    app = FastAPI(
        title=settings.ORBIT_APP_NAME,
        description="Geospatial Intelligence & Earth Monitoring Platform API",
        version="0.1.0",
        docs_url="/docs" if settings.ORBIT_DEBUG else None,
        redoc_url="/redoc" if settings.ORBIT_DEBUG else None,
        openapi_url="/openapi.json" if settings.ORBIT_DEBUG else None,
        lifespan=lifespan,
    )

    # Configure CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ORBIT_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Exception Handlers
    app.add_exception_handler(OrbitException, orbit_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Register API Routers
    app.include_router(api_router, prefix=settings.ORBIT_API_V1_STR)

    @app.get("/", summary="Root Status")
    async def root():
        return {
            "name": settings.ORBIT_APP_NAME,
            "version": "0.1.0",
            "status": "operational",
            "docs": "/docs" if settings.ORBIT_DEBUG else "disabled",
            "health": f"{settings.ORBIT_API_V1_STR}/health",
        }

    return app


app = create_application()
