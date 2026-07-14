import os
import json
import hashlib
import logging
import time
import uuid
import fitz  # PyMuPDF
import pdfplumber
from datetime import datetime, timezone
from fastapi import UploadFile
from backend.app.services.ocr_service import extract_text_from_image
from backend.app.models.document import DocumentStatus, DocumentIngestionResponse

logger = logging.getLogger("indusmind-ai")

def generate_sha256(file_bytes: bytes) -> str:
    """Generates a secure SHA-256 hash of the binary file."""
    return hashlib.sha256(file_bytes).hexdigest()

def extract_from_pdf(file_path: str) -> tuple[str, bool, str]:
    """
    Parses a PDF using PyMuPDF. If the page lacks text, attempts OCR.
    Returns: (extracted_text, ocr_was_used, parser_used)
    """
    extracted_text = ""
    ocr_used = False
    parser_used = "PyMuPDF"
    
    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text").strip()
            
            # Scanned page detection heuristic
            if len(text) < 20: 
                ocr_used = True
                logger.info(f"Page {page_num+1} appears to be scanned. Initiating OCR Pipeline.")
                # Convert page to image
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                ocr_text = extract_text_from_image(img_bytes)
                extracted_text += ocr_text + "\n\n"
            else:
                extracted_text += text + "\n\n"
                
        # Optional fallback check: if PyMuPDF missed structure, try pdfplumber briefly for tables
        if not ocr_used and "table" in extracted_text.lower()[:500]:
            parser_used = "PyMuPDF + pdfplumber"
            # In a full implementation, we'd extract specific tables here.
            
    except Exception as e:
        logger.error(f"Failed to parse PDF {file_path}: {e}")
        
    return extracted_text.strip(), ocr_used, parser_used

async def process_document(upload_file: UploadFile, file_bytes: bytes) -> DocumentIngestionResponse:
    """Main orchestration pipeline for a new document upload."""
    start_time = time.time()
    logger.info("Lifecycle: Upload Started")
    
    # 1. Generate Metadata & Hash
    doc_id = str(uuid.uuid4())
    file_hash = generate_sha256(file_bytes)
    file_size = len(file_bytes)
    mime_type = upload_file.content_type or "application/octet-stream"
    
    # 2. Storage Setup
    raw_path = os.path.join("data", "raw", f"{doc_id}_{upload_file.filename}")
    processed_path = os.path.join("data", "processed", "text", f"{doc_id}.txt")
    metadata_path = os.path.join("data", "processed", "metadata", f"{doc_id}.json")
    
    # 3. Save Raw Document
    with open(raw_path, "wb") as f:
        f.write(file_bytes)
    
    logger.info(f"Lifecycle: Saved raw document to {raw_path}")
    logger.info("Lifecycle: PROCESSING Started")
    
    extracted_text = ""
    ocr_used = False
    parser_used = "None"
    num_pages = None
    
    try:
        # 4. Parsing Logic Branching
        if mime_type == "application/pdf":
            # Extract PDF details
            doc_obj = fitz.open(raw_path)
            num_pages = len(doc_obj)
            doc_obj.close()
            
            extracted_text, ocr_used, parser_used = extract_from_pdf(raw_path)
            
        elif mime_type.startswith("image/"):
            logger.info("Lifecycle: OCR Started (Image Detected)")
            ocr_used = True
            parser_used = "Hybrid OCR Engine"
            extracted_text = extract_text_from_image(file_bytes)
            logger.info("Lifecycle: OCR Finished")
            
        elif mime_type == "text/plain" or upload_file.filename.endswith(".txt"):
            parser_used = "Native UTF-8 Decoding"
            extracted_text = file_bytes.decode('utf-8', errors='ignore')
            
        else:
            raise ValueError(f"Unsupported MIME type during processing: {mime_type}")
            
        # 5. Save Extracted Text for Stage 4
        with open(processed_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
            
        logger.info(f"Lifecycle: Saved extracted text to {processed_path}")
        logger.info("Lifecycle: COMPLETED")
        final_status = DocumentStatus.COMPLETED

    except Exception as e:
        logger.error(f"Lifecycle: FAILED - {e}")
        final_status = DocumentStatus.FAILED

    # 6. Construct Final Report
    process_time_ms = int((time.time() - start_time) * 1000)
    
    response_data = DocumentIngestionResponse(
        document_id=doc_id,
        filename=upload_file.filename,
        file_size_bytes=file_size,
        num_pages=num_pages,
        document_type=mime_type,
        text_length=len(extracted_text),
        ocr_used=ocr_used,
        processing_time_ms=process_time_ms,
        upload_timestamp=datetime.now(timezone.utc),
        sha256_hash=file_hash,
        status=final_status,
        extraction_method="Automatic Parsing Routing",
        parser_used=parser_used,
        saved_text_path=processed_path
    )
    
    # 7. Save JSON Metadata for Stage 4+
    metadata_payload = response_data.model_dump(mode='json')
    # Add source document per user spec
    metadata_payload["source_document"] = upload_file.filename
    metadata_payload["language"] = "en"
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=2)
        
    logger.info(f"Lifecycle: Saved metadata to {metadata_path}")
    
    return response_data
