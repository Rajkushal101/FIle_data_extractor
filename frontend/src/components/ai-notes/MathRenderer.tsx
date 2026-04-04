'use client'

import { useEffect, useRef } from 'react'
import MarkdownIt from 'markdown-it'

interface MathRendererProps {
  content: string
}

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
})

function renderKatexToHtml(equation: string, displayMode: boolean): string {
  if (typeof window === 'undefined' || !(window as any).katex) {
    return displayMode
      ? `<div class="katex-display">${equation}</div>`
      : `<span class="katex-inline">${equation}</span>`
  }

  try {
    return (window as any).katex.renderToString(equation.trim(), {
      displayMode,
      throwOnError: false,
      strict: 'ignore',
    })
  } catch {
    return displayMode
      ? `<div class="katex-display">${equation}</div>`
      : `<span class="katex-inline">${equation}</span>`
  }
}

export default function MathRenderer({ content }: MathRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

    const renderMarkdownWithMath = () => {
      const container = containerRef.current
      if (!container) return

      const displayMath: string[] = []
      const inlineMath: string[] = []

      let source = content

      // Display math blocks: $$...$$
      source = source.replace(/\$\$([\s\S]+?)\$\$/g, (_match, equation) => {
        const tokenIndex = displayMath.push(renderKatexToHtml(equation, true)) - 1
        return `\n\n@@DISPLAY_MATH_${tokenIndex}@@\n\n`
      })

      // Inline math: $...$
      source = source.replace(/(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)/g, (_match, equation) => {
        const tokenIndex = inlineMath.push(renderKatexToHtml(equation, false)) - 1
        return `@@INLINE_MATH_${tokenIndex}@@`
      })

      let html = md.render(source)

      html = html.replace(/<p>\s*@@DISPLAY_MATH_(\d+)@@\s*<\/p>/g, (_match, index) => {
        const idx = Number(index)
        return displayMath[idx] || ''
      })

      html = html.replace(/@@DISPLAY_MATH_(\d+)@@/g, (_match, index) => {
        const idx = Number(index)
        return displayMath[idx] || ''
      })

      html = html.replace(/@@INLINE_MATH_(\d+)@@/g, (_match, index) => {
        const idx = Number(index)
        return inlineMath[idx] || ''
      })

      container.innerHTML = html
    }

    if ((window as any).katex) {
      renderMarkdownWithMath()
      return
    }

    const checkKatex = setInterval(() => {
      if ((window as any).katex) {
        clearInterval(checkKatex)
        renderMarkdownWithMath()
      }
    }, 100)

    return () => clearInterval(checkKatex)
  }, [content])

  return (
    <div 
      ref={containerRef}
      className="math-content text-[#1E2022] leading-7 whitespace-normal break-words"
      dangerouslySetInnerHTML={{ __html: content }}
    />
  )
}