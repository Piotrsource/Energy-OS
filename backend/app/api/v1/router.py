# =============================================================================
# api/v1/router.py — Central API v1 Router
# =============================================================================
# PURPOSE: Aggregate all domain routers into a single router mounted
# under the /api/v1 prefix. This is the ONLY router imported by main.py.
#
# ENDPOINT MAP:
#   /api/v1/login                              → auth.py
#   /api/v1/users                              → users.py
#   /api/v1/buildings                          → buildings.py
#   /api/v1/zones                              → zones.py
#   /api/v1/sensors/readings                   → sensors.py
#   /api/v1/hvac/status                        → hvac.py
#   /api/v1/energy-meters/readings             → energy_meters.py
#   /api/v1/forecasts                          → forecasts.py
#   /api/v1/recommendations                    → recommendations.py
#   /api/v1/buildings/{id}/energy-summary      → analytics.py
#   /api/v1/buildings/{id}/carbon-emissions     → analytics.py
#   /api/v1/anomalies                          → analytics.py
#
# SWAGGER UI TAGS:
#   Each router is assigned a tag that groups its endpoints in the
#   Swagger documentation (http://localhost:8000/docs).
# =============================================================================

from fastapi import APIRouter

from app.api.v1 import (
    auth, users, buildings, zones, sensors, hvac,
    energy_meters, forecasts, recommendations, analytics,
)
from app.api.v1 import alert_rules, alerts, notifications, realtime
from app.api.v1.p2p import (
    prosumers as p2p_prosumers,
    wallet as p2p_wallet,
    offers as p2p_offers,
    requests as p2p_requests,
    orders as p2p_orders,
    trading_rules as p2p_trading_rules,
    market as p2p_market,
    communities as p2p_communities,
    analytics as p2p_analytics,
)

# =============================================================================
# MAIN V1 ROUTER
# =============================================================================
# All domain routers are mounted here with their URL prefixes and Swagger tags.
# The /api/v1 prefix is added when this router is included in main.py.
# =============================================================================
api_v1_router = APIRouter(prefix="/api/v1")

# Authentication — no prefix so login is at /api/v1/login
api_v1_router.include_router(
    auth.router,
    tags=["Authentication"],
)

# User management — /api/v1/users
api_v1_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

# Building CRUD — /api/v1/buildings
api_v1_router.include_router(
    buildings.router,
    prefix="/buildings",
    tags=["Buildings"],
)

# Zone CRUD — /api/v1/zones
api_v1_router.include_router(
    zones.router,
    prefix="/zones",
    tags=["Zones"],
)

# Sensor data — /api/v1/sensors/readings
api_v1_router.include_router(
    sensors.router,
    prefix="/sensors",
    tags=["Sensors"],
)

# HVAC status — /api/v1/hvac/status
api_v1_router.include_router(
    hvac.router,
    prefix="/hvac",
    tags=["HVAC"],
)

# Energy meters — /api/v1/energy-meters/readings
api_v1_router.include_router(
    energy_meters.router,
    prefix="/energy-meters",
    tags=["Energy Meters"],
)

# AI Forecasts — /api/v1/forecasts
api_v1_router.include_router(
    forecasts.router,
    prefix="/forecasts",
    tags=["Forecasts"],
)

# AI Recommendations — /api/v1/recommendations
api_v1_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["Recommendations"],
)

# Analytics & Dashboard — various paths under /api/v1/
# No prefix because analytics routes define their own paths:
#   /buildings/{id}/energy-summary
#   /buildings/{id}/carbon-emissions
#   /anomalies
api_v1_router.include_router(
    analytics.router,
    tags=["Analytics"],
)

# Alert rules — /api/v1/alert-rules
api_v1_router.include_router(
    alert_rules.router,
    prefix="/alert-rules",
    tags=["Alerts"],
)

# Alerts — /api/v1/alerts
api_v1_router.include_router(
    alerts.router,
    prefix="/alerts",
    tags=["Alerts"],
)

# Notifications — /api/v1/notifications
api_v1_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"],
)

# Real-time: latest readings, device health, WebSocket — /api/v1/sensors/*
api_v1_router.include_router(
    realtime.router,
    prefix="/sensors",
    tags=["Real-Time"],
)

# =========================================================================
# P2P ENERGY TRADING — Phase 9
# =========================================================================
api_v1_router.include_router(
    p2p_prosumers.router,
    prefix="/p2p/prosumers",
    tags=["P2P — Prosumers"],
)
api_v1_router.include_router(
    p2p_wallet.router,
    prefix="/p2p/wallet",
    tags=["P2P — Wallet"],
)
api_v1_router.include_router(
    p2p_offers.router,
    prefix="/p2p/offers",
    tags=["P2P — Marketplace"],
)
api_v1_router.include_router(
    p2p_requests.router,
    prefix="/p2p/requests",
    tags=["P2P — Marketplace"],
)
api_v1_router.include_router(
    p2p_orders.router,
    prefix="/p2p/orders",
    tags=["P2P — Orders"],
)
api_v1_router.include_router(
    p2p_trading_rules.router,
    prefix="/p2p/trading-rules",
    tags=["P2P — Trading Rules"],
)
api_v1_router.include_router(
    p2p_market.router,
    prefix="/p2p/market",
    tags=["P2P — Market"],
)
api_v1_router.include_router(
    p2p_communities.router,
    prefix="/p2p/communities",
    tags=["P2P — Communities"],
)
api_v1_router.include_router(
    p2p_analytics.router,
    prefix="/p2p/analytics",
    tags=["P2P — Analytics"],
)
