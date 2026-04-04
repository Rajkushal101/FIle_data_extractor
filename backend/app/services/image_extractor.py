"""
Image OCR Extraction Service
Uses AI models for text and math extraction
"""
import logging
from typing import Dict
import base64

from app.services.ai_processor import AIProcessor
from app.services.math_detector import math_detector

logger = logging.getLogger(__name__)


class ImageExtractor:
    """Extract text from images using OCR"""
    
    def __init__(self):
        self.ai_processor = AIProcessor()
    
    async def extract(self, file_path: str) -> Dict:
        """
        Extract content from image file
        
        Args:
            file_path: Path to image file
            
        Returns:
            Dict with extracted text
        """
        try:
            # Read image and convert to base64
            with open(file_path, 'rb') as f:
                img_bytes = f.read()
            
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            # Use AI to extract text and math
            prompt = """Extract all text and mathematical equations from this image.
            
For math equations, output them in LaTeX format like: $$equation$$
For regular text, output as plain text.
Preserve the structure and layout as much as possible."""
            
            extracted_text = await self.ai_processor.process_image(
                img_base64,
                prompt
            )
            
            return {
                "text": extracted_text,
                "math_expressions": math_detector.extract_math_expressions(extracted_text),
                "math_text": math_detector.to_math_text(extracted_text),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error extracting image: {e}")
            return {
                "text": "",
                "success": False,
                "error": str(e)
            }


# Singleton instance
image_extractor = ImageExtractor()


async def extract_text_from_image(image_bytes: bytes) -> str:
    """Extract text from image bytes"""
    import tempfile
    import os
    
    try:
        # Save bytes to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name
        
        # Extract text
        result = await image_extractor.extract(tmp_path)
        
        # Cleanup
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        
        return result.get("text", "")
    except Exception as e:
        logger.error(f"Error in extract_text_from_image: {e}")
        return ""
