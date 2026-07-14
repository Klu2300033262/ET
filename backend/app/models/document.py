from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class DocumentStatus(str, Enum):
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    OCR = "OCR"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class DocumentIngestionResponse(BaseModel):
    """Response returned when a document is fully ingested."""
    document_id: str = Field(..., description="Unique identifier for the document")
    filename: str = Field(..., description="Original filename")
    file_size_bytes: int = Field(..., description="Size of the file in bytes")
    num_pages: Optional[int] = Field(None, description="Number of pages (if applicable)")
    document_type: str = Field(..., description="MIME type of the document")
    text_length: int = Field(..., description="Total extracted text length (characters)")
    ocr_used: bool = Field(False, description="Whether OCR was triggered")
    processing_time_ms: int = Field(..., description="Total processing time in milliseconds")
    upload_timestamp: datetime = Field(..., description="When the upload occurred")
    sha256_hash: str = Field(..., description="SHA-256 hash of the original file")
    status: DocumentStatus = Field(..., description="Final processing status")
    extraction_method: str = Field(..., description="The primary parser/engine used")
    saved_text_path: str = Field(..., description="Path to the raw extracted text file")
