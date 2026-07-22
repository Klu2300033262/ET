import os

from backend.app.config.settings import settings

# Models Configuration
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
GEMINI_LLM_MODEL = settings.GEMINI_LLM_MODEL
GEMINI_FALLBACK_MODEL = settings.GEMINI_FALLBACK_MODEL
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", 5))

# Parsing Parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# File Configurations
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "tiff", "bmp", "txt"}
MAX_UPLOAD_SIZE_MB = 200

# Strict MIME Type Validation
ALLOWED_MIME_TYPES = {
    "application/pdf": "pdf",
    "image/png": "png",
    "image/jpeg": "jpeg",
    "image/tiff": "tiff",
    "image/bmp": "bmp",
    "text/plain": "txt"
}
