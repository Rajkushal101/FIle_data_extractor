"""
Markdown Conversion Utilities
"""
import re


def markdown_to_html(markdown_text: str) -> str:
    """
    Convert Markdown to HTML
    Simple converter - for production use 'markdown' library
    """
    html = markdown_text
    
    # Headers
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    
    # Bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    
    # Italic
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Code blocks
    html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    
    # Inline code
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    # Links
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
    
    # Lists
    html = re.sub(r'^\* (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = html.replace('<li>', '<ul><li>', 1).replace('</li>\n<li>', '</li><li>')
    html = html.replace('</li>\n', '</li></ul>\n', 1)
    
    # Paragraphs
    html = '<p>' + html.replace('\n\n', '</p><p>') + '</p>'
    
    return html