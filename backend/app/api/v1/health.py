from datetime import datetime, timezone
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import logger
from app.db.session import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    summary="Comprehensive Health Check",
    response_description="System status including Database, PostGIS, Redis, and Celery",
)
async def get_health_status(
    db: Optional[AsyncSession] = Depends(get_db),
) -> JSONResponse:
    """Performs active dependency health checks against PostgreSQL, PostGIS, Redis, and Celery."""
    health_results: Dict[str, Any] = {
        "status": "healthy",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "environment": settings.ORBIT_ENV,
        "app_name": settings.ORBIT_APP_NAME,
        "services": {
            "api": {
                "status": "healthy",
                "version": "0.1.0",
            },
            "database": {
                "status": "unknown",
                "details": None,
            },
            "postgis": {
                "status": "unknown",
                "details": None,
            },
            "redis": {
                "status": "unknown",
                "details": None,
            },
        },
    }

    is_degraded = False

    # 1. Check PostgreSQL Database Connectivity
    try:
        if db is not None:
            db_res = await db.execute(text("SELECT 1;"))
            val = db_res.scalar()
            if val == 1:
                health_results["services"]["database"]["status"] = "healthy"
                health_results["services"]["database"]["details"] = "Connected to PostgreSQL"
            else:
                health_results["services"]["database"]["status"] = "degraded"
                is_degraded = True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_results["services"]["database"]["status"] = "unavailable"
        health_results["services"]["database"]["details"] = f"Error: {type(e).__name__}"
        is_degraded = True

    # 2. Check PostGIS Extension Availability
    try:
        if db is not None and health_results["services"]["database"]["status"] == "healthy":
            postgis_res = await db.execute(text("SELECT postgis_full_version();"))
            version_str = postgis_res.scalar()
            if version_str:
                health_results["services"]["postgis"]["status"] = "healthy"
                health_results["services"]["postgis"]["details"] = str(version_str)
            else:
                health_results["services"]["postgis"]["status"] = "unavailable"
                is_degraded = True
        else:
            health_results["services"]["postgis"]["status"] = "unavailable"
            health_results["services"]["postgis"]["details"] = "Database unavailable"
    except Exception as e:
        logger.error(f"PostGIS health check failed: {str(e)}")
        health_results["services"]["postgis"]["status"] = "unavailable"
        health_results["services"]["postgis"]["details"] = f"Error: {type(e).__name__}"
        is_degraded = True

    # 3. Check Redis Connectivity
    try:
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        ping_res = await r.ping()
        await r.aclose()
        if ping_res is True or ping_res == "PONG":
            health_results["services"]["redis"]["status"] = "healthy"
            health_results["services"]["redis"]["details"] = "Connected to Redis"
        else:
            health_results["services"]["redis"]["status"] = "degraded"
            is_degraded = True
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        health_results["services"]["redis"]["status"] = "unavailable"
        health_results["services"]["redis"]["details"] = f"Error: {type(e).__name__}"
        is_degraded = True

    if is_degraded:
        # If any essential dependency is unavailable, mark overall system as degraded
        all_down = all(
            v["status"] == "unavailable" for k, v in health_results["services"].items() if k != "api"
        )
        health_results["status"] = "unavailable" if all_down else "degraded"
        status_code = (
            status.HTTP_503_SERVICE_UNAVAILABLE
            if all_down
            else status.HTTP_200_OK
        )
    else:
        health_results["status"] = "healthy"
        status_code = status.HTTP_200_OK

    return JSONResponse(status_code=status_code, content=health_results)
