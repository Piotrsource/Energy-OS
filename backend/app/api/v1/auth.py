# =============================================================================
# api/v1/auth.py — Authentication Router
# =============================================================================
# PURPOSE: Handle user login and JWT token issuance.
#
# ENDPOINTS:
#   POST /api/v1/login → Authenticate with email + password, receive JWT token
#
# AUTHENTICATION FLOW:
#   1. Client sends email + password in the request body
#   2. Server looks up the user by email
#   3. Server verifies the password against the stored bcrypt hash
#   4. On success: returns a JWT access token
#   5. On failure: returns 401 Unauthorized
#
# NOTE: This endpoint uses OAuth2PasswordRequestForm (form data, not JSON)
# so it's compatible with Swagger UI's "Authorize" button and standard
# OAuth2 client libraries. The fields are "username" (email) and "password".
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.user_service import UserService
from app.auth.jwt import create_access_token
from app.schemas.auth import TokenResponse

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT token",
    responses={
        401: {"description": "Invalid email or password"},
    },
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate a user with email and password.

    Send credentials as form data (application/x-www-form-urlencoded):
    - **username**: The user's email address (OAuth2 spec uses "username" field)
    - **password**: The user's plaintext password

    Returns a JWT access token on success. Use this token in the
    Authorization header for all subsequent requests:
        Authorization: Bearer <access_token>
    """
    # The OAuth2 spec calls it "username" but we use email for login
    user = await UserService.authenticate(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT with user ID and role as claims
    access_token = create_access_token(user.id, user.role.value)

    return TokenResponse(access_token=access_token, token_type="bearer")
