"""
Note Generation Service
Uses AI to structure extracted content into study notes
"""
import logging
from typing import Dict, Optional
from app.services.ai_processor import AIProcessor

logger = logging.getLogger(__name__)


class NoteGenerator:
    """Generate structured notes from extracted content"""
    
    def __init__(self):
        self.ai_processor = AIProcessor()
        
        self.style_prompts = {
            "structured": """Convert this content into well-structured study notes:
- Create clear headings and subheadings
- Use bullet points for key concepts
- Preserve all mathematical expressions in LaTeX ($$...$$)
- Use markdown tables when information is comparative (definitions, differences, pros/cons, parameters)
- Keep inline equations in $...$ and standalone equations in $$...$$
- Remove redundant information
- Format as Markdown""",
            
            "cornell": """Convert this into Cornell-style notes:
**Cues (Left Column - Questions/Keywords):**
- Key questions
- Important terms

**Notes (Right Column - Main Content):**
- Detailed explanations
- Examples
- Math equations in LaTeX
- Add markdown tables for comparison-heavy topics

**Summary (Bottom):**
- Brief overview""",
            
            "outline": """Create an outline-style note:
I. Main Topic
   A. Subtopic
      1. Detail
      2. Detail
   B. Subtopic

Use LaTeX for math: $$equation$$
Use markdown tables where tabular format improves readability.""",
            
            "mindmap": """Create a mind map structure (text-based):
Central Concept
├─ Branch 1
│  ├─ Sub-branch 1.1
│  └─ Sub-branch 1.2
├─ Branch 2
└─ Branch 3

        Include math in LaTeX format.
        Where useful, add a compact markdown table summarizing key entities."""
        }
    
    async def generate(self, raw_content: Dict, style: str = "structured") -> Dict:
        """
        Generate structured notes
        
        Args:
            raw_content: Dict with 'text', 'images', 'metadata'
            style: Note style (structured, cornell, outline, mindmap)
            
        Returns:
            Dict with structured notes in different formats
        """
        try:
            text = raw_content.get('text', '')
            
            if not text.strip():
                return {"markdown": "No content to process", "html": "<p>No content</p>"}
            
            # Get style-specific prompt
            prompt = self.style_prompts.get(style, self.style_prompts["structured"])
            
            # Process with AI
            structured_markdown = await self.ai_processor.process_text(text, prompt)
            
            # Convert to HTML (simple conversion)
            html = self._markdown_to_html(structured_markdown)
            
            return {
                "markdown": structured_markdown,
                "html": html,
                "style": style,
                "word_count": len(structured_markdown.split())
            }
            
        except Exception as e:
            logger.error(f"Error generating notes: {str(e)}")
            raise
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """
        Simple markdown to HTML conversion
        (In production, use a proper library like markdown or mistune)
        """
        html = markdown_text
        
        # Headers
        html = html.replace('\n# ', '\n<h1>').replace('\n', '</h1>\n', 1)
        html = html.replace('\n## ', '\n<h2>').replace('\n', '</h2>\n', 1)
        html = html.replace('\n### ', '\n<h3>').replace('\n', '</h3>\n', 1)
        
        # Bold
        import re
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # Paragraphs
        html = '<p>' + html.replace('\n\n', '</p><p>') + '</p>'
        
        return html