import os
import logging
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from backend.app.services.embedding_service import embedding_service

logger = logging.getLogger("indusmind-ai")

class VectorStoreService:
    """Manages all interactions with the local persistent ChromaDB vector store."""
    
    def __init__(self):
        # Initialize persistent client targeting our Stage 5 data directory
        db_path = os.path.abspath(os.path.join("data", "chromadb"))
        os.makedirs(db_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # We store everything in a master 'documents' collection
        self.collection = self.client.get_or_create_collection(
            name="indusmind_documents",
            metadata={"hnsw:space": "cosine"} # Cosine similarity is standard for bge models
        )
        
    def check_document_exists(self, document_id: str) -> bool:
        """Embedding Cache Mechanism: Checks if a document's chunks are already in the DB."""
        # Query chromadb to see if any chunk has this document_id in its metadata
        results = self.collection.get(
            where={"document_id": document_id},
            limit=1
        )
        return len(results.get("ids", [])) > 0
        
    def ingest_chunks(self, document_metadata: Dict[str, Any], chunks: List[Dict[str, Any]]) -> bool:
        """
        Embeds and stores chunks. 
        Returns True if newly ingested, False if skipped (cache hit).
        """
        document_id = document_metadata.get("document_id")
        
        # 1. Embedding Cache Check
        if self.check_document_exists(document_id):
            logger.info(f"[{document_id}] Embeddings already exist in ChromaDB. Skipping generation.")
            return False
            
        logger.info(f"[{document_id}] Lifecycle: Embedding Started")
        
        # 2. Prepare Data for Batch Generation
        texts = [chunk["content"] for chunk in chunks]
        chunk_ids = [chunk["chunk_id"] for chunk in chunks]
        
        # 3. Batch Generate Embeddings
        embeddings = embedding_service.generate_embeddings_batch(texts)
        
        # 4. Prepare Metadata
        # Chroma requires metadata values to be str, int, float, or bool.
        clean_doc_metadata = {}
        for k, v in document_metadata.items():
            if isinstance(v, (str, int, float, bool)):
                clean_doc_metadata[k] = v
            else:
                clean_doc_metadata[k] = str(v)
                
        # Merge chunk-specific metadata with document metadata
        metadatas = []
        for chunk in chunks:
            meta = clean_doc_metadata.copy()
            meta["chunk_id"] = chunk["chunk_id"]
            meta["chunk_number"] = chunk["chunk_number"]
            meta["start_offset"] = chunk["start_offset"]
            metadatas.append(meta)
            
        # 5. Store in Chroma
        # We batch add to avoid limits, though Chroma can handle 40k+ items in one add.
        logger.info(f"[{document_id}] Lifecycle: Embedding Finished. Saving to ChromaDB...")
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        logger.info(f"[{document_id}] Lifecycle: Saved to Chroma")
        
        return True

# Global singleton
vector_store = VectorStoreService()
