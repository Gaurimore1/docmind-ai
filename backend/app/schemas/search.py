# app/schemas/search.py

from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    """
    Request body for semantic document search.

    document_id is optional. When provided, the search is scoped to that
    specific document only. When omitted, all uploaded documents are searched.
    """

    question: str = Field(
        ...,
        min_length=3,
        description="Natural language question about the document",
    )

    document_id: int | None = Field(
        default=None,
        description=(
            "Selected document ID. "
            "If provided, search is restricted to that document only. "
            "If omitted, all uploaded documents are searched."
        ),
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Question cannot be empty or whitespace-only."
            )

        return value


class SearchResult(BaseModel):
    """
    Retrieved document chunk.
    """

    chunk_text: str

    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )

    chunk_index: int

    page_number: int


class Source(BaseModel):
    """
    Citation/source information for a retrieved chunk.
    """

    filename: str

    page_number: int

    chunk_index: int

    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )


class SearchResponse(BaseModel):
    """
    Complete RAG response.

    Contains the generated answer plus the document sources
    used to produce that answer.
    """

    answer: str

    sources: list[Source]

    results: list[SearchResult]