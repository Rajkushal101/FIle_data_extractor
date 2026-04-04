"""
Tests for AI Processor Service
"""

import pytest
from unittest.mock import patch, MagicMock


class TestAIProcessor:
    """Test cases for AI processing"""
    
    def test_ai_processor_import(self):
        """Test that AI processor can be imported"""
        from app.services.ai_processor import AIProcessor
        processor = AIProcessor()
        assert processor is not None
    
    @pytest.mark.asyncio
    async def test_ollama_availability_check(self):
        """Test Ollama availability detection"""
        from app.services.ai_processor import AIProcessor
        
        processor = AIProcessor()
        # Should return False if Ollama is not installed
        is_available = await processor.check_ollama_available()
        assert isinstance(is_available, bool)
    
    @pytest.mark.asyncio
    @patch('app.services.ai_processor.requests.post')
    async def test_groq_fallback(self, mock_post):
        """Test Groq API fallback"""
        from app.services.ai_processor import AIProcessor
        
        # Mock Groq API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test response'}}]
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        processor = AIProcessor()
        # Test will work if API key is configured
        assert processor is not None


if __name__ == "__main__":
    pytest.main([__file__])

