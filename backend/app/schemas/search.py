# app/schemas/search.py

from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    """
    Request body for semantic document search.
    """

    question: str = Field(
        ...,
        min_length=3,
        description="Natural language question about the document",
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