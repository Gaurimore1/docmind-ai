# schemas/search.py
# Pydantic models for the semantic search endpoint.
#
# Why Pydantic?
#   FastAPI uses these models to automatically validate incoming request JSON
#   and serialize outgoing response JSON. Validation rules (min_length, ge/le)
#   are enforced before route handlers run — invalid requests get 422 with
#   detailed error messages, no route code executes.

from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    """
    Request body for the semantic search endpoint.

    The question is validated for non-emptiness, stripped of leading/trailing
    whitespace, and enforced to be at least 3 characters long.
    """

    # The user's natural language question.
    # Field(...) with Ellipsis means required — requests without this key get 422.
    # min_length=3 enforces a minimum after stripping (1- or 2-char questions
    # like "hi" are meaningless for semantic search and are rejected).
    # description appears in the auto-generated /docs OpenAPI spec.
    question: str = Field(
        ...,
        min_length=3,
        description="User's natural language question about the document"
    )

    # Custom validator for the question field.
    # Runs after type coercion but before the model instance is created.
    # The @classmethod decorator is required for all Pydantic validators.
    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        """
        Strip whitespace and reject empty strings.

        Args:
            value: The raw question string after Pydantic type coercion.

        Returns:
            The stripped question string.

        Raises:
            ValueError: If the question is empty or whitespace-only after stripping.
        """

        # Remove leading and trailing whitespace.
        # "  What is the refund policy?  " → "What is the refund policy?"
        stripped = value.strip()

        # Reject empty strings or strings that were only whitespace.
        # After stripping, "   " becomes "", which fails this check.
        # Raising ValueError here produces a 422 response with this message.
        if not stripped:
            raise ValueError("Question cannot be empty or whitespace-only.")

        # Return the cleaned value — the final SearchRequest.question field
        # will hold the stripped string, not the original input.
        return stripped


class SearchResult(BaseModel):
    """
    A single search result — one text chunk matched by semantic similarity.
    """

    # The original text chunk from the document that matched the query.
    # Required field with no validation beyond type checking.
    chunk_text: str = Field(
        ...,
        description="The matched text chunk from the document"
    )

    # The cosine similarity score between the query embedding and this chunk.
    # ge=0.0 (greater-or-equal) and le=1.0 (less-or-equal) enforce the valid
    # range for cosine similarity on text embeddings, which is typically [0, 1].
    # These constraints catch upstream calculation bugs where invalid scores
    # (e.g. > 1.0 or negative) would otherwise silently propagate.
    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Cosine similarity score (0.0 to 1.0, higher is more relevant)"
    )


class SearchResponse(BaseModel):
    """
    Response body for the semantic search endpoint.

    Contains a list of matched chunks sorted by similarity score descending.
    """

    # List of search results, one per matched chunk.
    # list[SearchResult] means Pydantic validates every element in the list
    # as a SearchResult instance — type safety all the way down.
    # default_factory=list provides a safe empty-list default so constructing
    # SearchResponse() with no arguments produces {"results": []} rather than
    # raising an error. This is production-safe for cases where retrieval finds
    # nothing or the document store is empty.
    # Using default_factory instead of default=[] avoids Python's mutable
    # default argument bug (where all instances would share the same list).
    results: list[SearchResult] = Field(
        default_factory=list,
        description="List of matching text chunks sorted by relevance (highest first)"
    )
