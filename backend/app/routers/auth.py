# app/routers/auth.py
# Authentication routes for DocMind AI.
#
# Currently implements:
#   POST /signup
#   POST /login

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import (
    create_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(tags=["Auth"])


# ---------------------------------------------------------------------------
# Login schema
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    """
    Request body for user login.
    """

    email: EmailStr
    password: str


# ---------------------------------------------------------------------------
# Signup
# ---------------------------------------------------------------------------

@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def signup(
    payload: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Create a new user account.

    Flow:
        1. Validate request body.
        2. Normalize email to lowercase.
        3. Check for an existing account.
        4. Hash password with bcrypt.
        5. Store the user.
        6. Return safe user information.

    The password and password_hash are never returned.
    """

    # ---------------------------------------------------------
    # Step 1 — Normalize email
    # ---------------------------------------------------------

    normalised_email = payload.email.lower()

    # ---------------------------------------------------------
    # Step 2 — Check for duplicate email
    # ---------------------------------------------------------

    existing = (
        db.query(User.id)
        .filter(User.email == normalised_email)
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # ---------------------------------------------------------
    # Step 3 — Hash password
    # ---------------------------------------------------------

    hashed = hash_password(payload.password)

    # ---------------------------------------------------------
    # Step 4 — Create user
    # ---------------------------------------------------------

    user = User(
        name=payload.name.strip(),
        email=normalised_email,
        password_hash=hashed,
    )

    # ---------------------------------------------------------
    # Step 5 — Persist user
    # ---------------------------------------------------------

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account. Please try again.",
        )

    # ---------------------------------------------------------
    # Step 6 — Safe response
    # ---------------------------------------------------------

    return user


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    summary="Login to an existing account",
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate an existing user and return a JWT access token.

    Flow:
        Email + password
              ↓
        Find user
              ↓
        Verify bcrypt password
              ↓
        Check account status
              ↓
        Create JWT
              ↓
        Return token + user information
    """

    # ---------------------------------------------------------
    # Step 1 — Normalize email
    # ---------------------------------------------------------

    normalised_email = payload.email.lower()

    # ---------------------------------------------------------
    # Step 2 — Find user
    # ---------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.email == normalised_email)
        .first()
    )

    # ---------------------------------------------------------
    # Step 3 — Verify credentials
    # ---------------------------------------------------------

    if user is None or not verify_password(
        payload.password,
        user.password_hash,
    ):
        # Use the same message for both cases.
        #
        # This avoids revealing whether an email address exists
        # in the database.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # ---------------------------------------------------------
    # Step 4 — Check account status
    # ---------------------------------------------------------

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive.",
        )

    # ---------------------------------------------------------
    # Step 5 — Create JWT
    # ---------------------------------------------------------

    access_token = create_access_token(user.id)

    # ---------------------------------------------------------
    # Step 6 — Return token + safe user information
    # ---------------------------------------------------------

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_active": user.is_active,
        },
    }