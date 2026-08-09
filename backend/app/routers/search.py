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
):
    """
    Complete RAG search pipeline across ALL uploaded documents.

    Flow:

        User question
              ↓
        Question embedding
              ↓
        PostgreSQL + pgvector
              ↓
        Top relevant chunks from ALL documents
              ↓
        Build context
              ↓
        Ollama / Phi-3
              ↓
        Answer + sources
    """

    # ---------------------------------------------------------
    # STEP 1 — Generate question embedding
    # ---------------------------------------------------------

    question_embedding = generate_question_embedding(
        request.question
    )

    if not question_embedding:
        raise HTTPException(
            status_code=422,
            detail=(
                "Could not generate an embedding "
                "for the provided question."
            ),
        )

    # ---------------------------------------------------------
    # STEP 2 — Search PostgreSQL + pgvector
    # ---------------------------------------------------------
    #
    # IMPORTANT:
    # We no longer select only the latest document.
    #
    # search_chunks_by_embedding() now searches across
    # ALL uploaded documents.

    raw_results = search_chunks_by_embedding(
        db=db,
        query_embedding=question_embedding,
        top_k=5,
    )

    if not raw_results:
        raise HTTPException(
            status_code=404,
            detail=(
                "No relevant information found "
                "in the uploaded documents."
            ),
        )

    # ---------------------------------------------------------
    # STEP 3 — Build context for Ollama
    # ---------------------------------------------------------

    context_parts = []

    for result in raw_results:

        context_parts.append(
            (
                f"Document: {result['filename']}\n"
                f"Page: {result['page_number']}\n"
                f"Content:\n"
                f"{result['chunk_text']}"
            )
        )

    context = (
        "\n\n"
        "------------------------------"
        "\n\n"
    ).join(context_parts)

    # ---------------------------------------------------------
    # STEP 4 — Generate answer using Ollama
    # ---------------------------------------------------------

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
            detail=f"Failed to generate answer: {e}",
        )

    # ---------------------------------------------------------
    # STEP 5 — Build search results
    # ---------------------------------------------------------

    search_results = []

    for result in raw_results:

        search_results.append(
            SearchResult(
                chunk_text=result["chunk_text"],
                similarity_score=result["similarity_score"],
                chunk_index=result["chunk_index"],
                page_number=result["page_number"],
            )
        )

    # ---------------------------------------------------------
    # STEP 6 — Build source citations
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # STEP 7 — Return complete RAG response
    # ---------------------------------------------------------

    return SearchResponse(
        answer=answer,
        sources=sources,
        results=search_results,
    )