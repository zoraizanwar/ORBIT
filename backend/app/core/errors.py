from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.core.logging import logger


class OrbitException(Exception):
    """Base exception class for domain errors in ORBIT."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


async def orbit_exception_handler(request: Request, exc: OrbitException) -> JSONResponse:
    """Handles domain exceptions and returns structured JSON responses."""
    logger.warning(
        f"Domain exception on {request.method} {request.url.path}: {exc.message} | Details: {exc.details}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handles HTTP exceptions cleanly without exposing sensitive internals."""
    logger.warning(
        f"HTTP exception {exc.status_code} on {request.method} {request.url.path}: {exc.detail}"
    )
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "HTTPException",
                    "message": exc.detail.get("reason", str(exc.detail)),
                    "details": exc.detail,
                    "status_code": exc.status_code,
                }
            },
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "message": str(exc.detail),
                "status_code": exc.status_code,
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches unhandled internal exceptions, logging details without leaking secrets to client."""
    logger.error(
        f"Unhandled server error on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected internal server error occurred. Please contact the administrator.",
            }
        },
    )
