# app/services/chunk_service.py


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    """
    Split text into overlapping chunks.

    Returns:
        list[str]
    """

    if not text or not text.strip():
        return []

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            f"Invalid chunking parameters: "
            f"chunk_size={chunk_size}, "
            f"overlap={overlap}. "
            f"chunk_size must be > 0 and overlap must be >= 0 "
            f"and < chunk_size."
        )

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def chunk_pages(
    page_texts: list[str],
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:
    """
    Split PDF pages into overlapping chunks while preserving
    the original PDF page number.

    Returns:

        [
            {
                "text": "...",
                "page_number": 1
            },
            {
                "text": "...",
                "page_number": 2
            }
        ]
    """

    if not page_texts:
        return []

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            f"Invalid chunking parameters: "
            f"chunk_size={chunk_size}, "
            f"overlap={overlap}. "
            f"chunk_size must be > 0 and overlap must be >= 0 "
            f"and < chunk_size."
        )

    chunks = []

    for page_number, page_text in enumerate(page_texts, start=1):

        if not page_text or not page_text.strip():
            continue

        start = 0

        while start < len(page_text):

            end = start + chunk_size

            chunk = page_text[start:end]

            if chunk.strip():
                chunks.append(
                    {
                        "text": chunk,
                        "page_number": page_number,
                    }
                )

            start += chunk_size - overlap

    return chunks