import os
import logging
from backend.app.config.settings import settings

logger = logging.getLogger("indusmind-ai")

def initialize_folders():
    """Ensure all required system directories exist on startup."""
    required_directories = [
        "logs",
        "data/raw",
        "data/processed",
        "data/ocr",
        "data/images",
        "data/logs",
        "data/temp",
        settings.CHROMA_PERSIST_DIR
    ]
    
    for directory in required_directories:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            raise
    
    logger.info("System directories initialized successfully.")
