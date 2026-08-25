# app/models/user.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    """
    ORM model for the users table.

    Each user can own multiple uploaded documents.
    """

    __tablename__ = "users"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Display name
    name = Column(
        String(255),
        nullable=False,
    )

    # Email address
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # Bcrypt password hash.
    #
    # IMPORTANT:
    # The database column is called password_hash.
    password_hash = Column(
        String(255),
        nullable=False,
    )

    # Account status
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    # One user -> many documents
    documents = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} "
            f"name='{self.name}' "
            f"email='{self.email}'>"
        )