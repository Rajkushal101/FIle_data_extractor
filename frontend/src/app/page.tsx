'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'

export default function Home() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <main className="min-h-screen overflow-hidden bg-[#F0F5F9]">
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-grid-pattern opacity-[0.03]" />
        <div className="absolute -top-24 -left-24 h-72 w-72 rounded-full bg-[#C9D6DF]/60 blur-3xl" />
        <div className="absolute -bottom-20 -right-16 h-80 w-80 rounded-full bg-[#C9D6DF]/40 blur-3xl" />
      </div>

      <div className="relative z-10 container mx-auto px-4 py-12 md:py-20">
        <section className={`transition-all duration-700 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <div className="max-w-6xl mx-auto rounded-[28px] border border-[#C9D6DF] bg-[#F8FBFD] shadow-[0_16px_42px_rgba(30,32,34,0.10)] p-6 md:p-12">
            <div className="inline-flex items-center rounded-full border border-[#C9D6DF] bg-[#F0F5F9] px-4 py-2 text-xs tracking-wide uppercase text-[#1E2022]">
              NVIDIA-first extraction pipeline • Groq fallback
            </div>
            <h1 className="mt-6 text-4xl md:text-6xl font-bold tracking-tight text-slate-900">
              Document extraction with better math fidelity and cleaner outputs
            </h1>
            <p className="mt-5 text-base md:text-lg text-[#1E2022] max-w-3xl">
              Upload PDF, DOCX, PPTX, or images and get structured notes, formula-aware text, and exports designed for study and automation workflows.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row gap-4">
              <Link href="/ai-notes" className="rounded-xl px-7 py-3 font-semibold border-2 border-[#1E2022] bg-[#1E2022] text-[#F0F5F9] text-center transition-colors hover:bg-[#52616B] hover:border-[#52616B]">
                Start Extraction
              </Link>
              <Link href="/dashboard" className="rounded-xl px-7 py-3 font-semibold border border-[#52616B]/30 bg-[#C9D6DF] text-[#1E2022] text-center hover:bg-[#B6C7D3] transition-colors">
                Open Dashboard
              </Link>
            </div>
          </div>
        </section>

        <section className="max-w-6xl mx-auto mt-12 grid md:grid-cols-3 gap-4">
          {steps.map((step, index) => (
            <div key={step.title} className="rounded-2xl p-6 border border-[#C9D6DF] bg-white shadow-[0_8px_24px_rgba(30,32,34,0.08)]">
              <p className="text-xs uppercase tracking-widest text-[#52616B]">Step {index + 1}</p>
              <h4 className="mt-2 text-xl font-semibold text-[#1E2022]">{step.title}</h4>
              <p className="mt-2 text-sm text-[#1E2022]">{step.description}</p>
            </div>
          ))}
        </section>
      </div>
    </main>
  )
}

// Data: Steps
const steps = [
  {
    title: 'Upload',
    description: 'Drag and drop your document or click to browse'
  },
  {
    title: 'Process',
    description: 'AI extracts text, equations, and structure automatically'
  },
  {
    title: 'Export',
    description: 'Download formatted notes in your preferred format'
  }
]