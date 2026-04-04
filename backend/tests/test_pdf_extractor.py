"""
Tests for PDF Extractor Service
"""

import pytest
from pathlib import Path
import asyncio


class TestPDFExtractor:
    """Test cases for PDF extraction"""
    
    def test_pdf_extractor_import(self):
        """Test that PDF extractor can be imported"""
        from app.services.pdf_extractor import PDFExtractor
        extractor = PDFExtractor()
        assert extractor is not None
        assert extractor.dpi == 200
    
    @pytest.mark.asyncio
    async def test_extract_metadata(self):
        """Test metadata extraction"""
        from app.services.pdf_extractor import PDFExtractor
        import fitz
        
        extractor = PDFExtractor()
        # Create a minimal PDF for testing
        doc = fitz.open()
        doc.new_page()
        doc.set_metadata({"title": "Test PDF", "author": "Test Author"})
        
        metadata = extractor._extract_metadata(doc)
        assert metadata["title"] == "Test PDF"
        assert metadata["author"] == "Test Author"
        doc.close()
    
    def test_pdf_extractor_initialization(self):
        """Test that PDF extractor initializes correctly"""
        from app.services.pdf_extractor import pdf_extractor
        assert pdf_extractor is not None


if __name__ == "__main__":
    pytest.main([__file__])

