from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int

class DocumentCreate(DocumentBase):
    pass

class DocumentMetadata(BaseModel):
    author: Optional[str] = None
    created_date: Optional[str] = None
    page_count: int
    source_url: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: str
    status: str  # pending, processing, completed, failed
    metadata: DocumentMetadata
    created_at: datetime
    updated_at: datetime

class DocumentChunk(BaseModel):
    id: str
    document_id: str
    page_number: int
    text_content: str
    chunk_index: int
    metadata: Dict[str, Any] = {}
