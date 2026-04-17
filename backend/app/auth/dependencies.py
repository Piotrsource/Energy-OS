# =============================================================================
# auth/dependencies.py — FastAPI Authentication & Authorization Dependencies
# =============================================================================
# PURPOSE: Provide reusable FastAPI dependencies that protect API endpoints.
# These are injected into route handlers via Depends() to enforce:
#   1. Authentication: Is the user logged in with a valid JWT?
#   2. Authorization: Does the user's role allow this specific action?
#
# DEPENDENCY CHAIN:
#   Request → oauth2_scheme (extracts Bearer token from header)
#           → get_current_user (decodes JWT, loads user from DB)
#           → require_roles (checks user's role against allowed roles)
#           → Route handler receives the authenticated User object
#
# USAGE IN ROUTES:
#   # Any authenticated user:
#   @router.get("/buildings")
#   async def list_buildings(user: User = Depends(get_current_user)):
#       ...
#
#   # Only admins and facility managers:
#   @router.post("/buildings")
#   async def create_building(
#       user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FACILITY_MANAGER)),
#   ):
#       ...
# =============================================================================

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.jwt import decode_access_token
from app.models.user import User, UserRole
from app.middleware.request_context import request_user_id_var


# =============================================================================
# OAUTH2 SCHEME
# =============================================================================
# Tells FastAPI (and Swagger UI) that this API uses Bearer token authentication.
# tokenUrl is the endpoint where clients obtain tokens (the login endpoint).
# Swagger UI will show a "lock" icon and an authorize dialog because of this.
# =============================================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency: extract the JWT from the request, decode it,
    and load the corresponding User from the database.

    This dependency is used on EVERY authenticated endpoint.

    Args:
        token: The Bearer token extracted from the Authorization header.
        db: The database session (injected by FastAPI).

    Returns:
        The authenticated User ORM object.

    Raises:
        HTTPException 401: If the token is missing, invalid, expired,
            or the user no longer exists in the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Step 1: Decode and verify the JWT
    try:
        payload = decode_access_token(token)
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Step 2: Load the user from the database
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    request_user_id_var.set(str(user.id))
    return user


def require_roles(*allowed_roles: UserRole):
    """
    Factory that creates a FastAPI dependency requiring the current user
    to have one of the specified roles.

    This is a "dependency factory" — it returns a new async function
    each time it's called. The returned function can be used with Depends().

    Args:
        *allowed_roles: One or more UserRole values that are permitted.

    Returns:
        An async dependency function that returns the User if authorized,
        or raises HTTPException 403 if the user's role is not in the list.

    Usage:
        @router.post("/users")
        async def create_user(
            user: User = Depends(require_roles(UserRole.ADMIN)),
        ):
            ...
    """
    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{current_user.role.value}' does not have permission "
                    f"for this action. Required: {[r.value for r in allowed_roles]}"
                ),
            )
        return current_user

    return role_checker
