# routers/search.py
# Defines the semantic search endpoint.
# Routing logic only — all retrieval logic is delegated to retrieval_service.py
# and all storage access is delegated to memory_store.py.

from fastapi import APIRouter, HTTPException

# Import all three Pydantic models for this endpoint:
#   SearchRequest  — validates and cleans the incoming JSON body
#   SearchResult   — shape of each individual matched chunk
#   SearchResponse — wrapper that FastAPI serialises as the JSON response
from app.schemas.search import SearchRequest, SearchResponse, SearchResult

# get_chunks() and get_embeddings() read from the module-level dict that
# upload.py populated via save_document(). No arguments needed.
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.database_service import get_latest_document_chunks
# generate_question_embedding() converts the question string to a 384-dim vector.
# find_most_similar_chunks() ranks stored chunks by cosine similarity and
# returns the top-k most relevant results.
from app.services.retrieval_service import (
    generate_question_embedding,
    find_most_similar_chunks,
)

# APIRouter isolates these routes from main.py.
# 'tags' groups this endpoint under "Search" in the Swagger UI at /docs,
# separate from the "Upload" group.
router = APIRouter(tags=["Search"])


@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    db: Session = Depends(get_db),
):
    """
    Perform semantic search over the currently uploaded document.

    Accepts a natural language question, finds the top 3 most relevant
    text chunks using cosine similarity on pre-computed embeddings, and
    returns them sorted by relevance score (highest first).

    The request body is validated by SearchRequest before this handler runs:
    - question must be non-empty, stripped of whitespace, and >= 3 chars.

    Returns 404 if no document has been uploaded yet.
    Returns 422 if the question cannot be embedded (unexpected edge case).
    """

    # Read the stored chunks from the in-memory document store.
    # Returns [] if no document has been uploaded and save_document() has
    # never been called. Always safe — never raises.
    # Read the latest document's chunks and embeddings from PostgreSQL.
    chunks, embeddings = get_latest_document_chunks(db)

    # If either list is empty, no document has been uploaded.
    if not chunks or not embeddings:
        raise HTTPException(
            status_code=404,
            detail="No document found. Please upload a PDF before searching."
        )

    # Convert the validated, stripped question string into a 384-dimensional
    # embedding vector using the same SentenceTransformer model that was used
    # to embed the document chunks at upload time.
    # request.question is already clean — validated and stripped by SearchRequest.
    question_embedding = generate_question_embedding(request.question)

    # Defensive guard: generate_question_embedding() returns [] for empty input.
    # SearchRequest already prevents empty questions, so this should never
    # trigger in normal operation. It is here as a belt-and-suspenders check.
    # 422 is appropriate — the issue is with the request content, not the server.
    if not question_embedding:
        raise HTTPException(
            status_code=422,
            detail="Could not generate an embedding for the provided question."
        )

    # Rank all stored chunks by cosine similarity to the question vector.
    # top_k=3 is explicit here (not relying on the default) for readability —
    # a code reader can see the limit without checking the function signature.
    # Returns list[dict] where each dict has "chunk_text" and "similarity_score".
    raw_results = find_most_similar_chunks(
        question_embedding=question_embedding,
        chunk_embeddings=embeddings,
        chunks=chunks,
        top_k=3,
    )

    # Convert each raw result dict into a validated SearchResult instance.
    # **result unpacks {"chunk_text": ..., "similarity_score": ...} as kwargs.
    # Pydantic validates each instance — if similarity_score is outside [0, 1],
    # a ValidationError is raised here rather than silently returning bad data.
    search_results = [SearchResult(**result) for result in raw_results]

    # Wrap the list in a SearchResponse and return it.
    # FastAPI uses response_model=SearchResponse to serialise this as JSON:
    # {"results": [{"chunk_text": "...", "similarity_score": 0.87}, ...]}
    return SearchResponse(results=search_results)
