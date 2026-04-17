# =============================================================================
# auth/roles.py — Role Definitions and Permission Matrix
# =============================================================================
# PURPOSE: Define the role-based access control (RBAC) system.
# The UserRole enum is imported from models/user.py (single source of truth).
# This module adds the permission matrix that maps roles to allowed actions.
#
# ROLE HIERARCHY:
#   admin > facility_manager > technician
#
# PERMISSION RULES:
#   - Admin: Full access to all endpoints (create/read/update/delete everything)
#   - Facility Manager: Manage buildings/zones, create forecasts/recommendations,
#     but CANNOT manage other users
#   - Technician: Read-only access + can submit sensor readings and
#     approve/reject recommendations
#
# HOW PERMISSIONS ARE ENFORCED:
#   Route handlers use the require_roles() dependency from dependencies.py.
#   Example: Depends(require_roles(UserRole.ADMIN, UserRole.FACILITY_MANAGER))
# =============================================================================

from app.models.user import UserRole

# Re-export UserRole so other modules can import from auth.roles
__all__ = ["UserRole"]
