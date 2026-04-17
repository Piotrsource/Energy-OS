# =============================================================================
# auth/passwords.py — Password Hashing Utilities
# =============================================================================
# PURPOSE: Provide secure password hashing and verification using bcrypt.
#
# WHY BCRYPT?
#   - Industry standard for password storage (OWASP recommended)
#   - Includes a random salt automatically (no separate salt column needed)
#   - Intentionally slow (~100ms per hash) to resist brute-force attacks
#   - The "work factor" can be increased over time as hardware gets faster
#
# SECURITY RULES:
#   - Passwords are NEVER stored as plaintext in the database
#   - The password_hash column stores the full bcrypt output including salt
#   - The hash_password() function is called during user creation
#   - The verify_password() function is called during login
#
# USAGE:
#   from app.auth.passwords import hash_password, verify_password
#
#   hashed = hash_password("my_secret_password")
#   is_valid = verify_password("my_secret_password", hashed)  # True
# =============================================================================

import bcrypt

# Work factor (log rounds). 12 is the standard default (~250ms per hash).
_ROUNDS = 12


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password for secure storage in the database.

    Args:
        plain_password: The user's plaintext password.

    Returns:
        A bcrypt hash string (60 characters) including the salt.
    """
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against its stored bcrypt hash.

    Args:
        plain_password: The password the user just typed in.
        hashed_password: The bcrypt hash stored in the database.

    Returns:
        True if the password matches, False otherwise.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False
