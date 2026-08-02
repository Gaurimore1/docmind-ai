# routers/upload.py
# Defines the HTTP route for PDF uploads.
# Routing logic only — file saving is delegated to file_service.py
# and text extraction is delegated to pdf_service.py.

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.file_service import save_upload_file
# Import the extraction function from the service layer.
# The router calls it by name — it has no knowledge of PyMuPDF internals.
from app.services.pdf_service import extract_text_from_pdf

# APIRouter isolates these routes from main.py.
# 'tags' groups this endpoint under "Upload" in the Swagger UI at /docs.
router = APIRouter(tags=["Upload"])


@router.post("/upload")
async def upload_pdf(
    # UploadFile streams the file without loading it all into memory at once.
    # File(...) marks it as required — missing file returns 422 automatically.
    file: UploadFile = File(...)
):
    """
    Accept a PDF file, save it to the uploads/ directory,
    extract its text, and return upload status, filename,
    total pages, and a 500-character text preview.
    """

    # Reject anything that isn't a PDF before reading any bytes.
    # content_type is the MIME type sent by the client (e.g. application/pdf).
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Only PDF files are accepted."
        )

    # Hand off all disk I/O to the service layer.
    # saved_path is a pathlib.Path object; file_size is the byte count.
    saved_path, file_size = await save_upload_file(file)

    # Call the PDF text extraction service.
    # str(saved_path) converts the Path object to a plain string because
    # extract_text_from_pdf() and fitz.open() both expect a string path.
    # This runs after saving is confirmed — a failed save would have
    # raised an exception before reaching this line.
    try:
        extraction = extract_text_from_pdf(str(saved_path))
    except RuntimeError as e:
        # The file saved successfully but could not be parsed.
        # Return 500 with the specific reason rather than a generic crash.
        raise HTTPException(status_code=500, detail=str(e))

    # extraction is {"pages": int, "text": str}
    # .strip() removes leading/trailing whitespace and stray newlines
    # that often appear at the start of a PDF's first page.
    # [:500] slices the first 500 characters for the preview.
    text_preview = extraction["text"].strip()[:500]

    # Return a clean JSON response with exactly the four fields requested.
    return {
        "status": "success",
        "filename": file.filename,
        "pages": extraction["pages"],
        "text_preview": text_preview,
    }
