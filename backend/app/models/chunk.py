# models/chunk.py
# SQLAlchemy ORM model for the 'chunks' table.
#
# Each Chunk belongs to one Document (many-to-one) and stores:
#   - the text slice produced by chunk_service.chunk_text()
#   - the position of that slice within the document
#   - the 384-dimensional embedding vector produced by embedding_service
#
# The Vector column type is provided by the pgvector PostgreSQL extension
# and its SQLAlchemy integration (pgvector.sqlalchemy). It enables native
# vector similarity search directly in SQL using pgvector's operators.

# Column     — wraps each field definition in the ORM.
# Integer    — SQL INTEGER, used for id, document_id, and chunk_index.
# Text       — SQL TEXT (unbounded), used for chunk_text. Unlike VARCHAR(n),
#              TEXT has no length cap — correct for variable-length chunks.
# ForeignKey — SQL FOREIGN KEY constraint. Enforces referential integrity:
#              every chunk must reference a real row in the documents table.
from sqlalchemy import Column, Integer, Text, ForeignKey

# relationship() creates the Python-level back-reference to Document.
# Combined with back_populates="chunks" on Document, this forms a fully
# bidirectional link without a second foreign key.
from sqlalchemy.orm import relationship

# Vector is provided by the pgvector SQLAlchemy integration.
# Vector(384) maps to PostgreSQL's vector(384) type — a fixed-length array
# of 384 floats. This enables pgvector's similarity operators:
#   <-> (L2/Euclidean distance)   ORDER BY embedding <-> query_vec
#   <=> (cosine distance)         ORDER BY embedding <=> query_vec
from pgvector.sqlalchemy import Vector

# Base is the shared declarative registry from database.py.
# Both Document and Chunk must import the exact same Base instance so
# SQLAlchemy can resolve their relationship and manage them as one schema.
from app.database.database import Base


class Chunk(Base):
    """
    ORM model for the 'chunks' table.

    Stores one text slice of an uploaded document along with its
    position index and pre-computed embedding vector.
    """

    # SQL table name. Lowercase plural, consistent with 'documents'.
    __tablename__ = "chunks"

    # ---------------------------------------------------------------------------
    # Columns
    # ---------------------------------------------------------------------------

    # Auto-incrementing primary key. Integer PKs in PostgreSQL use SERIAL,
    # which auto-increments on every INSERT. index=True is explicit and
    # self-documenting even though PK indexes are automatic in PostgreSQL.
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to documents.id. Enforces referential integrity at the
    # database level — PostgreSQL rejects any chunk whose document_id does
    # not match an existing row in the documents table.
    # nullable=False — every chunk must belong to a document.
    # index=True — creates a B-tree index on document_id so queries like
    # "all chunks for document 5" avoid a full table scan on large datasets.
    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    # The zero-based position of this chunk within its parent document.
    # Preserves the original sequence so chunks can be reassembled in order.
    # nullable=False — every chunk must have a known position.
    chunk_index = Column(Integer, nullable=False)

    # The actual text content of this chunk.
    # Text (SQL TEXT) is unbounded — no length cap is imposed. This is
    # correct for chunks that can be up to 1000 characters long.
    # nullable=False — a chunk with no text has no value.
    chunk_text = Column(Text, nullable=False)

    # The 384-dimensional embedding vector for this chunk.
    # Vector(384) maps to PostgreSQL's native vector(384) column type,
    # provided by the pgvector extension. Enables SQL-level similarity
    # search using pgvector operators without loading all vectors into Python.
    # nullable=True — embeddings are generated after the text row is saved,
    # so there is a brief window where the row exists without an embedding.
    # nullable=True prevents IntegrityError during that window.
    embedding = Column(Vector(384), nullable=True)

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------

    # Many-to-one: many Chunks belong to one Document.
    #
    # "Document" — string reference to the Document class, resolved lazily
    #              by SQLAlchemy at query time. Avoids circular import errors
    #              between chunk.py and document.py.
    #
    # back_populates="chunks" — the matching attribute on Document. Together
    #              they form a bidirectional link:
    #                chunk.document → the parent Document instance
    #                document.chunks → list of child Chunk instances
    #
    # No cascade here — cascades are always defined on the parent (Document)
    # side, not the child side. Document already has cascade="all, delete-orphan".
    document = relationship("Document", back_populates="chunks")

    # ---------------------------------------------------------------------------
    # Representation
    # ---------------------------------------------------------------------------

    def __repr__(self) -> str:
        # Shows the three most diagnostic fields for debugging and logging.
        # print(chunk) → <Chunk id=3 doc_id=1 index=2>
        return (
            f"<Chunk id={self.id} "
            f"doc_id={self.document_id} "
            f"index={self.chunk_index}>"
        )
