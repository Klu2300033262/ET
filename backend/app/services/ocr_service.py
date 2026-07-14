import logging
import easyocr
import pytesseract
from PIL import Image
import io
import numpy as np

logger = logging.getLogger("indusmind-ai")

# Initialize EasyOCR reader securely (only English for now to keep memory low)
# This initialization happens once to avoid overhead per request
try:
    reader = easyocr.Reader(['en'], gpu=False)
    EASY_OCR_AVAILABLE = True
except Exception as e:
    logger.error(f"Failed to initialize EasyOCR: {e}")
    EASY_OCR_AVAILABLE = False

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
        if EASY_OCR_AVAILABLE:
            try:
                logger.debug("Attempting EasyOCR extraction.")
                # EasyOCR expects numpy array
                img_array = np.array(image)
                results = reader.readtext(img_array, detail=0)
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
