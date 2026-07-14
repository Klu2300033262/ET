from fastapi import APIRouter, UploadFile, File, HTTPException, status
import logging
from backend.app.config.constants import ALLOWED_MIME_TYPES, MAX_UPLOAD_SIZE_MB
from backend.app.services.document_service import process_document
from backend.app.models.document import DocumentIngestionResponse
from backend.app.models.base import BaseResponse

logger = logging.getLogger("indusmind-ai")
router = APIRouter()

@router.post(
    "/upload",
    response_model=BaseResponse[DocumentIngestionResponse],
    summary="Upload Industrial Document",
    description="Securely ingest, validate, and OCR-parse an industrial document."
)
async def upload_document(file: UploadFile = File(...)):
    """Handles the secure ingestion of document uploads."""
    
    # 1. Read bytes to determine size and content
    file_bytes = await file.read()
    file_size_mb = len(file_bytes) / (1024 * 1024)
    
    # 2. Maximum File Size Validation
    if file_size_mb > MAX_UPLOAD_SIZE_MB:
        logger.warning(f"Rejected upload: File size {file_size_mb:.2f}MB exceeds {MAX_UPLOAD_SIZE_MB}MB limit.")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_UPLOAD_SIZE_MB}MB."
        )
        
    # 3. MIME Type Validation
    mime_type = file.content_type
    if mime_type not in ALLOWED_MIME_TYPES:
        logger.warning(f"Rejected upload: Unsupported MIME type {mime_type}.")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {mime_type}. Allowed types: {list(ALLOWED_MIME_TYPES.keys())}"
        )
        
    # 4. Process Document (Hashing, Saving, Parsing, OCR)
    try:
        report = await process_document(file, file_bytes)
    except Exception as e:
        logger.error(f"Error during document processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the document: {str(e)}"
        )
        
    # 5. Return formatted standard response
    return BaseResponse(
        success=True,
        message="Document successfully processed and archived.",
        data=report
    )
