"""
FastAPI Application Entry Point — Phase 1 hardened.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings, validate_production_settings
from app.db.engine import engine
from app.api.v1.router import api_v1_router
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.error_handler import global_exception_handler, http_exception_handler
from app.middleware.logging_config import setup_logging

logger = logging.getLogger("energy_platform")


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_production_settings()
    setup_logging(settings.log_level)

    from app.services.alert_engine import run_alert_engine
    from app.db.redis import redis_client

    alert_task = asyncio.create_task(run_alert_engine())

    logger.info("Application startup complete — version 0.3.0")
    yield

    # ── Graceful shutdown ────────────────────────────────────────────────
    alert_task.cancel()
    try:
        await alert_task
    except asyncio.CancelledError:
        pass

    await redis_client.aclose()
    logger.info("Redis connection closed")

    await engine.dispose()
    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend API for the AI Energy Optimization Platform. "
        "Manages buildings, zones, sensors, AI forecasts, and "
        "energy optimization recommendations for hotels and commercial buildings."
    ),
    version="0.3.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware (outermost first) ──────────────────────────────────────────
app.add_middleware(RequestContextMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ───────────────────────────────────────────────────
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, global_exception_handler)  # type: ignore[arg-type]

# ── Routers ───────────────────────────────────────────────────────────────
app.include_router(api_v1_router)


# ── Health check with DB ping (1.9) ──────────────────────────────────────
@app.get("/health", tags=["Health"], summary="Health check with DB ping")
async def health_check():
    """
    Returns DB connectivity status.
    Always HTTP 200 — "degraded" when DB is unreachable (avoids restart loops).
    """
    from sqlalchemy import text
    from app.db.engine import AsyncSessionLocal

    db_status = "ok"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "unreachable"

    overall = "ok" if db_status == "ok" else "degraded"
    return {"status": overall, "db": db_status, "version": "0.3.0"}
