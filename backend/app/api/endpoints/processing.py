from fastapi import APIRouter, HTTPException, status
import logging
from backend.app.services.processing_service import process_document_pipeline
from backend.app.models.base import BaseResponse

logger = logging.getLogger("indusmind-ai")
router = APIRouter()

@router.post(
    "/{document_id}/process",
    response_model=BaseResponse,
    summary="Process and Chunk Document",
    description="Cleans, normalizes, and chunks a previously ingested document, preparing it for Embeddings (Stage 5)."
)
async def process_document_endpoint(document_id: str):
    """Triggers the Stage 4 Processing Pipeline."""
    try:
        result = process_document_pipeline(document_id)
        return BaseResponse(
            success=True,
            message="Document successfully cleaned and chunked.",
            data=result
        )
    except FileNotFoundError as e:
        logger.warning(f"Process triggered on missing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        logger.warning(f"Process triggered on invalid document content: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during document processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while chunking the document: {str(e)}"
        )
