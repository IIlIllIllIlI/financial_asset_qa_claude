"""RAG Upload API — POST /api/rag/upload."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api.schemas.rag import UploadResponse
from app.database.session import get_db
from app.services.rag_service import process_file
from app.utils.logger import setup_logger

logger = setup_logger("api.rag")
router = APIRouter(prefix="/api/rag", tags=["rag"])

ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt"}
KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent.parent.parent.parent / "knowledge_base"


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. Supported: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Save file
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = KNOWLEDGE_BASE_DIR / safe_name

    content = await file.read()
    file_path.write_bytes(content)

    try:
        result = await process_file(str(file_path), file.filename, db)
        return UploadResponse(**result)
    except Exception as e:
        logger.error(f"Upload processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
