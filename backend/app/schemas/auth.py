# =============================================================================
# schemas/auth.py — Authentication Schemas
# =============================================================================
# PURPOSE: Define request/response schemas for the login endpoint.
#
# LOGIN FLOW:
#   1. Client sends LoginRequest (email + password) to POST /api/v1/login
#   2. Server validates credentials
#   3. Server returns TokenResponse (access_token + token_type)
#   4. Client includes token in future requests: Authorization: Bearer <token>
# =============================================================================

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """
    Request body for POST /api/v1/login.
    Contains the user's email and plaintext password.
    """
    email: str = Field(..., description="User's email address", examples=["admin@energyplatform.local"])
    password: str = Field(..., description="User's plaintext password", min_length=1)


class TokenResponse(BaseModel):
    """
    Response body returned after successful authentication.
    Contains a JWT access token that the client uses for all subsequent requests.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
