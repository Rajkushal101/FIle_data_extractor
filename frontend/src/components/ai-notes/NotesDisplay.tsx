'use client'

import { useState } from 'react'
import Image from 'next/image'
import MathRenderer from './MathRenderer'
import ExportButtons from './ExportButtons'
import type { ProcessingResult } from '@/lib/types'

interface NotesDisplayProps {
  result: ProcessingResult
  onReset: () => void
}

export default function NotesDisplay({ result, onReset }: NotesDisplayProps) {
  const [activeTab, setActiveTab] = useState<'notes' | 'raw'>('notes')

  return (
    <div className="rounded-2xl shadow-xl overflow-hidden fade-in border border-[#C9D6DF] bg-white">
      {/* Header */}
      <div className="p-6 text-slate-900 bg-[#F8FBFD] border-b border-[#C9D6DF]">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-1">Generated Notes</h2>
            <p className="text-slate-600">
              {result.filename} • {result.file_type.toUpperCase()}
            </p>
          </div>
          <button
            onClick={onReset}
            className="px-4 py-2 rounded-lg border border-[#52616B] bg-[#F0F5F9] text-[#1E2022] transition-colors hover:bg-[#C9D6DF]"
          >
            New Upload
          </button>
        </div>
      </div>

      {/* Export Buttons */}
      <div className="border-b border-[#C9D6DF] px-6 py-4 bg-[#F8FBFD]">
        <ExportButtons result={result} />
      </div>

      {/* Tabs */}
      <div className="border-b border-[#C9D6DF] bg-white">
        <div className="flex">
          <button
            onClick={() => setActiveTab('notes')}
            className={`px-6 py-3 font-medium transition-colors ${
              activeTab === 'notes'
                ? 'border-b-2 border-[#1E2022] text-[#1E2022]'
                : 'text-[#52616B] hover:text-[#1E2022]'
            }`}
          >
            Structured Notes
          </button>
          <button
            onClick={() => setActiveTab('raw')}
            className={`px-6 py-3 font-medium transition-colors ${
              activeTab === 'raw'
                ? 'border-b-2 border-[#1E2022] text-[#1E2022]'
                : 'text-[#52616B] hover:text-[#1E2022]'
            }`}
          >
            Raw Content
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 bg-white text-[#1E2022]">
        {activeTab === 'notes' && result.structured_notes ? (
          <div className="max-w-none text-[#1E2022]">
            <MathRenderer content={result.structured_notes.markdown} />
          </div>
        ) : (
          <div className="max-w-none text-[#1E2022]">
            <pre className="whitespace-pre-wrap bg-[#F8FBFD] border border-[#C9D6DF] p-4 rounded-xl text-sm text-[#1E2022]">
              {result.raw_content.text}
            </pre>
            
            {result.raw_content.images && result.raw_content.images.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-3">Extracted Images</h3>
                <div className="grid grid-cols-2 gap-4">
                  {result.raw_content.images.slice(0, 10).map((img, idx) => (
                    <div key={idx} className="border rounded-lg p-2">
                      <Image
                        src={`data:image/png;base64,${img.data}`}
                        alt={`Extracted image ${idx + 1}`}
                        width={640}
                        height={360}
                        className="w-full rounded h-auto"
                      />
                      {img.page && <p className="text-xs text-[#52616B] mt-1">Page {img.page}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Metadata Footer */}
      <div className="bg-[#F8FBFD] px-6 py-4 border-t border-[#C9D6DF]">
        <div className="text-sm text-[#1E2022]">
          <span className="font-medium">Metadata:</span>{' '}
          {result.raw_content.metadata.page_count && (
            <span className="ml-2">{result.raw_content.metadata.page_count} pages</span>
          )}
          {result.structured_notes?.word_count && (
            <span className="ml-4">{result.structured_notes.word_count} words</span>
          )}
          {result.structured_notes?.style && (
            <span className="ml-4">{result.structured_notes.style} style</span>
          )}
          {result.raw_content.math_expressions?.length ? (
            <span className="ml-4">{result.raw_content.math_expressions.length} math expressions</span>
          ) : null}
          {result.metadata?.enhancement_applied ? (
            <span className="ml-4">enhanced ({result.metadata?.enhancement_depth || 'deep'})</span>
          ) : null}
          {result.metadata?.ai_provider ? (
            <span className="ml-4">provider: {result.metadata.ai_provider}</span>
          ) : null}
          {typeof result.metadata?.strict_provider === 'boolean' ? (
            <span className="ml-4">strict: {result.metadata.strict_provider ? 'yes' : 'no'}</span>
          ) : null}
        </div>
        {result.metadata?.warnings?.length ? (
          <div className="mt-3 rounded-lg border border-[#C9D6DF] bg-[#F0F5F9] px-3 py-2 text-xs text-[#1E2022]">
            {result.metadata.warnings.map((warning: string, idx: number) => (
              <p key={idx}>{warning}</p>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  )
}