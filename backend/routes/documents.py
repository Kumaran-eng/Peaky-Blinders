import os
import shutil
import logging
from pathlib import Path

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends
)
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from ..config import UPLOAD_DIR
from ..admin_auth import require_admin
from ..database import get_db
from ..models import Document
from ..services.document_service import process_document

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)


# ============================================================
# ALLOWED FILE TYPES
# ============================================================

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt"
}


# ============================================================
# CREATE UPLOAD DIRECTORY
# ============================================================

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


@router.get("/view/{filename}", include_in_schema=False)
def view_evidence_document(filename: str, db: Session = Depends(get_db)):
    """Open an indexed source cited by the student chatbot."""
    safe_filename = Path(filename).name
    if safe_filename != filename:
        raise HTTPException(status_code=404, detail="Document not found.")

    document = (
        db.query(Document)
        .filter(Document.filename == safe_filename, Document.status == "indexed")
        .first()
    )
    file_path = Path(UPLOAD_DIR) / safe_filename
    if not document or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Document not found.")

    media_types = {
        ".pdf": "application/pdf",
        ".txt": "text/plain; charset=utf-8",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    return FileResponse(
        file_path,
        media_type=media_types.get(file_path.suffix.lower(), "application/octet-stream"),
        content_disposition_type="inline",
    )


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """
    Upload a PDF, DOCX, or TXT document.

    The uploaded document is:
    
    1. Saved to the uploads directory.
    2. Extracted.
    3. Split into chunks.
    4. Converted into embeddings.
    5. Stored in FAISS.
    """

    # --------------------------------------------------------
    # Check filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is missing"
        )


    # --------------------------------------------------------
    # Get file extension
    # --------------------------------------------------------

    extension = os.path.splitext(
        file.filename
    )[1].lower()


    # --------------------------------------------------------
    # Validate file type
    # --------------------------------------------------------

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Only PDF, DOCX and TXT files are allowed."
            )
        )


    # --------------------------------------------------------
    # Create safe filename
    # --------------------------------------------------------

    filename = os.path.basename(
        file.filename
    )


    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    if os.path.exists(file_path) or db.query(Document).filter(Document.filename == filename).first():
        raise HTTPException(
            status_code=409,
            detail="A document with this filename already exists. Rename it before uploading.",
        )


    # --------------------------------------------------------
    # Save uploaded file
    # --------------------------------------------------------

    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as exc:
        logger.exception("Failed to save uploaded document")

        raise HTTPException(
            status_code=500,
            detail="Failed to save the uploaded document."
        ) from exc


    # --------------------------------------------------------
    # Create database record
    # --------------------------------------------------------

    document = Document(
        filename=filename,
        file_type=extension,
        status="processing"
    )

    db.add(document)

    db.commit()

    db.refresh(document)


    # --------------------------------------------------------
    # Process document
    # --------------------------------------------------------

    try:

        result = process_document(
            file_path
        )


        # Update status

        document.status = "indexed"

        db.commit()


        return {

            "success": True,

            "message": (
                "Document uploaded and "
                "indexed successfully"
            ),

            "document_id": document.id,

            "filename": filename,

            "pages": result["pages"],

            "chunks": result["chunks"]

        }


    except (ValueError, FileNotFoundError) as exc:

        # ----------------------------------------------------
        # Update status if processing fails
        # ----------------------------------------------------

        document.status = "failed"

        db.commit()


        raise HTTPException(
            status_code=400,
            detail=f"Document processing failed: {exc}",
        ) from exc
    except Exception as exc:
        document.status = "failed"
        db.commit()
        logger.exception("Document indexing failed for %s", filename)
        raise HTTPException(
            status_code=500,
            detail="Document processing failed. Check that the server has its embedding model available.",
        ) from exc
