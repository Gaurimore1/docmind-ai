# services/pdf_service.py
# Responsible for all PDF text extraction logic.
# This is the service layer — it sits between the route layer and raw
# library calls, keeping business logic out of the router.

# PyMuPDF is installed as the 'pymupdf' package but imported as 'fitz'.
# It is a C-extension that wraps the MuPDF rendering library, giving us
# fast, accurate access to PDF content.
import fitz


def extract_text_from_pdf(file_path: str) -> dict:
    """
    Open a PDF file, read every page, and return the extracted text
    along with the total page count.

    Args:
        file_path: Absolute or relative path to the PDF file on disk.

    Returns:
        {
            "pages": <int>   — total number of pages in the document,
            "text":  <str>   — all extracted text, pages separated by newlines
        }

    Raises:
        RuntimeError: If the file cannot be opened or text extraction fails.
    """
    try:
        # fitz.open() parses the PDF at file_path and returns a Document object.
        # Using it as a context manager ensures the file handle is released
        # automatically when the block exits, even if an exception occurs.
        with fitz.open(file_path) as doc:

            # len(doc) returns the total number of pages.
            # fitz.Document implements __len__ for exactly this purpose.
            total_pages = len(doc)

            # Iterate over every page in order.
            # Each 'page' is a fitz.Page object with methods for text, images, etc.
            # page.get_text() extracts the plain text layer of that page as a string.
            # The list comprehension collects one string per page.
            page_texts = [page.get_text() for page in doc]

            # Join all page strings with a newline so the final text is one
            # continuous string with a clear boundary between pages.
            extracted_text = "\n".join(page_texts)

        # Return the exact shape the caller expects.
        return {
            "pages": total_pages,
            "text": extracted_text,
        }

    except Exception as e:
        # Catch any error from fitz (corrupt PDF, file not found, permission
        # denied, etc.) and re-raise as a RuntimeError with a clear message.
        # This prevents raw fitz internals from leaking out of the service layer.
        raise RuntimeError(f"Failed to extract text from PDF '{file_path}': {e}") from e
