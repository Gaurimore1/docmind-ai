# services/retrieval_service.py
# Responsible for semantic retrieval — converting a user question into an
# embedding and finding the most relevant text chunks via cosine similarity.
#
# Model sharing decision:
#   embedding_service.py already loads all-MiniLM-L6-v2 at startup.
#   We import that same instance (_model) directly instead of loading a
#   second copy. This saves ~90MB of RAM and eliminates redundant startup
#   latency. The underscore prefix is a convention, not an access lock.

import logging

# numpy is used to reshape Python lists into the 2D arrays that sklearn
# expects as input for cosine_similarity.
import numpy as np

# cosine_similarity computes the angle-based similarity between two sets
# of vectors in one vectorised operation — faster and cleaner than a loop.
from sklearn.metrics.pairwise import cosine_similarity

# Import the already-loaded model instance from embedding_service.
# Both services share the exact same object in memory — no second load.
from app.services.embedding_service import _model

# Module-scoped logger scoped to 'app.services.retrieval_service'.
logger = logging.getLogger(__name__)


def generate_question_embedding(question: str) -> list[float]:
    """
    Encode a single user question into a 384-dimensional embedding vector.

    Reuses the same SentenceTransformer model instance loaded by
    embedding_service — no additional memory or startup cost.

    Args:
        question: The user's natural language question as a plain string.

    Returns:
        A list of 384 floats representing the question's semantic meaning.
        Returns an empty list if the input is empty or whitespace-only.

    Example:
        vec = generate_question_embedding("What is the refund policy?")
        # vec → [0.045, -0.12, 0.083, ...]  (384 floats)
    """

    # Guard: empty or whitespace-only questions produce meaningless vectors.
    # Returning [] early lets callers handle this without try/except.
    if not question or not question.strip():
        return []

    # Encode a single string — passing str (not list[str]) returns a 1D
    # ndarray of shape (384,) rather than the 2D batch shape (1, 384).
    # show_progress_bar=False prevents tqdm output from polluting server logs.
    embedding = _model.encode(question, show_progress_bar=False)

    # Convert the 1D NumPy ndarray to a plain Python list[float].
    # Required for JSON serialisability; consistent with generate_embeddings().
    return embedding.tolist()


def find_most_similar_chunks(
    question_embedding: list[float],
    chunk_embeddings: list[list[float]],
    chunks: list[str],
    top_k: int = 3,
) -> list[dict]:
    """
    Find the top_k text chunks most semantically similar to a question.

    Uses cosine similarity to score every chunk against the question vector,
    then returns the highest-scoring results sorted in descending order.

    Args:
        question_embedding:  A single question vector — list of 384 floats.
                             Produced by generate_question_embedding().
        chunk_embeddings:    One vector per chunk — list of list[float].
                             Produced by embedding_service.generate_embeddings().
        chunks:              The original text strings that were embedded.
                             Must be the same length as chunk_embeddings.
        top_k:               Number of top results to return. Defaults to 3.
                             Clamped to len(chunks) if chunks is smaller.

    Returns:
        A list of dicts sorted by similarity_score descending:
        [
            {"chunk_text": "...", "similarity_score": 0.8731},
            ...
        ]
        Returns an empty list if any input is empty.

    Raises:
        ValueError: If len(chunk_embeddings) != len(chunks).
    """

    # Guard: if any input is empty we cannot compute meaningful results.
    # This handles PDFs with no extractable text or an unanswered question.
    if not question_embedding or not chunk_embeddings or not chunks:
        return []

    # Sanity check: the embedding list and the text list must be in sync.
    # A mismatch means something went wrong upstream (a bug, not user error).
    # Raising ValueError surfaces it immediately rather than silently
    # pairing the wrong text with the wrong score.
    if len(chunk_embeddings) != len(chunks):
        raise ValueError(
            f"Mismatch: {len(chunk_embeddings)} embeddings vs {len(chunks)} chunks. "
            "chunk_embeddings and chunks must have the same length."
        )

    # Wrap the flat question list in an outer list to create shape (1, 384).
    # cosine_similarity requires both inputs to be 2D arrays.
    # np.array([question_embedding]) → shape (1, 384)
    q_vector = np.array([question_embedding])

    # Convert the list of chunk vectors to a 2D NumPy array of shape (n, 384).
    # np.array(chunk_embeddings) with a list[list[float]] input produces (n, 384).
    c_matrix = np.array(chunk_embeddings)

    # Compute cosine similarity between the question and every chunk in one call.
    # Result shape is (1, n_chunks). [0] selects the single row → shape (n_chunks,).
    # Each score is in [-1.0, 1.0]; for text embeddings typically in [0.0, 1.0].
    scores = cosine_similarity(q_vector, c_matrix)[0]

    # Clamp top_k to the actual number of available chunks.
    # Without this, np.argsort slicing would silently return fewer results
    # than expected on short documents rather than raising an error.
    top_k_clamped = min(top_k, len(chunks))

    # np.argsort returns indices that sort scores in ascending order.
    # [::-1] reverses to descending (highest similarity first).
    # [:top_k_clamped] takes only as many as requested.
    top_indices = np.argsort(scores)[::-1][:top_k_clamped]

    # Build the result list from the top-ranked indices.
    # float(scores[i])    — converts NumPy float32 to Python float for JSON safety.
    # round(..., 4)       — 4 decimal places is precise without being noisy.
    # chunks[i]           — the original text string that produced this embedding.
    return [
        {
            "chunk_text": chunks[i],
            "similarity_score": round(float(scores[i]), 4),
        }
        for i in top_indices
    ]
