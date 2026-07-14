import os
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any

from backend.app.services.text_cleaner import clean_extracted_text
from backend.app.services.chunking_service import chunk_document_text

logger = logging.getLogger("indusmind-ai")

def calculate_nlp_metrics(text: str) -> Dict[str, Any]:
    """Generates basic NLP metadata metrics."""
    char_count = len(text)
    word_count = len(text.split())
    # Rough heuristic for sentences
    sentence_count = text.count('.') + text.count('!') + text.count('?')
    if sentence_count == 0 and word_count > 0:
        sentence_count = 1
        
    # Standard reading speed ~200 WPM
    reading_time_mins = max(1, round(word_count / 200))
    
    return {
        "Total Characters": char_count,
        "Total Words": word_count,
        "Total Sentences": sentence_count,
        "Estimated Reading Time": f"{reading_time_mins} min"
    }

def process_document_pipeline(document_id: str) -> Dict[str, Any]:
    """
    Main execution pipeline for Stage 4 Document Processing.
    Consumes raw Stage 3 outputs, cleans them, chunks them, and stores the results.
    """
    start_time = time.time()
    
    text_path = os.path.join("data", "processed", "text", f"{document_id}.txt")
    metadata_path = os.path.join("data", "processed", "metadata", f"{document_id}.json")
    
    # 1. Validation & Error Handling
    if not os.path.exists(text_path) or not os.path.exists(metadata_path):
        logger.error(f"Missing source files for document_id: {document_id}")
        raise FileNotFoundError(f"Source files missing for {document_id}")
        
    logger.info(f"[{document_id}] Lifecycle: Cleaning Started")
    
    # 2. Read Source Data
    with open(text_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_text = f.read()
        
    if not raw_text.strip():
        raise ValueError(f"Empty text found for document_id: {document_id}")
        
    with open(metadata_path, "r", encoding="utf-8") as f:
        original_metadata = json.load(f)
        
    # 3. Clean & Normalize
    clean_text = clean_extracted_text(raw_text)
    logger.info(f"[{document_id}] Lifecycle: Cleaning Finished")
    
    # 4. Generate Enhanced Metadata
    nlp_metrics = calculate_nlp_metrics(clean_text)
    enhanced_metadata = {**original_metadata, **nlp_metrics}
    enhanced_metadata["Document Category"] = "Uncategorized"  # Placeholder for future classification
    enhanced_metadata["Processing Timestamp"] = datetime.now(timezone.utc).isoformat()
    
    # 5. Intelligent Chunking
    logger.info(f"[{document_id}] Lifecycle: Chunking Started")
    try:
        chunks = chunk_document_text(clean_text)
    except Exception as e:
        logger.error(f"[{document_id}] Chunk Generation Failure: {e}")
        raise RuntimeError(f"Chunking failed: {e}")
        
    if not chunks:
        raise ValueError(f"No chunks generated for document_id: {document_id} (Very Short Document?)")
        
    logger.info(f"[{document_id}] Lifecycle: Chunking Finished")
    
    # 6. Chunk Storage
    chunk_dir = os.path.join("data", "processed", "chunks", document_id)
    os.makedirs(chunk_dir, exist_ok=True)
    
    # Store individual chunk txt files
    for chunk in chunks:
        chunk_filename = f"chunk_{chunk['chunk_number']:03d}.txt"
        chunk_path = os.path.join(chunk_dir, chunk_filename)
        with open(chunk_path, "w", encoding="utf-8") as f:
            f.write(chunk['content'])
            
    # Store master chunks.json
    chunks_json_path = os.path.join(chunk_dir, "chunks.json")
    
    # Embed the parent metadata into the chunk payload to make Stage 5 trivial
    final_payload = {
        "document_metadata": enhanced_metadata,
        "chunks": chunks
    }
    
    with open(chunks_json_path, "w", encoding="utf-8") as f:
        json.dump(final_payload, f, indent=2)
        
    logger.info(f"[{document_id}] Lifecycle: Metadata Saved")
    
    # 7. Processing Statistics
    chunk_sizes = [c['character_count'] for c in chunks]
    process_time_ms = int((time.time() - start_time) * 1000)
    
    stats = {
        "Total Chunks": len(chunks),
        "Average Chunk Size": sum(chunk_sizes) // len(chunks),
        "Largest Chunk": max(chunk_sizes),
        "Smallest Chunk": min(chunk_sizes),
        "Processing Time (ms)": process_time_ms,
        "Compression Ratio": f"{(len(clean_text) / max(1, len(raw_text))) * 100:.2f}%"
    }
    
    logger.info(f"[{document_id}] Lifecycle: Completed. Stats: {stats}")
    
    return {
        "document_id": document_id,
        "status": "CHUNKED",
        "statistics": stats
    }
