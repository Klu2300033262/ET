from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
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

@router.get(
    "/",
    response_model=BaseResponse[list],
    summary="List Processed Documents",
    description="Returns metadata for all processed documents in the system."
)
async def list_documents():
    """Fetches all document metadata from the processed directory."""
    import os
    import json
    metadata_dir = "data/processed/metadata"
    docs = []
    
    if os.path.exists(metadata_dir):
        for filename in os.listdir(metadata_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(metadata_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        
                        # Add chunk count
                        doc_id = meta.get("document_id")
                        chunks_file = os.path.join("data", "processed", "chunks", str(doc_id), "chunks.json")
                        total_chunks = 0
                        if os.path.exists(chunks_file):
                            try:
                                with open(chunks_file, "r", encoding="utf-8") as cf:
                                    cdata = json.load(cf)
                                    total_chunks = len(cdata.get("chunks", []))
                            except Exception:
                                pass
                        meta["total_chunks"] = total_chunks
                        
                        # Normalize date field for frontend
                        meta["processed_at"] = meta.get("Processing Timestamp") or meta.get("upload_timestamp") or ""
                        
                        docs.append(meta)
                except Exception as e:
                    logger.error(f"Failed to read metadata file {filename}: {e}")
                    
    # Sort by processed_at descending
    docs.sort(key=lambda x: x.get("processed_at", ""), reverse=True)
    
    return BaseResponse(
        success=True,
        message=f"Retrieved {len(docs)} documents.",
        data=docs
    )

@router.get(
    "/{document_id}/chunks",
    response_model=BaseResponse[list],
    summary="Get Document Chunks",
    description="Returns the processed text chunks for a specific document."
)
async def get_document_chunks(document_id: str):
    """Fetches the extracted chunks from the filesystem."""
    import os
    import json
    chunks_file = os.path.join("data", "processed", "chunks", document_id, "chunks.json")
    
    if not os.path.exists(chunks_file):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chunks for document {document_id} not found. Ensure the document was fully processed."
        )
        
    try:
        with open(chunks_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            chunks = data.get("chunks", [])
            return BaseResponse(
                success=True,
                message=f"Retrieved {len(chunks)} chunks.",
                data=chunks
            )
    except Exception as e:
        logger.error(f"Failed to read chunks for {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document chunks."
        )

@router.delete(
    "/{document_id}",
    response_model=BaseResponse,
    summary="Delete Document",
    description="Deletes a document raw file, chunks, metadata, vector embeddings, and knowledge graph nodes."
)
async def delete_document_endpoint(document_id: str):
    """Orchestrates the complete deletion of a document from all database layers."""
    import os
    import shutil
    import json
    from backend.app.services.vector_store import vector_store
    from backend.app.services.neo4j_service import neo4j_db
    
    deleted_items = []
    
    # 1. Delete ChromaDB Embeddings
    try:
        if vector_store.collection:
            vector_store.collection.delete(where={"document_id": document_id})
            deleted_items.append("chromadb_embeddings")
    except Exception as e:
        logger.error(f"Failed to delete ChromaDB embeddings for {document_id}: {e}")
        
    # 2. Delete Neo4j Knowledge Graph Nodes
    try:
        if neo4j_db.is_online():
            neo4j_db.execute_write(
                "MATCH (n:IndustrialNode {source_document: $doc_id}) DETACH DELETE n",
                {"doc_id": document_id}
            )
            deleted_items.append("neo4j_nodes")
    except Exception as e:
        logger.error(f"Failed to delete Neo4j nodes for {document_id}: {e}")
        
    # 3. Delete Files (Raw, processed text, processed chunks, metadata)
    meta_path = os.path.join("data", "processed", "metadata", f"{document_id}.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                filename = meta.get("filename")
                if filename:
                    raw_file = os.path.join("data", "raw", f"{document_id}_{filename}")
                    if os.path.exists(raw_file):
                        os.remove(raw_file)
                        deleted_items.append("raw_file")
        except Exception as e:
            logger.error(f"Failed to parse metadata or delete raw file for {document_id}: {e}")
            
    # Delete text file
    txt_path = os.path.join("data", "processed", "text", f"{document_id}.txt")
    if os.path.exists(txt_path):
        try:
            os.remove(txt_path)
            deleted_items.append("extracted_text")
        except Exception:
            pass
            
    # Delete chunks directory
    chunks_dir = os.path.join("data", "processed", "chunks", document_id)
    if os.path.exists(chunks_dir):
        try:
            shutil.rmtree(chunks_dir)
            deleted_items.append("chunks_dir")
        except Exception:
            pass
            
    # Finally delete metadata file itself
    if os.path.exists(meta_path):
        try:
            os.remove(meta_path)
            deleted_items.append("metadata_file")
        except Exception:
            pass
            
    if not deleted_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found or already deleted."
        )
        
    return BaseResponse(
        success=True,
        message=f"Document {document_id} completely deleted.",
        data={"deleted_components": deleted_items}
    )

@router.get(
    "/{document_id}/download",
    summary="Download Original PDF",
    description="Downloads the original uploaded file from raw storage."
)
async def download_document(document_id: str):
    """Finds and returns the raw document file as a FileResponse."""
    import os
    import json
    meta_path = os.path.join("data", "processed", "metadata", f"{document_id}.json")
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="Document metadata not found.")
        
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            filename = meta.get("filename")
            if filename:
                raw_file = os.path.join("data", "raw", f"{document_id}_{filename}")
                if os.path.exists(raw_file):
                    return FileResponse(
                        path=raw_file,
                        filename=filename,
                        media_type=meta.get("document_type") or "application/octet-stream"
                    )
    except Exception as e:
        logger.error(f"Failed to load download for {document_id}: {e}")
        
    raise HTTPException(status_code=404, detail="Raw file not found on disk.")

@router.get(
    "/{document_id}/text",
    response_model=BaseResponse[dict],
    summary="Get Extracted Text",
    description="Returns the full extracted text for a specific document."
)
async def get_document_text(document_id: str):
    """Reads and returns the extracted text file."""
    import os
    txt_path = os.path.join("data", "processed", "text", f"{document_id}.txt")
    if not os.path.exists(txt_path):
        raise HTTPException(status_code=404, detail="Extracted text not found.")
    try:
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
            return BaseResponse(
                success=True,
                message="Extracted text retrieved successfully.",
                data={"text": text}
            )
    except Exception as e:
        logger.error(f"Failed to read text file for {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to read extracted text.")

@router.get(
    "/{document_id}",
    response_model=BaseResponse[dict],
    summary="Get Document Details",
    description="Returns metadata for a specific document by its ID."
)
async def get_document_details(document_id: str):
    """Fetches single document metadata from the processed directory."""
    import os
    import json
    meta_path = os.path.join("data", "processed", "metadata", f"{document_id}.json")
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found.")
        
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            
            # Add chunk count
            chunks_file = os.path.join("data", "processed", "chunks", document_id, "chunks.json")
            total_chunks = 0
            if os.path.exists(chunks_file):
                try:
                    with open(chunks_file, "r", encoding="utf-8") as cf:
                        cdata = json.load(cf)
                        total_chunks = len(cdata.get("chunks", []))
                except Exception:
                    pass
            meta["total_chunks"] = total_chunks
            meta["processed_at"] = meta.get("Processing Timestamp") or meta.get("upload_timestamp") or ""
            
            return BaseResponse(
                success=True,
                message="Document details retrieved.",
                data=meta
            )
    except Exception as e:
        logger.error(f"Failed to read metadata for {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve document details.")
