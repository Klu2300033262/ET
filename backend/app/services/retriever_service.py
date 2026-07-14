import time
import logging
from typing import List, Dict, Any, Optional
from backend.app.services.vector_store import vector_store
from backend.app.services.embedding_service import embedding_service

logger = logging.getLogger("indusmind-ai")

class RetrieverService:
    """
    Reusable retrieval service that abstracts away vector math.
    Designed for Stage 5 API, but easily consumable by Neo4j (Stage 6) 
    and LangGraph Agents (Stage 7).
    """
    
    def __init__(self, default_top_k: int = 5, default_threshold: float = 0.3):
        self.default_top_k = default_top_k
        self.default_threshold = default_threshold

    def search(
        self, 
        query: str, 
        top_k: Optional[int] = None, 
        document_id: Optional[str] = None,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes a semantic search against the Chroma database.
        """
        start_time = time.time()
        k = top_k or self.default_top_k
        min_score = threshold if threshold is not None else self.default_threshold
        
        logger.info(f"Lifecycle: Search Executed | Query: '{query[:50]}...'")
        
        # 1. Generate query embedding
        query_embedding = embedding_service.generate_embedding(query)
        
        # 2. Build Optional Metadata Filters
        where_filter = None
        if document_id:
            where_filter = {"document_id": document_id}
            
        # 3. Execute Vector Search
        results = vector_store.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        # 4. Format and Filter Results (Similarity Threshold)
        formatted_results = []
        
        if not results["ids"] or not results["ids"][0]:
            return []
            
        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        
        for i in range(len(ids)):
            # Chroma uses Cosine Distance by default (1 - Cosine Similarity). 
            # Lower distance = better match.
            # Convert to a standard similarity score (0.0 to 1.0)
            distance = distances[i]
            # Handle slight floating point errors
            similarity_score = max(0.0, 1.0 - distance)
            
            # Apply Threshold Filtering
            if similarity_score < min_score:
                continue
                
            formatted_results.append({
                "chunk_id": ids[i],
                "content": documents[i],
                "similarity_score": round(similarity_score, 4),
                "metadata": metadatas[i]
            })
            
        search_time_ms = int((time.time() - start_time) * 1000)
        logger.info(f"Lifecycle: Search Time: {search_time_ms}ms | Retrieved {len(formatted_results)} relevant chunks.")
        
        return formatted_results

# Global singleton
retriever_service = RetrieverService()
