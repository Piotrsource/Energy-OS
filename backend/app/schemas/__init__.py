# =============================================================================
# schemas/__init__.py — Pydantic Schemas Package
# =============================================================================
# PURPOSE: Marks the schemas/ directory as a Python package.
#
# This package contains Pydantic v2 models for request validation and
# response serialization. Schemas are SEPARATE from ORM models because:
#
#   1. API responses should never expose sensitive fields (e.g., password_hash)
#   2. Request bodies often have different fields than database rows
#   3. Schemas enforce input validation (type checking, required fields)
#   4. Schemas document the API contract via OpenAPI/Swagger
#
# NAMING CONVENTION:
#   - *Create: Fields required to create a new resource (request body)
#   - *Update: Optional fields for partial updates (PATCH request body)
#   - *Read:   Full resource representation (response body)
# =============================================================================
