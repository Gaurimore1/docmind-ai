# app/schemas/user.py
# Pydantic schemas for user registration and responses.
#
# IMPORTANT: UserResponse deliberately omits password_hash so it is never
# exposed through the API, even accidentally.

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """
    Request body for user registration.

    The plain-text password is accepted here for validation and is
    immediately hashed before any database write — it is never stored.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User's display name",
    )

    email: EmailStr = Field(
        ...,
        description="User's email address — must be unique",
    )

    password: str = Field(
        ...,
        min_length=8,
        description="Plain-text password (minimum 8 characters)",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty or whitespace-only.")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        # Enforce minimum length after stripping is intentionally NOT done
        # for passwords — whitespace may be deliberate in a passphrase.
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return value


class UserResponse(BaseModel):
    """
    Safe public representation of a user.

    password_hash is intentionally absent — it must never leave the server.
    """

    id: int
    name: str
    email: str
    is_active: bool

    # Allow Pydantic to populate this model from a SQLAlchemy ORM instance
    # (orm_mode equivalent in Pydantic v2).
    model_config = {"from_attributes": True}
