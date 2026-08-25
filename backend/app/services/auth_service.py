# app/services/auth_service.py
# Authentication utilities for DocMind AI.
#
# Handles:
#   1. Password hashing with bcrypt
#   2. Password verification
#   3. JWT access-token creation
#
# Plain-text passwords are never stored.

import os
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt


# ---------------------------------------------------------------------------
# JWT configuration
# ---------------------------------------------------------------------------
#
# In development, a fallback secret is provided so the application can run
# without additional configuration.
#
# IMPORTANT:
# In production, always set JWT_SECRET_KEY to a long random secret through
# an environment variable. Never use the development fallback in production.

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "dev-only-change-this-secret-before-production",
)

JWT_ALGORITHM = "HS256"

# Access token lifetime.
JWT_EXPIRE_MINUTES = 60


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    A unique random salt is generated automatically on every call, so
    hashing the same password twice produces different hashes.

    Args:
        password: Plain-text password.

    Returns:
        Bcrypt hash string suitable for database storage.
    """

    password_bytes = password.encode("utf-8")

    hashed_bytes = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return hashed_bytes.decode("utf-8")


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain_password: Password supplied by the user.
        password_hash: Bcrypt hash retrieved from the database.

    Returns:
        True if the password matches.
        False if it does not match or the stored hash is invalid.
    """

    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except Exception:
        # Invalid/malformed hashes are treated as incorrect passwords.
        return False


# ---------------------------------------------------------------------------
# JWT access token
# ---------------------------------------------------------------------------

def create_access_token(user_id: int) -> str:
    """
    Create a JWT access token for an authenticated user.

    The user's database ID is stored in the JWT `sub` (subject) claim.

    Args:
        user_id: Database ID of the authenticated user.

    Returns:
        Encoded JWT access token.
    """

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    return token