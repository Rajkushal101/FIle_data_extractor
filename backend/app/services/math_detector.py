"""
Math Detection Service
Identifies mathematical content in extracted text/images
"""
import logging
import re
from typing import List, Dict

logger = logging.getLogger(__name__)


class MathDetector:
    """Detect and extract mathematical content"""
    
    def __init__(self):
        # Common math symbols and patterns
        self.math_patterns = [
            r'\$\$.*?\$\$',  # LaTeX display math
            r'\$.*?\$',      # LaTeX inline math
            r'\\[a-zA-Z]+',  # LaTeX commands
            r'[∫∑∏√∂∇×÷±≤≥≠≈∞]',  # Math symbols
            r'\b(sin|cos|tan|log|ln|exp)\b',  # Math functions
        ]
        
        self.compiled_patterns = [re.compile(p, re.DOTALL) for p in self.math_patterns]
    
    def detect_math_regions(self, text: str) -> List[Dict]:
        """
        Detect mathematical content in text
        
        Returns:
            List of dicts with math content and positions
        """
        math_regions = []
        
        for pattern in self.compiled_patterns:
            for match in pattern.finditer(text):
                math_regions.append({
                    "content": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "type": "latex" if match.group().startswith(('$', '\\')) else "symbol"
                })
        
        return math_regions
    
    def has_math_content(self, text: str) -> bool:
        """Quick check if text contains math"""
        return any(pattern.search(text) for pattern in self.compiled_patterns)

    def extract_math_expressions(self, text: str) -> List[str]:
        """Extract unique math expressions from text while preserving order."""
        regions = sorted(self.detect_math_regions(text), key=lambda item: item["start"])
        expressions: List[str] = []
        seen = set()

        for region in regions:
            content = region["content"].strip()
            if not content or content in seen:
                continue
            seen.add(content)
            expressions.append(content)

        return expressions

    def latex_to_plain_text(self, expr: str) -> str:
        """Convert common LaTeX/math symbols to readable text."""
        text = expr.strip()
        if text.startswith("$$") and text.endswith("$$"):
            text = text[2:-2]
        elif text.startswith("$") and text.endswith("$"):
            text = text[1:-1]

        replacements = {
            r"\\frac": "frac",
            r"\\sqrt": "sqrt",
            r"\\sum": "sum",
            r"\\int": "integral",
            r"\\prod": "product",
            r"\\leq": "<=",
            r"\\geq": ">=",
            r"\\neq": "!=",
            r"\\times": "*",
            r"\\cdot": "*",
            r"\\div": "/",
            r"\\pm": "+/-",
            r"\\alpha": "alpha",
            r"\\beta": "beta",
            r"\\gamma": "gamma",
            r"\\delta": "delta",
            r"\\theta": "theta",
            r"\\lambda": "lambda",
            r"\\pi": "pi",
            r"\\sigma": "sigma",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)

        text = re.sub(r"[_^]\{([^}]+)\}", r"(\1)", text)
        text = re.sub(r"[_^]([a-zA-Z0-9])", r"(\1)", text)
        text = re.sub(r"[{}]", "", text)
        text = re.sub(r"\\+", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def to_math_text(self, text: str) -> str:
        """Render text with a dedicated plain-text math appendix."""
        expressions = self.extract_math_expressions(text)
        if not expressions:
            return text

        lines = [text.rstrip(), "", "---", "MATH EXPRESSIONS (PLAINTEXT)"]
        for idx, expr in enumerate(expressions, start=1):
            lines.append(f"{idx}. {self.latex_to_plain_text(expr)}")

        return "\n".join(lines)


# Singleton instance
math_detector = MathDetector()


def find_math_regions(page) -> List:
    """Find math regions in a PDF page using heuristics"""
    import fitz
    regions = []
    
    try:
        # Strategy 1: Find images (often embedded equations)
        images = page.get_images()
        for img in images:
            try:
                xref = img[0]
                bbox = page.get_image_bbox(xref)
                if bbox:
                    regions.append(bbox)
            except Exception:
                pass
        
        # Strategy 2: Find text with math fonts
        blocks = page.get_text("dict").get("blocks", [])
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        font = span.get("font", "").lower()
                        # Common math fonts
                        if any(math_font in font for math_font in ["math", "symbol", "cmr", "euler", "stix"]):
                            regions.append(block.get("bbox", (0, 0, 0, 0)))
                            break
    except Exception as e:
        logger.warning(f"Error finding math regions: {e}")
    
    return regions