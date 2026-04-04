"""
PDF Generation Service
Converts Markdown to beautifully formatted PDFs using WeasyPrint
"""

from typing import Dict, Optional
import io
from pathlib import Path

# Try to import WeasyPrint, but make it optional
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    print(f"⚠️  WeasyPrint not available: {e}")
    print("📝 PDF generation will be disabled until GTK3 is installed")

import markdown
from markdown.extensions import fenced_code, tables, toc
import re


async def generate_pdf_from_markdown(
    markdown_content: str,
    metadata: Optional[Dict[str, str]] = None,
    style: str = "modern"
) -> bytes:
    """
    Generate PDF from Markdown content with LaTeX math support
    
    Args:
        markdown_content: Markdown text with optional LaTeX math
        metadata: Optional dict with title, author, date
        style: Style theme (modern, academic, minimal)
        
    Returns:
        PDF file as bytes
        
    Raises:
        RuntimeError: If WeasyPrint is not available
    """
    if not WEASYPRINT_AVAILABLE:
        raise RuntimeError(
            "PDF generation is not available. Please install GTK3 runtime:\n"
            "Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases\n"
            "After installation, restart the application."
        )
    
    metadata = metadata or {}
    
    # Preprocess LaTeX math for KaTeX
    processed_content = _preprocess_math(markdown_content)
    
    # Convert Markdown to HTML
    md = markdown.Markdown(extensions=[
        'fenced_code',
        'tables',
        'toc',
        'nl2br',
        'sane_lists'
    ])
    html_content = md.convert(processed_content)
    
    # Get CSS based on style
    css_content = _get_style_css(style)
    
    # Build complete HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{metadata.get('title', 'Document')}</title>
    
    <!-- KaTeX for math rendering -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
    
    <style>
        {css_content}
    </style>
</head>
<body>
    <!-- Title Page -->
    <div class="title-page">
        <h1 class="doc-title">{metadata.get('title', 'Untitled Document')}</h1>
        {f'<p class="doc-author">By {metadata.get("author")}</p>' if metadata.get('author') else ''}
        {f'<p class="doc-date">{metadata.get("date")}</p>' if metadata.get('date') else ''}
    </div>
    
    <!-- Content -->
    <div class="content">
        {html_content}
    </div>
    
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: "$$", right: "$$", display: true}},
                    {{left: "$", right: "$", display: false}}
                ]
            }});
        }});
    </script>
</body>
</html>
    """
    
    # Generate PDF
    pdf_file = io.BytesIO()
    HTML(string=html).write_pdf(
        pdf_file,
        stylesheets=[CSS(string=css_content)]
    )
    
    return pdf_file.getvalue()


def _preprocess_math(content: str) -> str:
    """Preprocess LaTeX math expressions for proper rendering"""
    # Protect display math
    content = re.sub(r'\$\$(.*?)\$\$', r'<span class="math display">\\[\1\\]</span>', content, flags=re.DOTALL)
    
    # Protect inline math
    content = re.sub(r'\$(.*?)\$', r'<span class="math inline">\\(\1\\)</span>', content)
    
    return content


def _get_style_css(style: str) -> str:
    """Get CSS for specified style theme"""
    
    base_css = """
        @page {
            size: A4;
            margin: 2.5cm;
        }
        
        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.6;
            color: #333;
        }
        
        .title-page {
            page-break-after: always;
            text-align: center;
            padding-top: 30%;
        }
        
        .doc-title {
            font-size: 2.5em;
            margin-bottom: 0.5em;
            font-weight: bold;
        }
        
        .doc-author {
            font-size: 1.2em;
            margin-bottom: 0.3em;
        }
        
        .doc-date {
            font-size: 1em;
            color: #666;
        }
        
        .content {
            max-width: 100%;
        }
        
        h1, h2, h3, h4, h5, h6 {
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: bold;
        }
        
        h1 { font-size: 2em; border-bottom: 2px solid #333; padding-bottom: 0.3em; }
        h2 { font-size: 1.75em; }
        h3 { font-size: 1.5em; }
        
        p {
            margin-bottom: 1em;
            text-align: justify;
        }
        
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        pre {
            background-color: #f4f4f4;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
            margin: 1em 0;
        }
        
        pre code {
            background: none;
            padding: 0;
        }
        
        blockquote {
            border-left: 4px solid #ccc;
            padding-left: 1em;
            margin-left: 0;
            font-style: italic;
            color: #666;
        }
        
        ul, ol {
            margin-bottom: 1em;
            padding-left: 2em;
        }
        
        li {
            margin-bottom: 0.5em;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1em 0;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 0.75em;
            text-align: left;
        }
        
        th {
            background-color: #f4f4f4;
            font-weight: bold;
        }
        
        .math {
            overflow-x: auto;
        }
    """
    
    if style == "modern":
        return base_css + """
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica', sans-serif;
            }
            h1 { color: #6366f1; }
            h2, h3 { color: #4f46e5; }
        """
    elif style == "academic":
        return base_css + """
            body {
                font-family: 'Times New Roman', Georgia, serif;
                font-size: 12pt;
            }
            h1, h2, h3 { color: #000; }
        """
    else:  # minimal
        return base_css + """
            body {
                font-family: 'Helvetica', Arial, sans-serif;
            }
            h1 { border-bottom: none; }
        """
