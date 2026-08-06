# services/embedding_service.py
# Responsible for generating vector embeddings from text chunks.
# Uses the Sentence Transformers library with the all-MiniLM-L6-v2 model.
#
# Design decision — module-level singleton:
#   Loading a transformer model is expensive (reads ~90MB of weights,
#   initialises tensor operations). We load it once when this module is
#   first imported and reuse the same instance for every call. This keeps
#   API response times fast after the initial server startup.

import logging

# SentenceTransformer handles everything: tokenisation, inference, and
# mean-pooling to produce a single fixed-size vector per input string.
from sentence_transformers import SentenceTransformer

# Module-scoped logger. Using __name__ scopes log output to
# 'app.services.embedding_service', making it easy to filter in production.
logger = logging.getLogger(__name__)

# The model name is defined as a constant so it can be changed in one place.
# all-MiniLM-L6-v2:
#   - Produces 384-dimensional embeddings
#   - Fast on CPU, good accuracy for semantic similarity tasks
#   - Downloaded automatically on first run and cached by HuggingFace
MODEL_NAME = "all-MiniLM-L6-v2"

# Log before loading so server startup logs show when the cost begins.
logger.info(f"Loading embedding model: {MODEL_NAME}...")

# Instantiate the model at module load time (when the app starts).
# The leading underscore signals this is module-private — callers should
# use generate_embeddings() and not access _model directly.
_model = SentenceTransformer(MODEL_NAME)

# Log after loading so the gap between these two lines shows startup cost.
logger.info("Embedding model loaded successfully.")


def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    """
    Generate vector embeddings for a list of text chunks.

    Each chunk is encoded into a 384-dimensional float vector using
    the all-MiniLM-L6-v2 model. The entire list is processed in a
    single batched call for efficiency.

    Args:
        chunks: A list of text strings to embed. Typically the output
                of chunk_service.chunk_text().

    Returns:
        A list of embeddings, one per input chunk. Each embedding is
        a list of 384 floats. Returns an empty list if input is empty.

    Example:
        embeddings = generate_embeddings(["Hello world", "FastAPI is great"])
        # embeddings[0] → [0.023, -0.14, 0.087, ...]  (384 floats)
    """

    # Return early for empty input — avoids a pointless model call and
    # makes the empty-list contract explicit to callers.
    if not chunks:
        return []

    # encode() accepts a list of strings and processes them in one
    # optimised batch — significantly faster than calling it in a loop.
    # show_progress_bar=False suppresses tqdm output that would pollute
    # server logs on every API request.
    # The result is a NumPy ndarray of shape (len(chunks), 384).
    embeddings = _model.encode(chunks, show_progress_bar=False)

    # .tolist() converts the NumPy ndarray to a plain Python list[list[float]].
    # This is required because NumPy arrays are not JSON-serialisable — FastAPI
    # would raise a serialisation error if we returned the raw ndarray.
    return embeddings.tolist()
