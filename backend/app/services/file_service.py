# utils/file_handler.py
# Handles all file I/O for uploads.
# Isolated here so swapping storage backends later (e.g. S3) only
# requires changes in this one file, not in any route code.

from pathlib import Path
from fastapi import UploadFile

# Build an absolute path to backend/uploads/ using this file's location.
# Path(__file__)                  = .../backend/app/utils/file_handler.py
# .parent                         = .../backend/app/utils/
# .parent.parent                  = .../backend/app/
# .parent.parent.parent           = .../backend/
# / "uploads"                     = .../backend/uploads/
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"


async def save_upload_file(file: UploadFile) -> tuple[Path, int]:
    """
    Save an uploaded file to the uploads/ directory.

    Returns:
        saved_path  — full Path of the written file
        file_size   — total bytes written
    """

    # Create uploads/ if it doesn't exist yet.
    # parents=True  — also create any missing parent directories.
    # exist_ok=True — don't raise an error if the folder is already there.
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Join the directory path with the original filename from the client.
    destination = UPLOAD_DIR / file.filename

    # Read all file bytes from the UploadFile stream.
    # 'await' is required — UploadFile.read() is async and must not block
    # the event loop while waiting on I/O.
    contents = await file.read()

    # Write bytes to disk.
    # "wb" = write binary mode, required for non-text formats like PDF.
    # The 'with' block guarantees the file handle closes even on errors.
    with open(destination, "wb") as f:
        f.write(contents)

    # Derive size from bytes already in memory — no extra disk stat call.
    file_size = len(contents)

    return destination, file_size
