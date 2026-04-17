# =============================================================================
# services/__init__.py — Business Logic Layer Package
# =============================================================================
# PURPOSE: Marks the services/ directory as a Python package.
#
# The service layer sits between API routers and the database:
#   Router (validates input) → Service (business logic) → Database (persistence)
#
# WHY A SEPARATE SERVICE LAYER?
#   1. Keeps routers thin — they only handle HTTP concerns (status codes, headers)
#   2. Business logic is testable without FastAPI/HTTP overhead
#   3. Multiple routers can reuse the same service methods
#   4. Complex operations (multi-table queries, calculations) stay organized
#
# Each service file corresponds to one domain (buildings, zones, users, etc.)
# and contains static methods that accept a database session as their first arg.
# =============================================================================
