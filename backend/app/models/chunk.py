# app/models/chunk.py
#
# SQLAlchemy ORM model for the 'chunks' table.
#
# Each Chunk belongs to one Document and stores:
#   - the text content
#   - the position of the chunk
#   - the PDF page where the chunk came from
#   - the 384-dimensional embedding vector

from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from pgvector.sqlalchemy import Vector

from app.database.database import Base


class Chunk(Base):
    """
    ORM model for the 'chunks' table.

    Stores one text chunk from an uploaded document together with
    its page number and embedding.
    """

    __tablename__ = "chunks"

    # ---------------------------------------------------------
    # Primary key
    # ---------------------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ---------------------------------------------------------
    # Document relationship
    # ---------------------------------------------------------

    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    # ---------------------------------------------------------
    # Chunk position
    # ---------------------------------------------------------

    chunk_index = Column(
        Integer,
        nullable=False,
    )

    # ---------------------------------------------------------
    # PDF page number
    # ---------------------------------------------------------

    page_number = Column(
        Integer,
        nullable=True,
        index=True,
    )

    # ---------------------------------------------------------
    # Chunk text
    # ---------------------------------------------------------

    chunk_text = Column(
        Text,
        nullable=False,
    )

    # ---------------------------------------------------------
    # Embedding
    # ---------------------------------------------------------

    embedding = Column(
        Vector(384),
        nullable=True,
    )

    # ---------------------------------------------------------
    # Relationship
    # ---------------------------------------------------------

    document = relationship(
        "Document",
        back_populates="chunks",
    )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<Chunk id={self.id} "
            f"doc_id={self.document_id} "
            f"page={self.page_number} "
            f"index={self.chunk_index}>"
        )