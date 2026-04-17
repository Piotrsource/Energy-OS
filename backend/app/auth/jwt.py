# =============================================================================
# auth/jwt.py — JWT Token Creation and Verification
# =============================================================================
# PURPOSE: Handle JSON Web Token (JWT) operations for API authentication.
#
# JWT FLOW:
#   1. User sends POST /api/v1/login with email + password
#   2. Server verifies credentials → calls create_access_token()
#   3. Server returns the JWT to the client
#   4. Client includes the JWT in Authorization header: "Bearer <token>"
#   5. Server calls decode_access_token() on every authenticated request
#
# TOKEN PAYLOAD (claims):
#   - sub: User's UUID (subject — identifies who the token belongs to)
#   - role: User's role (admin/facility_manager/technician) for RBAC
#   - exp: Expiration timestamp (after this, the token is rejected)
#
# SECURITY NOTES:
#   - Tokens are signed with HS256 (symmetric) using JWT_SECRET_KEY
#   - The secret MUST be at least 32 characters and cryptographically random
#   - Tokens are stateless — no server-side session storage needed
#   - Token revocation requires a deny-list (not implemented in MVP)
#
# USAGE:
#   from app.auth.jwt import create_access_token, decode_access_token
#
#   token = create_access_token(user.id, user.role.value)
#   payload = decode_access_token(token)  # {"sub": "uuid", "role": "admin", "exp": ...}
# =============================================================================

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import jwt, JWTError  # noqa: F401 — JWTError re-exported for dependencies.py

from app.config import settings


def create_access_token(user_id: UUID, role: str) -> str:
    """
    Create a signed JWT access token containing the user's identity and role.

    Args:
        user_id: The user's UUID (stored as the "sub" claim).
        role: The user's role string (e.g., "admin", "facility_manager").

    Returns:
        A signed JWT string that the client should include in the
        Authorization header as "Bearer <token>".
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload = {
        "sub": str(user_id),   # Subject: who this token identifies
        "role": role,           # Role: for role-based access control
        "exp": expire,          # Expiration: when this token becomes invalid
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.

    Checks the signature and expiration. Raises JWTError if the token
    is invalid, expired, or tampered with.

    Args:
        token: The JWT string from the Authorization header.

    Returns:
        The decoded payload dict with "sub", "role", and "exp" keys.

    Raises:
        jose.JWTError: If the token is invalid or expired.
    """
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
