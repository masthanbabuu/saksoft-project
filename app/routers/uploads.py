"""Safe document upload endpoint."""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

router = APIRouter(tags=["uploads"])

MAX_FILE_BYTES = 2 * 1024 * 1024
UPLOAD_DIR = Path("data/uploads")

ALLOWED_TYPES = {
    "application/pdf": (".pdf", b"%PDF-"),
    "image/png": (".png", b"\x89PNG\r\n\x1a\n"),
}


def save_file(content: bytes, extension: str) -> str:
    """Store a document outside the async event loop."""
    UPLOAD_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"

    with (UPLOAD_DIR / filename).open("xb") as destination:
        destination.write(content)

    return filename


@router.post("/upload", status_code=201)
async def upload_file(file: UploadFile) -> dict[str, str | int]:
    """Validate and store an uploaded document."""
    try:
        allowed = ALLOWED_TYPES.get(file.content_type or "")

        if allowed is None:
            raise HTTPException(
                status_code=415,
                detail="Unsupported file type",
            )

        extension, signature = allowed
        content = await file.read(MAX_FILE_BYTES + 1)

        if len(content) > MAX_FILE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="File too large",
            )

        if not content.startswith(signature):
            raise HTTPException(
                status_code=415,
                detail="Invalid file content",
            )

        filename = await run_in_threadpool(save_file, content, extension)

        return {
            "filename": filename,
            "size": len(content),
        }
    finally:
        await file.close()
