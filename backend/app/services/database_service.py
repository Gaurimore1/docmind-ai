# app/services/database_service.py

"""
Database persistence and retrieval services for DocMind AI.

Responsibilities:
    1. Save documents and their chunks atomically.
    2. Associate every document with its owner.
    3. Preserve page numbers for every chunk.
    4. Retrieve the latest document's chunks.
    5. Perform pgvector similarity search.
    6. Restrict searches to the authenticated user's documents.
    7. Prevent duplicate chunks from flooding search results.
"""

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.chunk import Chunk


# =============================================================================
# DOCUMENT + CHUNK PERSISTENCE
# =============================================================================

def save_document_with_chunks(
    db: Session,
    filename: str,
    chunks: list[dict],
    embeddings: list[list[float]],
    user_id: int,
) -> Document:
    """
    Save one document and all of its chunks in a single transaction.

    Args:
        db:
            Active SQLAlchemy database session.

        filename:
            Original uploaded PDF filename.

        chunks:
            Page-aware chunk dictionaries.

            Each chunk must contain:

                {
                    "text": "...",
                    "page_number": 1
                }

        embeddings:
            One embedding vector for every chunk.

        user_id:
            ID of the authenticated user who uploaded the document.

    Returns:
        The newly created Document ORM object.

    Raises:
        ValueError:
            If the number of chunks and embeddings do not match.

        Exception:
            Any database exception is rolled back and re-raised.
    """

    # -------------------------------------------------------------------------
    # Validate chunk / embedding alignment
    # -------------------------------------------------------------------------

    if len(chunks) != len(embeddings):
        raise ValueError(
            f"Mismatch: {len(chunks)} chunks vs "
            f"{len(embeddings)} embeddings. "
            "Both lists must have the same length."
        )

    # -------------------------------------------------------------------------
    # Create everything inside one transaction
    # -------------------------------------------------------------------------

    try:

        # ---------------------------------------------------------------------
        # Step 1 — Create document
        # ---------------------------------------------------------------------

        document = Document(
            filename=filename,
            user_id=user_id,
        )

        db.add(document)

        # Flush so PostgreSQL generates document.id.
        #
        # The transaction is still open at this point.
        db.flush()

        # ---------------------------------------------------------------------
        # Step 2 — Create chunk rows
        # ---------------------------------------------------------------------

        chunk_objects = []

        for index, (chunk_data, embedding) in enumerate(
            zip(chunks, embeddings)
        ):

            chunk = Chunk(
                document_id=document.id,
                chunk_index=index,
                page_number=chunk_data["page_number"],
                chunk_text=chunk_data["text"],
                embedding=embedding,
            )

            chunk_objects.append(chunk)

        db.add_all(chunk_objects)

        # ---------------------------------------------------------------------
        # Step 3 — Commit atomically
        # ---------------------------------------------------------------------

        db.commit()

        # Refresh so database-generated values are available.
        db.refresh(document)

        return document

    except Exception:

        # If anything fails, undo the entire transaction.
        db.rollback()

        raise


# =============================================================================
# LATEST DOCUMENT CHUNKS
# =============================================================================

def get_latest_document_chunks(
    db: Session,
) -> tuple[list[str], list[list[float]]]:
    """
    Retrieve chunks and embeddings belonging to the latest document.

    This function is retained for compatibility with the existing project.
    """

    # -------------------------------------------------------------------------
    # Step 1 — Find latest document
    # -------------------------------------------------------------------------

    document = (
        db.query(Document)
        .order_by(Document.uploaded_at.desc())
        .first()
    )

    if document is None:
        return [], []

    # -------------------------------------------------------------------------
    # Step 2 — Load chunks in their original order
    # -------------------------------------------------------------------------

    chunk_rows = (
        db.query(Chunk)
        .filter(
            Chunk.document_id == document.id
        )
        .order_by(
            Chunk.chunk_index.asc()
        )
        .all()
    )

    # -------------------------------------------------------------------------
    # Step 3 — Extract parallel lists
    # -------------------------------------------------------------------------

    chunk_texts = [
        row.chunk_text
        for row in chunk_rows
    ]

    chunk_embeddings = [
        row.embedding
        for row in chunk_rows
    ]

    return chunk_texts, chunk_embeddings


# =============================================================================
# VECTOR SEARCH
# =============================================================================

def search_chunks_by_embedding(
    db: Session,
    query_embedding: list[float],
    top_k: int = 5,
    document_id: int | None = None,
    user_id: int | None = None,
) -> list[dict]:
    """
    Search document chunks using pgvector cosine distance.

    Security:
        When user_id is provided, ONLY documents owned by that user
        are searched.

    Scope:
        - user_id=None:
            All documents are searched.
        - user_id provided:
            Only that user's documents are searched.
        - document_id provided:
            Search is additionally restricted to that document.

    Returns:
        Up to top_k unique search results.

    Each result contains:

        {
            "chunk_text": str,
            "similarity_score": float,
            "chunk_index": int,
            "page_number": int,
            "document_id": int,
            "filename": str
        }
    """

    # -------------------------------------------------------------------------
    # Validate inputs
    # -------------------------------------------------------------------------

    if not query_embedding:
        return []

    if top_k <= 0:
        return []

    # -------------------------------------------------------------------------
    # Calculate cosine distance
    #
    # pgvector:
    #
    #     0.0 = identical
    #     higher = less similar
    #
    # We later convert this to:
    #
    #     similarity = 1.0 - distance
    # -------------------------------------------------------------------------

    distance = Chunk.embedding.cosine_distance(
        query_embedding
    )

    # -------------------------------------------------------------------------
    # Fetch a larger candidate pool.
    #
    # We need extra candidates because some results may be duplicates.
    # -------------------------------------------------------------------------

    candidate_limit = max(top_k * 5, top_k)

    # -------------------------------------------------------------------------
    # Base query
    # -------------------------------------------------------------------------

    query = (
        db.query(
            Chunk,
            Document.filename,
            distance.label("distance"),
        )
        .join(
            Document,
            Chunk.document_id == Document.id,
        )
        .filter(
            Chunk.embedding.isnot(None),
            Chunk.page_number.isnot(None),
        )
    )

    # -------------------------------------------------------------------------
    # SECURITY FILTER
    #
    # This is the important multi-user boundary.
    #
    # Even if a user guesses another document's ID, this condition prevents
    # chunks belonging to another user from being returned.
    # -------------------------------------------------------------------------

    if user_id is not None:
        query = query.filter(
            Document.user_id == user_id
        )

    # -------------------------------------------------------------------------
    # Optional document-specific filtering
    # -------------------------------------------------------------------------

    if document_id is not None:
        query = query.filter(
            Chunk.document_id == document_id
        )

    # -------------------------------------------------------------------------
    # Rank by cosine distance.
    #
    # Lower distance = more similar.
    #
    # Chunk.id provides a deterministic secondary ordering when two chunks
    # have exactly the same distance.
    # -------------------------------------------------------------------------

    query = (
        query
        .order_by(
            distance.asc(),
            Chunk.id.asc(),
        )
        .limit(candidate_limit)
    )

    rows = query.all()

    # -------------------------------------------------------------------------
    # Python-level deduplication
    #
    # Primary key:
    #     chunk_text
    #
    # This prevents repeated uploads of the same PDF from flooding the
    # response with logically identical chunks.
    #
    # Secondary key:
    #     (document_id, chunk_index)
    #
    # This protects against unexpected duplicate database rows.
    # -------------------------------------------------------------------------

    seen_texts: set[str] = set()
    seen_chunk_keys: set[tuple[int, int]] = set()

    unique_results: list[dict] = []

    for chunk, filename, distance_value in rows:

        # ---------------------------------------------------------------------
        # Skip duplicate text
        # ---------------------------------------------------------------------

        normalized_text = chunk.chunk_text.strip()

        if normalized_text in seen_texts:
            continue

        # ---------------------------------------------------------------------
        # Skip duplicate physical chunk keys
        # ---------------------------------------------------------------------

        chunk_key = (
            chunk.document_id,
            chunk.chunk_index,
        )

        if chunk_key in seen_chunk_keys:
            continue

        seen_texts.add(normalized_text)
        seen_chunk_keys.add(chunk_key)

        # ---------------------------------------------------------------------
        # Convert cosine distance to similarity
        # ---------------------------------------------------------------------

        similarity = round(
            1.0 - float(distance_value),
            4,
        )

        # Pydantic SearchResult expects [0, 1].
        similarity = max(
            0.0,
            min(1.0, similarity),
        )

        # ---------------------------------------------------------------------
        # Build result
        # ---------------------------------------------------------------------

        unique_results.append(
            {
                "chunk_text": chunk.chunk_text,
                "similarity_score": similarity,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "document_id": chunk.document_id,
                "filename": filename,
            }
        )

        # Stop once enough unique results have been collected.
        if len(unique_results) >= top_k:
            break

    return unique_results