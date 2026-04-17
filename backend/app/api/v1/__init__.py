# =============================================================================
# api/v1/__init__.py — API Version 1 Package
# =============================================================================
# PURPOSE: Marks the v1/ directory as a Python package.
#
# This package contains all API v1 routers, one per domain:
#   - auth.py            → POST /api/v1/login
#   - buildings.py       → CRUD /api/v1/buildings
#   - zones.py           → CRUD /api/v1/zones
#   - users.py           → CRUD /api/v1/users
#   - sensors.py         → /api/v1/sensors/readings
#   - forecasts.py       → CRUD /api/v1/forecasts
#   - recommendations.py → CRUD /api/v1/recommendations
#   - analytics.py       → /api/v1/buildings/{id}/energy-summary, carbon-emissions, anomalies
#   - router.py          → Aggregates all routers under /api/v1
# =============================================================================
