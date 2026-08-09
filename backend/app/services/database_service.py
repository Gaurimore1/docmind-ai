# app/services/database_service.py
#
# Database persistence layer for DocMind AI.
#
# Responsibilities:
#   1. Save a document and its chunks atomically.
#   2. Preserve the PDF page number for every chunk.
#   3. Retrieve the latest document's chunks.
#   4. Perform vector similarity search using PostgreSQL + pgvector.

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.chunk import Chunk


def save_document_with_chunks(
    db: Session,
    filename: str,
    chunks: list[dict],
    embeddings: list[list[float]],
) -> Document:
    """
    Save one document and all its chunks in a single transaction.

    Each chunk dictionary must contain:

        {
            "text": "...",
            "page_number": 1
        }

    The embeddings list must contain one embedding for every chunk.
    """

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    if len(chunks) != len(embeddings):
        raise ValueError(
            f"Mismatch: {len(chunks)} chunks vs "
            f"{len(embeddings)} embeddings. "
            "Both lists must have the same length."
        )

    try:

        # -----------------------------------------------------
        # Step 1 — Create Document
        # -----------------------------------------------------

        document = Document(
            filename=filename
        )

        db.add(document)

        # Flush so PostgreSQL generates document.id.
        # The transaction remains open.
        db.flush()

        # -----------------------------------------------------
        # Step 2 — Create Chunk rows
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # Step 3 — Commit everything atomically
        # -----------------------------------------------------

        db.commit()

        # Refresh the document so database-generated values
        # are available in Python.
        db.refresh(document)

        return document

    except Exception:

        # If anything fails, undo the entire transaction.
        db.rollback()

        raise


def get_latest_document_chunks(
    db: Session,
) -> tuple[list[str], list[list[float]]]:
    """
    Retrieve chunks and embeddings belonging to the latest document.

    This function is retained for compatibility with the current
    search pipeline.
    """

    # ---------------------------------------------------------
    # Step 1 — Find latest document
    # ---------------------------------------------------------

    document = (
        db.query(Document)
        .order_by(Document.uploaded_at.desc())
        .first()
    )

    if document is None:
        return [], []

    # ---------------------------------------------------------
    # Step 2 — Load chunks
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Step 3 — Extract text and embeddings
    # ---------------------------------------------------------

    chunk_texts = [
        row.chunk_text
        for row in chunk_rows
    ]

    chunk_embeddings = [
        row.embedding
        for row in chunk_rows
    ]

    return chunk_texts, chunk_embeddings


def search_chunks_by_embedding(
    db: Session,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[dict]:
    """
    Search across ALL uploaded documents using pgvector cosine distance.

    Returns up to top_k genuinely unique results. Deduplication happens
    at two levels:

    1. Database level  — we fetch top_k * 5 candidates so that after
       deduplication we still have enough unique results to fill top_k.

    2. Python level (primary) — deduplicate by chunk_text so that the
       same document uploaded multiple times never floods the results
       with semantically identical content.

    3. Python level (secondary) — deduplicate by (document_id, chunk_index)
       as a safety net against any unexpected query-level duplicates.

    Only chunks that have BOTH a non-null embedding AND a non-null
    page_number are searched, preserving backwards compatibility with
    older uploads that lack page numbers.
    """

    # cosine_distance(query_embedding) generates:
    #   chunks.embedding <=> '[0.1, 0.2, ...]'
    # Lower value = more similar (distance 0 = identical).
    distance = Chunk.embedding.cosine_distance(query_embedding)

    # Fetch a larger candidate pool (top_k * 5) so that after
    # deduplication by chunk_text we can still return top_k unique results.
    # We do NOT use DISTINCT here because SQLAlchemy DISTINCT with an
    # ORDER BY on a computed expression requires careful handling; it is
    # safer and clearer to deduplicate in Python after fetching.
    #
    # The join is a simple INNER JOIN on the PK — each Chunk row has
    # exactly one Document row, so no fanout / no duplicate rows from the join.
    #
    # Filters:
    #   Chunk.embedding.isnot(None)   — skip chunks without embeddings
    #   Chunk.page_number.isnot(None) — skip old chunks without page numbers
    candidate_limit = top_k * 5

    raw_rows = (
        db.query(
            Chunk,
            Document.filename,
            distance.label("distance"),
        )
        .join(Document, Chunk.document_id == Document.id)
        .filter(
            Chunk.embedding.isnot(None),
            Chunk.page_number.isnot(None),
        )
        .order_by(distance)
        .limit(candidate_limit)
        .all()
    )

    # -----------------------------------------------------------------
    # Deduplication — level 1: by chunk_text (semantic deduplication)
    # -----------------------------------------------------------------
    # When the same PDF is uploaded multiple times, every upload produces
    # chunks with identical text. After sorting by distance (best first),
    # we keep only the first occurrence of each unique chunk_text.
    # This ensures the top_k results contain genuinely different content.
    seen_texts: set[str] = set()

    # -----------------------------------------------------------------
    # Deduplication — level 2: by (document_id, chunk_index)
    # -----------------------------------------------------------------
    # Safety net against any unexpected duplicate rows from the query.
    seen_keys: set[tuple[int, int]] = set()

    unique_results: list[dict] = []

    for chunk, filename, distance_value in raw_rows:

        # Skip if this exact text has already been included.
        if chunk.chunk_text in seen_texts:
            continue

        # Skip if this (doc_id, chunk_index) pair has already been included.
        key = (chunk.document_id, chunk.chunk_index)
        if key in seen_keys:
            continue

        seen_texts.add(chunk.chunk_text)
        seen_keys.add(key)

        # cosine_distance returns a value in [0, 2].
        # similarity = 1 - distance maps it to [-1, 1].
        # For well-formed embeddings the result is in [0, 1].
        similarity = round(1.0 - float(distance_value), 4)
        # Clamp to [0, 1] to satisfy the Pydantic ge=0/le=1 constraint.
        similarity = max(0.0, min(1.0, similarity))

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

        if len(unique_results) >= top_k:
            break

    return unique_results