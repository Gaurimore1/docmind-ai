# app/services/auth_dependency.py
# JWT authentication dependency for DocMind AI.
#
# This module:
#   1. Reads the Authorization: Bearer <token> header
#   2. Validates the JWT
#   3. Extracts the user ID
#   4. Loads the user from PostgreSQL
#   5. Returns the authenticated User object
#
# Protected routes can then use:
#
#     current_user: User = Depends(get_current_user)

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.services.auth_service import (
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)


# ---------------------------------------------------------------------------
# HTTP Bearer authentication
# ---------------------------------------------------------------------------

security = HTTPBearer(
    auto_error=True,
)


# ---------------------------------------------------------------------------
# Get current authenticated user
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Validate the JWT access token and return the authenticated User.

    Expected request header:

        Authorization: Bearer <JWT_TOKEN>

    Raises:
        401 if the token is missing, invalid, expired, or the user
        no longer exists/is inactive.

    Returns:
        User ORM object representing the authenticated user.
    """

    # ---------------------------------------------------------
    # Step 1 — Extract token
    # ---------------------------------------------------------

    token = credentials.credentials

    # ---------------------------------------------------------
    # Step 2 — Decode and validate JWT
    # ---------------------------------------------------------

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ---------------------------------------------------------
    # Step 3 — Extract user ID
    # ---------------------------------------------------------

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ---------------------------------------------------------
    # Step 4 — Convert user ID
    # ---------------------------------------------------------

    try:
        user_id = int(user_id)

    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ---------------------------------------------------------
    # Step 5 — Load user
    # ---------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ---------------------------------------------------------
    # Step 6 — Check account status
    # ---------------------------------------------------------

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive.",
        )

    # ---------------------------------------------------------
    # Step 7 — Authentication successful
    # ---------------------------------------------------------

    return user