# models/document.py
# SQLAlchemy ORM model for the 'documents' table.
#
# This model represents one uploaded PDF document. It stores only metadata
# (filename, timestamp) — the actual text content and embeddings live in
# the related Chunk model to keep the documents table lean and fast.

# Column      — wraps a column definition in the ORM.
# Integer     — SQL INTEGER, used for the primary key.
# String      — SQL VARCHAR, used for the filename.
# DateTime    — SQL TIMESTAMP, used for the upload timestamp.
from sqlalchemy import Column, Integer, String, DateTime

# relationship() defines a Python-level association between two ORM models.
# It does not create a foreign key column — that lives in the Chunk model.
from sqlalchemy.orm import relationship

# func gives access to SQL functions. func.now() maps to SQL NOW() and
# is used as the server-side default for uploaded_at, ensuring the
# database clock is used rather than the application server clock.
from sqlalchemy.sql import func

# Base is the shared declarative registry. Every model that inherits from
# it is registered in Base.metadata, enabling Base.metadata.create_all()
# to create all tables in one call.
from app.database.database import Base


class Document(Base):
    """
    ORM model for the 'documents' table.

    Stores metadata for each uploaded PDF. The actual text chunks and
    their embeddings are stored in the related Chunk model.
    """

    # The SQL table name this class maps to.
    # SQLAlchemy uses this string when generating CREATE TABLE statements
    # and in all SQL queries produced by the ORM.
    __tablename__ = "documents"

    # ---------------------------------------------------------------------------
    # Columns
    # ---------------------------------------------------------------------------

    # Primary key. Integer primary keys in PostgreSQL are auto-incrementing
    # (SERIAL type). index=True creates a database index — explicit and
    # self-documenting even though PK indexes are automatic in PostgreSQL.
    id = Column(Integer, primary_key=True, index=True)

    # The original filename of the uploaded PDF.
    # String(255) maps to VARCHAR(255) — a safe upper bound for filenames.
    # nullable=False maps to NOT NULL; every document must have a filename.
    filename = Column(String(255), nullable=False)

    # The UTC timestamp when this document was uploaded.
    # func.now() is a server-side default — the database generates the
    # timestamp at insert time using its own clock. This is more reliable
    # than datetime.now() on the application server, especially in
    # distributed deployments where clocks may drift.
    # nullable=False ensures every row always has a timestamp.
    uploaded_at = Column(DateTime, default=func.now(), nullable=False)

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------

    # One-to-many: one Document has many Chunks.
    #
    # "Chunk" — string reference to the Chunk class, resolved lazily by
    #            SQLAlchemy at query time. Using a string avoids circular
    #            import errors between document.py and chunk.py.
    #
    # back_populates="document" — creates a bidirectional link. Accessing
    #            document.chunks returns a list of Chunk objects. On the
    #            Chunk side, chunk.document returns the parent Document.
    #            Both sides stay in sync automatically.
    #
    # cascade="all, delete-orphan" — when a Document is deleted, all its
    #            Chunks are deleted automatically (no orphaned rows).
    #            "delete-orphan" also deletes a Chunk if it is removed from
    #            document.chunks without being assigned to another Document.
    chunks = relationship(
        "Chunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    # ---------------------------------------------------------------------------
    # Representation
    # ---------------------------------------------------------------------------

    def __repr__(self) -> str:
        # Human-readable output for debugging and logging.
        # print(document) → <Document id=1 filename='annual_report.pdf'>
        return f"<Document id={self.id} filename='{self.filename}'>"
