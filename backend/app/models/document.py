# app/models/document.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Document(Base):
    """
    ORM model for the documents table.

    Each document belongs to exactly one authenticated user.
    """

    __tablename__ = "documents"

    # Primary key.
    id = Column(Integer, primary_key=True, index=True)

    # Original uploaded filename.
    filename = Column(String(255), nullable=False)

    # Database-generated upload timestamp.
    uploaded_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    # Owner of this document.
    #
    # ForeignKey ensures the user must exist in the users table.
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # Relationship to the User model.
    user = relationship(
        "User",
        back_populates="documents",
    )

    # One document -> many chunks.
    chunks = relationship(
        "Chunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Document id={self.id} "
            f"filename='{self.filename}' "
            f"user_id={self.user_id}>"
        )