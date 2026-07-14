import logging
import os
from backend.app.config.settings import settings

def setup_logging():
    # Make sure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join("logs", "app.log")),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger("indusmind-ai")
    logger.info(f"Logging configured at {settings.LOG_LEVEL} level.")
    return logger
