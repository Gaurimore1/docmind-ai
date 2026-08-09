# app/routers/upload.py

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends,
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.services.file_service import (
    save_upload_file,
)

from app.services.pdf_service import (
    extract_text_from_pdf,
)

from app.services.chunk_service import (
    chunk_pages,
)

from app.services.embedding_service import (
    generate_embeddings,
)

from app.services.database_service import (
    save_document_with_chunks,
)


router = APIRouter(tags=["Upload"])


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a PDF and process it through the complete pipeline:

    PDF
      ↓
    Save file
      ↓
    Extract text
      ↓
    Split into page-aware chunks
      ↓
    Generate embeddings
      ↓
    Store document + chunks + embeddings in PostgreSQL
    """

    # ---------------------------------------------------------
    # 1. Validate file type
    # ---------------------------------------------------------

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid file type '{file.content_type}'. "
                "Only PDF files are accepted."
            ),
        )

    # ---------------------------------------------------------
    # 2. Save uploaded PDF
    # ---------------------------------------------------------

    try:

        saved_path, file_size = await save_upload_file(file)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save uploaded file: {e}",
        )

    # ---------------------------------------------------------
    # 3. Extract PDF text
    # ---------------------------------------------------------

    try:

        extraction = extract_text_from_pdf(
            str(saved_path)
        )

    except RuntimeError as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    # ---------------------------------------------------------
    # 4. Create preview
    # ---------------------------------------------------------

    text_preview = (
        extraction["text"]
        .strip()
        [:500]
    )

    # ---------------------------------------------------------
    # 5. Create page-aware chunks
    # ---------------------------------------------------------

    try:

        chunks = chunk_pages(
            extraction["page_texts"]
        )

    except ValueError as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
    
    chunk_count = len(chunks)

    # ---------------------------------------------------------
    # 6. Extract only chunk text for embedding
    # ---------------------------------------------------------

    chunk_texts = [
        chunk["text"]
        for chunk in chunks
    ]

    # ---------------------------------------------------------
    # 7. Generate embeddings
    # ---------------------------------------------------------

    try:

        embeddings = generate_embeddings(
            chunk_texts
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate embeddings: {e}",
        )

    embeddings_generated = len(embeddings)

    # ---------------------------------------------------------
    # 8. Determine embedding dimension
    # ---------------------------------------------------------

    embedding_dimension = (
        len(embeddings[0])
        if embeddings
        else 0
    )

    # ---------------------------------------------------------
    # 9. Save everything to PostgreSQL
    # ---------------------------------------------------------

    try:

        document = save_document_with_chunks(
            db=db,
            filename=file.filename,
            chunks=chunks,
            embeddings=embeddings,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save document to database: {e}",
        )

    # ---------------------------------------------------------
    # 10. Return response
    # ---------------------------------------------------------

    return {
        "status": "success",
        "filename": file.filename,
        "document_id": document.id,
        "file_size": file_size,
        "pages": extraction["pages"],
        "chunks": chunk_count,
        "embedding_dimension": embedding_dimension,
        "embeddings_generated": embeddings_generated,
        "text_preview": text_preview,
    }