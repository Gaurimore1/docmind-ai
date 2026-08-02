# routers/upload.py
# Defines the HTTP route for PDF uploads.
# Routing logic only — file saving is delegated to utils/file_handler.py.

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.file_service import save_upload_file

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
    and return filename, size, and status.
    """

    # Reject anything that isn't a PDF before reading any bytes.
    # content_type is the MIME type sent by the client (e.g. application/pdf).
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Only PDF files are accepted."
        )

    # Hand off all disk I/O to the utility layer.
    saved_path, file_size = await save_upload_file(file)

    # Return a clean JSON response the client can use to confirm success.
    return {
        "status": "success",
        "filename": file.filename,
        "file_size_bytes": file_size,
        "saved_path": str(saved_path),
    }
