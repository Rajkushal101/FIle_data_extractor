"""
PDF Extraction Service
Handles text and image extraction from PDF files using PyMuPDF
"""

import fitz  # PyMuPDF
import io
from PIL import Image
from pathlib import Path
from typing import List, Dict, Any
import logging

from app.services.math_detector import find_math_regions, math_detector
from app.services.image_extractor import extract_text_from_image

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract content from PDF files"""
    
    def __init__(self):
        self.dpi = 200  # Resolution for image extraction
        
    async def extract(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract all content from PDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary containing extracted text, images, and metadata
        """
        doc = None
        try:
            doc = fitz.open(str(file_path))
            page_count = len(doc)

            result = {
                'text': '',
                'pages': [],
                'metadata': self._extract_metadata(doc),
                'page_count': page_count
            }

            for page_num in range(page_count):
                page_content = await self._extract_page(doc, page_num)
                result['pages'].append(page_content)
                result['text'] += page_content['text'] + '\n\n---\n\n'

            logger.info(f"Successfully extracted {page_count} pages from PDF")
            return result

        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            raise
        finally:
            if doc is not None:
                doc.close()
    
    async def _extract_page(self, doc: fitz.Document, page_num: int) -> Dict[str, Any]:
        """Extract content from a single page"""
        page = doc[page_num]
        
        # Extract text
        text = page.get_text("text")
        
        # Find potential math regions
        math_regions = find_math_regions(page)
        
        # Extract images and math regions
        images = []
        math_content = []
        
        # Process embedded images
        image_list = page.get_images()
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Convert to PIL Image
                pil_image = Image.open(io.BytesIO(image_bytes))
                
                images.append({
                    'index': img_index,
                    'size': pil_image.size,
                    'format': pil_image.format
                })
                
            except Exception as e:
                logger.warning(f"Could not extract image {img_index}: {str(e)}")
        
        # Process math regions
        for region_index, bbox in enumerate(math_regions):
            try:
                # Render region as image
                pix = page.get_pixmap(clip=bbox, dpi=self.dpi)
                img_bytes = pix.tobytes("png")
                
                # OCR the math region
                math_text = await extract_text_from_image(img_bytes)
                
                if math_text.strip():
                    math_content.append({
                        'region': region_index,
                        'bbox': list(bbox),
                        'content': math_text
                    })
                    
                    # Add to page text
                    text += f"\n\n[Math Region {region_index}]\n{math_text}\n"
                    
            except Exception as e:
                logger.warning(f"Could not process math region {region_index}: {str(e)}")
        
        return {
            'page_number': page_num + 1,
            'text': text,
            'images': images,
            'math_content': math_content,
            'math_expressions': math_detector.extract_math_expressions(text)
        }
    
    def _extract_metadata(self, doc: fitz.Document) -> Dict[str, Any]:
        """Extract PDF metadata"""
        metadata = doc.metadata
        return {
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'subject': metadata.get('subject', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'modification_date': metadata.get('modDate', '')
        }


# Singleton instance
pdf_extractor = PDFExtractor()


async def extract_pdf(file_path: Path) -> Dict[str, Any]:
    """
    Convenience function for PDF extraction
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted content dictionary
    """
    return await pdf_extractor.extract(file_path)
