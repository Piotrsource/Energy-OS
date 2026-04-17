"""
Global exception handler that returns structured JSON errors
with request_id for every unhandled exception.
"""

import logging
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.middleware.request_context import request_id_var

logger = logging.getLogger("energy_platform")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    rid = request_id_var.get("")
    logger.error(
        "Unhandled exception: %s | path=%s | request_id=%s",
        exc,
        request.url.path,
        rid,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "request_id": rid,
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    rid = request_id_var.get("")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "code": _status_to_code(exc.status_code),
            "request_id": rid,
        },
    )


def _status_to_code(status: int) -> str:
    return {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
    }.get(status, f"HTTP_{status}")
