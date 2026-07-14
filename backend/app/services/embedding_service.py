import logging
from typing import List, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("indusmind-ai")

class EmbeddingService:
    """
    Singleton service for generating vector embeddings locally.
    Implements Lazy Loading to ensure the large models only load into memory
    when an embedding request is actually made, speeding up server boot time.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance.model = None
        return cls._instance

    def _load_model(self):
        """Lazy loads the primary BAAI model, falls back to MiniLM if unavailable."""
        if self.model is None:
            logger.info("Lifecycle: Embedding Model Initialization Started")
            try:
                # Primary highly-optimized BAAI model
                logger.info("Attempting to load BAAI/bge-small-en-v1.5...")
                self.model = SentenceTransformer("BAAI/bge-small-en-v1.5")
                logger.info("Successfully loaded BAAI/bge-small-en-v1.5")
            except Exception as e:
                logger.warning(f"Failed to load BAAI model ({e}). Falling back to all-MiniLM-L6-v2.")
                try:
                    self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                    logger.info("Successfully loaded fallback model: all-MiniLM-L6-v2")
                except Exception as e_fallback:
                    logger.error(f"Critical Error: Fallback model also failed to load. {e_fallback}")
                    raise RuntimeError("No local embedding model could be loaded.")
            
    def generate_embedding(self, text: str) -> List[float]:
        """Generates a single embedding vector."""
        self._load_model()
        # sentence-transformers outputs a numpy array, convert to standard python list for JSON/Chroma
        return self.model.encode(text).tolist()

    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generates embeddings for a batch of strings efficiently."""
        self._load_model()
        logger.info(f"Generating embeddings for batch of {len(texts)} texts...")
        embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=False)
        return embeddings.tolist()

# Global singleton instance
embedding_service = EmbeddingService()
