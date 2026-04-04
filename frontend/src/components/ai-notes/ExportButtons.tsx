'use client'

import { downloadFile } from '@/lib/utils'
import type { ProcessingResult } from '@/lib/types'

interface ExportButtonsProps {
  result: ProcessingResult
}

export default function ExportButtons({ result }: ExportButtonsProps) {
  const exportMarkdown = () => {
    if (!result.structured_notes) return
    downloadFile(
      result.structured_notes.markdown,
      `notes-${result.filename}.md`,
      'text/markdown'
    )
  }

  const exportHTML = () => {
    if (!result.structured_notes) return
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${result.filename} - Notes</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
    .katex { font-size: 1.1em; }
  </style>
</head>
<body>
  ${result.structured_notes.html}
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
</body>
</html>`
    
    downloadFile(htmlContent, `notes-${result.filename}.html`, 'text/html')
  }

  const exportText = () => {
    downloadFile(
      result.raw_content.text,
      `raw-${result.filename}.txt`,
      'text/plain'
    )
  }

  const exportMathText = () => {
    const content = result.raw_content.math_text || result.raw_content.text
    downloadFile(
      content,
      `math-${result.filename}.txt`,
      'text/plain'
    )
  }

  return (
    <div className="flex flex-wrap gap-2">
      <button
        onClick={exportMarkdown}
        disabled={!result.structured_notes}
        className="px-4 py-2 bg-[#52616B] hover:bg-[#1E2022] disabled:bg-gray-400 text-[#F0F5F9] rounded-lg text-sm font-medium transition-colors"
      >
        Markdown
      </button>
      
      <button
        onClick={exportHTML}
        disabled={!result.structured_notes}
        className="px-4 py-2 bg-[#1E2022] hover:bg-[#52616B] disabled:bg-gray-400 text-[#F0F5F9] rounded-lg text-sm font-medium transition-colors"
      >
        HTML
      </button>
      
      <button
        onClick={exportText}
        className="px-4 py-2 bg-[#C9D6DF] hover:bg-[#52616B] hover:text-[#F0F5F9] text-[#1E2022] rounded-lg text-sm font-medium transition-colors"
      >
        Text
      </button>

      <button
        onClick={exportMathText}
        className="px-4 py-2 bg-[#52616B] hover:bg-[#1E2022] text-[#F0F5F9] rounded-lg text-sm font-medium transition-colors"
      >
        Math Text
      </button>
    </div>
  )
}