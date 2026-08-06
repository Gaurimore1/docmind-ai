# routers/upload.py
# Defines the HTTP route for PDF uploads.
# Routing logic only — file saving is delegated to file_service.py
# and text extraction is delegated to pdf_service.py.
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.database_service import save_document_with_chunks
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.file_service import save_upload_file
# Import the extraction function from the service layer.
# The router calls it by name — it has no knowledge of PyMuPDF internals.
from app.services.pdf_service import extract_text_from_pdf
# Import the chunking function from the service layer.
# The router calls it to split extracted text into fixed-size overlapping pieces.
from app.services.chunk_service import chunk_text
# Import the embedding function from the service layer.
# The router calls it to generate a vector for every chunk.
from app.services.embedding_service import generate_embeddings
# Import the store function to persist chunks and embeddings in memory.
# The router calls it after embeddings are generated so the query endpoint
# can retrieve them later without re-processing the document.


# APIRouter isolates these routes from main.py.
# 'tags' groups this endpoint under "Upload" in the Swagger UI at /docs.
router = APIRouter(tags=["Upload"])


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Accept a PDF file, save it to the uploads/ directory, extract its
    text, chunk it, generate embeddings, and return upload metadata.
    The full embedding vectors are not returned — only counts and dimension.
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

    # Pass the full extracted text to chunk_text().
    # chunk_text() uses chunk_size=1000 and overlap=200 by default.
    # It returns a list[str] — one entry per chunk.
    chunks = chunk_text(extraction["text"])

    # len(chunks) gives the total number of chunks produced.
    # This is what goes into the "chunks" key of the response.
    chunk_count = len(chunks)

    # Pass all chunks to generate_embeddings() in a single batched call.
    # Returns list[list[float]] — one 384-dimensional vector per chunk.
    # We store the full result to derive metadata but do NOT put it in the
    # response: returning raw vectors would add ~1500 floats per chunk to
    # the JSON payload, making it huge and meaningless for the client here.
    embeddings = generate_embeddings(chunks)

    # Count how many vectors were actually produced by the model.
    # Computed from the real output rather than chunk_count so it honestly
    # reflects what generate_embeddings() returned.
    embeddings_generated = len(embeddings)

    # Read the dimension from the first vector in the list.
    # all-MiniLM-L6-v2 always produces 384-dimensional vectors.
    # The 'if embeddings else 0' guard prevents an IndexError on empty PDFs
    # where generate_embeddings() returned [] and embeddings[0] would crash.
    embedding_dimension = len(embeddings[0]) if embeddings else 0

    # Persist chunks and embeddings to the in-memory store so the query
    # endpoint can retrieve them without re-processing the document.
    # save_document() raises ValueError if inputs are empty or mismatched —
    # both are internal pipeline failures, so we surface them as HTTP 500.
    # We catch only ValueError (not bare Exception) so unexpected errors
    # still produce a full traceback rather than a swallowed 500 message.
      # Save the document, chunks, and embeddings to PostgreSQL.
    try:
        save_document_with_chunks(
            db=db,
            filename=file.filename,
            chunks=chunks,
            embeddings=embeddings,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Return a clean JSON response.
    return {
        "status": "success",
        "filename": file.filename,
        "pages": extraction["pages"],
        "chunks": chunk_count,
        "embedding_dimension": embedding_dimension,
        "embeddings_generated": embeddings_generated,
        "text_preview": text_preview,
    }