import logging
import easyocr
import pytesseract
from PIL import Image
import io
import numpy as np

logger = logging.getLogger("indusmind-ai")

import threading

_reader = None
_reader_lock = threading.Lock()
_easy_ocr_failed = False

def _get_reader():
    global _reader, _easy_ocr_failed
    if _easy_ocr_failed:
        return None
    if _reader is None:
        with _reader_lock:
            if _reader is None and not _easy_ocr_failed:
                try:
                    logger.info("Initializing EasyOCR reader (lazy-loaded)...")
                    _reader = easyocr.Reader(['en'], gpu=False)
                    logger.info("EasyOCR reader initialized successfully.")
                except Exception as e:
                    logger.error(f"Failed to initialize EasyOCR: {e}")
                    _easy_ocr_failed = True
    return _reader

def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extracts text from an image utilizing a hybrid OCR pipeline:
    Attempts EasyOCR first -> Falls back to Tesseract.
    """
    extracted_text = ""
    
    try:
        # Load image via PIL to verify integrity
        image = Image.open(io.BytesIO(image_bytes))
        # Convert to RGB (required for some formats)
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        # Strategy 1: EasyOCR
        ocr_reader = _get_reader()
        if ocr_reader is not None:
            try:
                logger.debug("Attempting EasyOCR extraction.")
                # EasyOCR expects numpy array
                img_array = np.array(image)
                results = ocr_reader.readtext(img_array, detail=0)
                extracted_text = "\n".join(results)
                if extracted_text.strip():
                    logger.debug("EasyOCR extraction successful.")
                    return extracted_text.strip()
            except Exception as e:
                logger.warning(f"EasyOCR failed: {e}. Falling back to Tesseract.")
                
        # Strategy 2: Tesseract Fallback
        logger.debug("Attempting Tesseract OCR extraction.")
        extracted_text = pytesseract.image_to_string(image)
        logger.debug("Tesseract extraction finished.")
        return extracted_text.strip()
        
    except Exception as e:
        logger.error(f"OCR Pipeline failed completely: {e}", exc_info=True)
        return ""
