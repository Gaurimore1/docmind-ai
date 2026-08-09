# app/services/pdf_service.py

import fitz


def extract_text_from_pdf(file_path: str) -> dict:
    """
    Extract text from every PDF page.

    Returns:
        {
            "pages": int,
            "text": str,
            "page_texts": list[str]
        }
    """

    try:
        with fitz.open(file_path) as doc:

            total_pages = len(doc)

            page_texts = [
                page.get_text()
                for page in doc
            ]

            extracted_text = "\n".join(page_texts)

        return {
            "pages": total_pages,
            "text": extracted_text,
            "page_texts": page_texts,
        }

    except Exception as e:
        raise RuntimeError(
            f"Failed to extract text from PDF '{file_path}': {e}"
        ) from e