# services/chunk_service.py
# Responsible for splitting extracted PDF text into overlapping chunks.
# This is pure Python — no AI, no external libraries, no database.
#
# Why chunking?
#   Downstream components (vector stores, LLMs) have hard input size limits.
#   Splitting text into fixed-size pieces makes it compatible with those limits.
#
# Why overlap?
#   A sentence or paragraph that straddles a chunk boundary would be cut in
#   half without overlap. By repeating the last 'overlap' characters at the
#   start of the next chunk, we ensure every piece of meaning appears complete
#   in at least one chunk.


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    """
    Split a string into overlapping fixed-size chunks.

    Args:
        text:       The full extracted text to be chunked.
        chunk_size: Maximum number of characters per chunk. Default: 1000.
        overlap:    Number of characters shared between consecutive chunks.
                    Must be less than chunk_size. Default: 200.

    Returns:
        A list of text chunk strings. Returns an empty list if the input
        is empty or contains only whitespace.

    Raises:
        ValueError: If chunk_size <= 0, overlap < 0, or overlap >= chunk_size.
    """

    # Guard: return an empty list for None, "", or whitespace-only input.
    # A PDF of blank pages produces "\n\n\n" — strip() normalises that to "".
    # Returning [] is safer than raising; callers can handle it without try/except.
    if not text or not text.strip():
        return []

    # Guard: reject configurations that are logically impossible.
    # - chunk_size <= 0 would produce zero-length or negative slices.
    # - overlap < 0 makes no sense (negative shared region).
    # - overlap >= chunk_size means the window never advances — infinite loop.
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            f"Invalid chunking parameters: chunk_size={chunk_size}, overlap={overlap}. "
            f"chunk_size must be > 0 and overlap must be >= 0 and < chunk_size."
        )

    # List that will hold all produced chunks.
    # Typed explicitly as list[str] to make intent clear for static analysers.
    chunks: list[str] = []

    # 'start' is the index into 'text' where the current chunk begins.
    # It advances by (chunk_size - overlap) each iteration so consecutive
    # chunks share 'overlap' characters at their boundary.
    start = 0

    while start < len(text):

        # Calculate where this chunk ends.
        # If end exceeds len(text), Python slicing clamps it automatically —
        # no IndexError, it simply returns the remaining characters.
        end = start + chunk_size

        # Extract the chunk as a plain string slice.
        chunk = text[start:end]

        # Append the extracted chunk to the result list.
        chunks.append(chunk)

        # Advance the start position by (chunk_size - overlap).
        # Example with chunk_size=1000, overlap=200:
        #   Chunk 1: text[0:1000]
        #   Chunk 2: text[800:1800]   ← shares chars 800–999 with chunk 1
        #   Chunk 3: text[1600:2600]  ← shares chars 1600–1799 with chunk 2
        start += chunk_size - overlap

    return chunks
