# app/routers/search.py

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
)

from sqlalchemy.orm import Session

from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    Source,
)

from app.database.database import get_db

from app.models.document import Document
from app.models.user import User

from app.services.auth_dependency import (
    get_current_user,
)

from app.services.database_service import (
    search_chunks_by_embedding,
)

from app.services.retrieval_service import (
    generate_question_embedding,
)

from app.services.llm_service import (
    generate_answer,
)


router = APIRouter(tags=["Search"])


@router.post(
    "/search",
    response_model=SearchResponse,
)
async def search(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Complete authenticated RAG search pipeline.

    Flow:

        JWT
         ↓
        Current user
         ↓
        Optional document validation
         ↓
        Question embedding
         ↓
        User-owned documents only
         ↓
        pgvector similarity search
         ↓
        Top relevant chunks
         ↓
        Build context
         ↓
        Ollama / Phi-3
         ↓
        Answer + sources
    """

    # -------------------------------------------------------------------------
    # STEP 1 — Validate selected document
    # -------------------------------------------------------------------------
    #
    # If document_id is provided, verify BOTH:
    #
    #     1. The document exists.
    #     2. The document belongs to the authenticated user.
    #
    # This prevents ID guessing / cross-user document access.
    # -------------------------------------------------------------------------

    if request.document_id is not None:

        document_exists = (
            db.query(Document.id)
            .filter(
                Document.id == request.document_id,
                Document.user_id == current_user.id,
            )
            .first()
        )

        if document_exists is None:

            raise HTTPException(
                status_code=404,
                detail="Selected document was not found.",
            )

    # -------------------------------------------------------------------------
    # STEP 2 — Generate question embedding
    # -------------------------------------------------------------------------

    try:

        question_embedding = generate_question_embedding(
            request.question
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to generate question embedding: "
                f"{e}"
            ),
        )

    if not question_embedding:

        raise HTTPException(
            status_code=422,
            detail=(
                "Could not generate an embedding "
                "for the provided question."
            ),
        )

    # -------------------------------------------------------------------------
    # STEP 3 — Search PostgreSQL + pgvector
    #
    # user_id is ALWAYS passed.
    #
    # This means global search means:
    #
    #     all documents belonging to THIS USER
    #
    # and never all documents in the entire database.
    # -------------------------------------------------------------------------

    raw_results = search_chunks_by_embedding(
        db=db,
        query_embedding=question_embedding,
        top_k=5,
        document_id=request.document_id,
        user_id=current_user.id,
    )

    if not raw_results:

        raise HTTPException(
            status_code=404,
            detail=(
                "No relevant information found "
                "in your uploaded documents."
            ),
        )

    # -------------------------------------------------------------------------
    # STEP 4 — Build context for Ollama
    # -------------------------------------------------------------------------

    context_parts = []

    for result in raw_results:

        context_parts.append(
            (
                f"Document: {result['filename']}\n"
                f"Page: {result['page_number']}\n"
                f"Chunk: {result['chunk_index']}\n"
                f"Content:\n"
                f"{result['chunk_text']}"
            )
        )

    context = (
        "\n\n"
        "------------------------------"
        "\n\n"
    ).join(context_parts)

    # -------------------------------------------------------------------------
    # STEP 5 — Generate answer using Ollama
    # -------------------------------------------------------------------------

    try:

        answer = generate_answer(
            question=request.question,
            context=context,
        )

    except RuntimeError as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to generate answer: "
                f"{e}"
            ),
        )

    # -------------------------------------------------------------------------
    # STEP 6 — Build SearchResult objects
    # -------------------------------------------------------------------------

    results = []

    for result in raw_results:

        results.append(
            SearchResult(
                chunk_text=result["chunk_text"],
                similarity_score=result["similarity_score"],
                chunk_index=result["chunk_index"],
                page_number=result["page_number"],
            )
        )

    # -------------------------------------------------------------------------
    # STEP 7 — Build source citations
    # -------------------------------------------------------------------------

    sources = []

    for result in raw_results:

        sources.append(
            Source(
                filename=result["filename"],
                page_number=result["page_number"],
                chunk_index=result["chunk_index"],
                similarity_score=result["similarity_score"],
            )
        )

    # -------------------------------------------------------------------------
    # STEP 8 — Return final response
    # -------------------------------------------------------------------------

    return SearchResponse(
        answer=answer,
        sources=sources,
        results=results,
    )