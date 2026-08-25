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

from app.models.user import User

from app.services.auth_dependency import (
    get_current_user,
)

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
    current_user: User = Depends(get_current_user),
):
    """
    Upload a PDF and process it through the complete pipeline.

    Pipeline:

        Authenticated user
              ↓
        PDF upload
              ↓
        Save file
              ↓
        Extract text
              ↓
        Page-aware chunking
              ↓
        Generate embeddings
              ↓
        Save document with user_id
              ↓
        Save chunks + embeddings
    """

    # -------------------------------------------------------------------------
    # 1. Validate file type
    # -------------------------------------------------------------------------

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid file type '{file.content_type}'. "
                "Only PDF files are accepted."
            ),
        )

    # -------------------------------------------------------------------------
    # 2. Save uploaded PDF
    # -------------------------------------------------------------------------

    try:

        saved_path, file_size = await save_upload_file(
            file
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save uploaded file: {e}",
        )

    # -------------------------------------------------------------------------
    # 3. Extract PDF text
    # -------------------------------------------------------------------------

    try:

        extraction = extract_text_from_pdf(
            str(saved_path)
        )

    except RuntimeError as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    # -------------------------------------------------------------------------
    # 4. Create text preview
    # -------------------------------------------------------------------------

    text_preview = (
        extraction["text"]
        .strip()
        [:500]
    )

    # -------------------------------------------------------------------------
    # 5. Create page-aware chunks
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # 6. Extract chunk text for embedding
    # -------------------------------------------------------------------------

    chunk_texts = [
        chunk["text"]
        for chunk in chunks
    ]

    # -------------------------------------------------------------------------
    # 7. Generate embeddings
    # -------------------------------------------------------------------------

    try:

        embeddings = generate_embeddings(
            chunk_texts
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate embeddings: {e}",
        )

    embeddings_generated = len(
        embeddings
    )

    # -------------------------------------------------------------------------
    # 8. Determine embedding dimension
    # -------------------------------------------------------------------------

    embedding_dimension = (
        len(embeddings[0])
        if embeddings
        else 0
    )

    # -------------------------------------------------------------------------
    # 9. Validate chunk / embedding count
    # -------------------------------------------------------------------------

    if chunk_count != embeddings_generated:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Chunk/embedding mismatch: "
                f"{chunk_count} chunks but "
                f"{embeddings_generated} embeddings generated."
            ),
        )

    # -------------------------------------------------------------------------
    # 10. Save document + chunks + embeddings
    #
    # IMPORTANT:
    #
    # current_user.id is the authenticated owner's ID.
    #
    # This is what connects the uploaded document to the user.
    # -------------------------------------------------------------------------

    try:

        document = save_document_with_chunks(
            db=db,
            filename=file.filename,
            chunks=chunks,
            embeddings=embeddings,
            user_id=current_user.id,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to save document to database: "
                f"{e}"
            ),
        )

    # -------------------------------------------------------------------------
    # 11. Return response
    # -------------------------------------------------------------------------

    return {
        "status": "success",
        "filename": file.filename,
        "document_id": document.id,
        "user_id": current_user.id,
        "file_size": file_size,
        "pages": extraction["pages"],
        "chunks": chunk_count,
        "embedding_dimension": embedding_dimension,
        "embeddings_generated": embeddings_generated,
        "text_preview": text_preview,
    }