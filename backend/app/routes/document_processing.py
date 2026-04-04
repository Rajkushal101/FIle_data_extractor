"""
Document Processing API Routes
Main endpoint for file upload and processing
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Body
from typing import Optional
import logging
import os
import re
import asyncio
from pathlib import Path

from app.services.pdf_extractor import PDFExtractor
from app.services.docx_extractor import DOCXExtractor
from app.services.pptx_extractor import PPTXExtractor
from app.services.image_extractor import ImageExtractor
from app.services.ai_processor import AIProcessor
from app.services.note_generator import NoteGenerator
from app.services.math_detector import math_detector
from app.utils.file_handler import save_upload_file, cleanup_temp_file
from app.utils.validators import validate_file
from app.models.processing_result import ProcessingResult
from config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/process-document")
async def process_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    generate_notes: bool = True,
    note_style: Optional[str] = "structured",
    enhance_content: bool = False,
    enhancement_depth: str = "deep",
    ai_provider: str = "nvidia",
    strict_provider: bool = True,
):
    """
    Process uploaded document and extract content
    
    Args:
        file: Uploaded file (PDF, DOCX, PPTX, or image)
        generate_notes: Whether to generate AI notes
        note_style: Style of notes (structured, cornell, outline, mindmap)
    
    Returns:
        ProcessingResult with extracted content and generated notes
    """
    try:
        warnings: list[str] = []

        # Validate file
        validate_file(file)
        
        # Save uploaded file temporarily
        file_path = await save_upload_file(file)
        filename = file.filename or "uploaded_file"
        logger.info(f"Processing file: {filename} ({file.content_type})")
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_temp_file, file_path)
        
        # Extract content based on file type
        file_extension = filename.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            extractor = PDFExtractor()
            raw_content = await asyncio.wait_for(
                extractor.extract(Path(file_path)),
                timeout=settings.PROCESSING_TIMEOUT,
            )
        elif file_extension == 'docx':
            extractor = DOCXExtractor()
            raw_content = await asyncio.wait_for(
                extractor.extract(file_path),
                timeout=settings.PROCESSING_TIMEOUT,
            )
        elif file_extension == 'pptx':
            extractor = PPTXExtractor()
            raw_content = await asyncio.wait_for(
                extractor.extract(file_path),
                timeout=settings.PROCESSING_TIMEOUT,
            )
        elif file_extension in ['png', 'jpg', 'jpeg']:
            extractor = ImageExtractor()
            raw_content = await asyncio.wait_for(
                extractor.extract(file_path),
                timeout=settings.PROCESSING_TIMEOUT,
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
        
        logger.info(f"Extracted {len(raw_content.get('text', ''))} characters")
        
        # Optional deep enhancement/verification pass.
        enhancement_applied = False
        if enhance_content and raw_content.get("text"):
            try:
                ai_processor = AIProcessor()
                original_text = raw_content.get("text", "")
                enhanced_text = await ai_processor.enhance_text_content(
                    original_text,
                    depth=enhancement_depth,
                    preferred_provider=ai_provider,
                    strict_provider=strict_provider,
                )

                raw_content["original_text"] = original_text
                raw_content["text"] = enhanced_text
                enhancement_applied = True
            except Exception as e:
                warnings.append(f"Text enhancement skipped due to provider error: {str(e)}")
                logger.warning("Enhancement failed, continuing with extracted text", exc_info=True)

        # Generate structured notes if requested
        structured_notes = None
        math_expressions = raw_content.get("math_expressions")
        if math_expressions is None:
            math_expressions = math_detector.extract_math_expressions(raw_content.get("text", ""))

        math_text = raw_content.get("math_text")
        if not math_text:
            math_text = math_detector.to_math_text(raw_content.get("text", ""))

        raw_content["math_expressions"] = math_expressions
        raw_content["math_text"] = math_text

        if generate_notes and raw_content.get('text'):
            try:
                note_gen = NoteGenerator()
                structured_notes = await note_gen.generate(
                    raw_content,
                    style=note_style or "structured"
                )
                logger.info(f"Generated {note_style} notes")
            except Exception as e:
                warnings.append(f"Structured note generation failed: {str(e)}")
                logger.warning("Note generation failed, returning raw-text fallback notes", exc_info=True)
                fallback_text = raw_content.get("text", "")
                structured_notes = {
                    "markdown": fallback_text,
                    "html": f"<pre>{fallback_text}</pre>",
                    "style": "fallback",
                    "word_count": len(fallback_text.split()),
                }

        if not raw_content.get("text", "").strip() and not structured_notes:
            raise HTTPException(status_code=422, detail="No extractable content found in the uploaded file")
        
        # Build response
        result = ProcessingResult(
            success=True,
            filename=filename,
            file_type=file_extension,
            raw_content=raw_content,
            structured_notes=structured_notes,
            metadata={
                "file_size_bytes": file.size,
                "note_style": note_style if generate_notes else None,
                "math_expression_count": len(math_expressions),
                "enhancement_applied": enhancement_applied,
                "enhancement_depth": enhancement_depth if enhancement_applied else None,
                "ai_provider": ai_provider,
                "strict_provider": strict_provider,
                "warnings": warnings,
            }
        )
        
        return result
        
    except HTTPException:
        raise
    except asyncio.TimeoutError:
        logger.error("Document processing timed out")
        raise HTTPException(status_code=504, detail="Processing timed out. Please try a smaller file or light enhancement mode")
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@router.post("/extract-only")
async def extract_only(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Extract content without AI note generation
    Faster endpoint for simple extraction
    """
    return await process_document(
        background_tasks=background_tasks,
        file=file,
        generate_notes=False
    )


@router.post("/enhance-text")
async def enhance_text(
    content: str = Body(..., embed=True),
    depth: str = "deep",
    ai_provider: str = "nvidia",
    strict_provider: bool = True,
):
    """
    Deeply verify and enhance plain text using a powerful model.
    """
    try:
        ai_processor = AIProcessor()
        enhanced = await ai_processor.enhance_text_content(
            content,
            depth=depth,
            preferred_provider=ai_provider,
            strict_provider=strict_provider,
        )

        return {
            "success": True,
            "enhanced_text": enhanced,
            "original_text": content,
            "metadata": {
                "depth": depth,
                "ai_provider": ai_provider,
                "strict_provider": strict_provider,
                "fallback_used": False,
            },
        }
    except Exception as e:
        logger.warning(f"Error enhancing text, returning original content: {str(e)}")
        return {
            "success": False,
            "enhanced_text": content,
            "original_text": content,
            "metadata": {
                "depth": depth,
                "ai_provider": ai_provider,
                "strict_provider": strict_provider,
                "fallback_used": True,
                "warning": str(e),
            },
        }


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported file formats
    """
    return {
        "formats": settings.get_allowed_extensions,
        "max_file_size_mb": settings.MAX_FILE_SIZE / (1024**2),
        "note_styles": ["structured", "cornell", "outline", "mindmap"]
    }


# ==================== EXPORT ENDPOINTS (Phase 1) ====================

from fastapi.responses import StreamingResponse
from app.services.pdf_generator import generate_pdf_from_markdown
from app.services.docx_exporter import export_markdown_to_docx
from io import BytesIO
from datetime import datetime


@router.post("/export/pdf")
async def export_pdf(
    markdown_content: str,
    filename: Optional[str] = None,
    style: str = "modern",
    title: Optional[str] = None,
    author: Optional[str] = None
):
    """
    Export Markdown content as PDF
    
    Args:
        markdown_content: Markdown text with LaTeX math
        filename: Output filename (default: notes.pdf)
        style: PDF style (modern, academic, minimal)
        title: Document title
        author: Document author
    
    Returns:
        PDF file download
    """
    try:
        # Prepare metadata
        metadata = {
            "title": title or "Document Notes",
            "author": author or "File Data Extractor",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Generate PDF
        pdf_bytes = await generate_pdf_from_markdown(
            markdown_content,
            metadata=metadata,
            style=style
        )
        
        # Prepare filename
        output_filename = filename or f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        if not output_filename.endswith('.pdf'):
            output_filename += '.pdf'
        
        # Return as downloadable file
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PDF: {str(e)}"
        )


@router.post("/export/docx")
async def export_docx(
    markdown_content: str,
    filename: Optional[str] = None,
    title: Optional[str] = None,
    author: Optional[str] = None
):
    """
    Export Markdown content as Word DOCX
    
    Args:
        markdown_content: Markdown text
        filename: Output filename (default: notes.docx)
        title: Document title
        author: Document author
    
    Returns:
        DOCX file download
    """
    try:
        # Prepare metadata
        metadata = {
            "title": title or "Document Notes",
            "author": author or "File Data Extractor",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Generate DOCX
        docx_bytes = await export_markdown_to_docx(
            markdown_content,
            metadata=metadata
        )
        
        # Prepare filename
        output_filename = filename or f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        if not output_filename.endswith('.docx'):
            output_filename += '.docx'
        
        # Return as downloadable file
        return StreamingResponse(
            BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting DOCX: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating DOCX: {str(e)}"
        )


@router.post("/export/markdown")
async def export_markdown(
    markdown_content: str,
    filename: Optional[str] = None
):
    """
    Export Markdown content as .md file
    
    Args:
        markdown_content: Markdown text
        filename: Output filename (default: notes.md)
    
    Returns:
        Markdown file download
    """
    try:
        # Prepare filename
        output_filename = filename or f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        if not output_filename.endswith('.md'):
            output_filename += '.md'
        
        # Return as downloadable file
        return StreamingResponse(
            BytesIO(markdown_content.encode('utf-8')),
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting Markdown: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting Markdown: {str(e)}"
        )


@router.post("/export/math-text")
async def export_math_text(
    content: str = Body(..., embed=True),
    filename: Optional[str] = None
):
    """
    Export plain text with math expressions converted into readable text.

    Args:
        content: Source text (supports LaTeX equations)
        filename: Output filename (default: notes_math.txt)

    Returns:
        Plain text file download
    """
    try:
        output_text = math_detector.to_math_text(content)

        output_filename = filename or f"notes_math_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        if not output_filename.endswith('.txt'):
            output_filename += '.txt'

        return StreamingResponse(
            BytesIO(output_text.encode('utf-8')),
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )

    except Exception as e:
        logger.error(f"Error exporting math text: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting math text: {str(e)}"
        )


@router.post("/export/latex")
async def export_latex(
    markdown_content: str,
    filename: Optional[str] = None,
    title: Optional[str] = None,
    author: Optional[str] = None
):
    """
    Export content as LaTeX source file
    
    Args:
        markdown_content: Markdown text with LaTeX math
        filename: Output filename (default: notes.tex)
        title: Document title
        author: Document author
    
    Returns:
        LaTeX .tex file download
    """
    try:
        # Convert Markdown to LaTeX format
        latex_content = convert_markdown_to_latex(
            markdown_content,
            title=title or "Document Notes",
            author=author or "File Data Extractor"
        )
        
        # Prepare filename
        output_filename = filename or f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tex"
        if not output_filename.endswith('.tex'):
            output_filename += '.tex'
        
        # Return as downloadable file
        return StreamingResponse(
            BytesIO(latex_content.encode('utf-8')),
            media_type="application/x-tex",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting LaTeX: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting LaTeX: {str(e)}"
        )


def convert_markdown_to_latex(markdown_text: str, title: str, author: str) -> str:
    """
    Convert Markdown to LaTeX document
    
    Simple converter for basic Markdown structures
    """
    # LaTeX document template
    latex = f"""\\documentclass[11pt,a4paper]{{article}}

% Packages
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{hyperref}}
\\usepackage{{geometry}}
\\geometry{{margin=1in}}

% Document info
\\title{{{title}}}
\\author{{{author}}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

"""
    
    # Process content
    lines = markdown_text.split('\n')
    for line in lines:
        line = line.strip()
        
        # Headers
        if line.startswith('# '):
            latex += f"\\section{{{line[2:]}}}\n\n"
        elif line.startswith('## '):
            latex += f"\\subsection{{{line[3:]}}}\n\n"
        elif line.startswith('### '):
            latex += f"\\subsubsection{{{line[4:]}}}\n\n"
        
        # Lists
        elif line.startswith('- ') or line.startswith('* '):
            if '\\begin{itemize}' not in latex[-50:]:
                latex += "\\begin{itemize}\n"
            latex += f"  \\item {line[2:]}\n"
        
        # Inline math: $...$ is already LaTeX
        # Display math: $$...$$ becomes \[...\]
        elif line.startswith('$$') and line.endswith('$$'):
            latex += f"\\[\n{line[2:-2]}\n\\]\n\n"
        
        # Regular paragraphs
        elif line:
            # Close itemize if needed
            if '\\begin{itemize}' in latex and '\\end{itemize}' not in latex[-100:]:
                latex += "\\end{itemize}\n\n"
            
            # Bold: **text** → \textbf{text}
            line = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', line)
            # Italic: *text* → \textit{text}
            line = re.sub(r'\*(.*?)\*', r'\\textit{\1}', line)
            
            latex += f"{line}\n\n"
    
    # Close itemize if still open
    if '\\begin{itemize}' in latex and '\\end{itemize}' not in latex[-100:]:
        latex += "\\end{itemize}\n\n"
    
    latex += "\\end{document}\n"
    
    return latex