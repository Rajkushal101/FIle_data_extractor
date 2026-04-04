'use client'

import { useState } from 'react'
import FileUploader from '@/components/ai-notes/FileUploader'
import ProcessingStatus from '@/components/ai-notes/ProcessingStatus'
import NotesDisplay from '@/components/ai-notes/NotesDisplay'
import { api } from '@/lib/api'
import type { ProcessingResult, NoteStyle } from '@/lib/types'

export default function AINotesPage() {
  const [file, setFile] = useState<File | null>(null)
  const [processing, setProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState<ProcessingResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [noteStyle, setNoteStyle] = useState<NoteStyle>('structured')
  const [enhanceContent, setEnhanceContent] = useState(true)
  const [enhancementDepth, setEnhancementDepth] = useState<'light' | 'deep'>('deep')
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [currentStage, setCurrentStage] = useState('Preparing upload')
  const [isLongRunning, setIsLongRunning] = useState(false)

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile)
    setResult(null)
    setError(null)
  }

  const handleProcess = async () => {
    if (!file) return

    setProcessing(true)
    setProgress(0)
    setError(null)
    setElapsedSeconds(0)
    setIsLongRunning(false)
    setCurrentStage('Uploading file')

    let progressInterval: ReturnType<typeof setInterval> | null = null

    try {
      // Simulate stage-based progress so users know work is still active.
      progressInterval = setInterval(() => {
        setElapsedSeconds(prev => {
          const next = prev + 1

          if (next <= 4) {
            setCurrentStage('Uploading file')
            setProgress(Math.max(8, Math.min(22, next * 4)))
          } else if (next <= 12) {
            setCurrentStage('Extracting text and layout')
            setProgress(Math.max(24, Math.min(48, 22 + (next - 4) * 3)))
          } else if (next <= 24) {
            setCurrentStage('Detecting formulas and technical content')
            setProgress(Math.max(50, Math.min(72, 48 + (next - 12) * 2)))
          } else if (next <= 45) {
            setCurrentStage(enhanceContent ? 'Enhancing and verifying extracted content' : 'Generating structured notes')
            setProgress(Math.max(74, Math.min(92, 72 + Math.floor((next - 24) * 0.9))))
          } else {
            setCurrentStage('Final validation and packaging response')
            setProgress((prevProgress) => Math.min(97, typeof prevProgress === 'number' ? prevProgress + 1 : 97))
          }

          if (next >= 25) {
            setIsLongRunning(true)
          }

          return next
        })
      }, 1000)

      const processingResult = await api.processDocument(file, {
        generateNotes: true,
        noteStyle,
        enhanceContent,
        enhancementDepth,
        aiProvider: 'nvidia',
        strictProvider: true,
      })
      
      if (progressInterval) {
        clearInterval(progressInterval)
      }
      setCurrentStage('Completed')
      setProgress(100)
      setResult(processingResult)
    } catch (err: any) {
      setError(err.message || 'Processing failed')
      setCurrentStage('Failed')
    } finally {
      if (progressInterval) {
        clearInterval(progressInterval)
      }
      setProcessing(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#F0F5F9]">
      <div className="container mx-auto px-4 py-8 md:py-12">
        {/* Header */}
        <div className="text-center mb-8 max-w-3xl mx-auto rounded-3xl p-6 md:p-8 border border-[#C9D6DF] bg-[#F8FBFD] shadow-[0_12px_30px_rgba(30,32,34,0.08)]">
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-2">
            AI Notes Generator
          </h1>
          <p className="text-[#1E2022]">
            Upload your document and let AI create structured study notes
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {!result && !processing && (
            <div className="mb-6 rounded-2xl p-4 border border-[#C9D6DF] bg-white shadow-sm">
              <h2 className="text-sm font-semibold text-slate-800 mb-2">How to use</h2>
              <div className="grid md:grid-cols-3 gap-3 text-xs text-[#1E2022]">
                <p><span className="font-semibold">1. Upload:</span> Choose one file up to 50MB.</p>
                <p><span className="font-semibold">2. Configure:</span> Select note style and enhancement depth.</p>
                <p><span className="font-semibold">3. Generate:</span> Wait for all stages to complete before leaving page.</p>
              </div>
            </div>
          )}

          {/* File Upload Section */}
          {!result && (
            <div className="rounded-2xl p-6 mb-6 border border-[#C9D6DF] bg-white shadow-[0_14px_34px_rgba(30,32,34,0.10)]">
              <FileUploader onFileSelect={handleFileSelect} />
              
              {file && (
                <div className="mt-6">
                  {/* Note Style Selector */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-[#1E2022] mb-2">
                      Note Style:
                    </label>
                    <div className="grid grid-cols-4 gap-2">
                      {(['structured', 'cornell', 'outline', 'mindmap'] as NoteStyle[]).map(style => (
                        <button
                          key={style}
                          onClick={() => setNoteStyle(style)}
                          className={`px-4 py-2 rounded-lg border-2 transition-all ${
                            noteStyle === style
                              ? 'border-[#1E2022] bg-[#C9D6DF] text-[#1E2022]'
                              : 'border-slate-300 bg-white text-[#1E2022] hover:border-slate-500'
                          }`}
                        >
                          {style.charAt(0).toUpperCase() + style.slice(1)}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Process Button */}
                  <div className="mb-4 rounded-xl border border-[#C9D6DF] bg-[#F8FBFD] p-4">
                    <label className="flex items-center gap-2 text-sm text-[#1E2022]">
                      <input
                        type="checkbox"
                        checked={enhanceContent}
                        onChange={(e) => setEnhanceContent(e.target.checked)}
                        className="h-4 w-4"
                      />
                      Enhance and verify extracted text using NVIDIA
                    </label>
                    {enhanceContent && (
                      <div className="mt-3 grid grid-cols-2 gap-2">
                        <button
                          onClick={() => setEnhancementDepth('light')}
                          className={`rounded-lg border px-3 py-2 text-sm ${enhancementDepth === 'light' ? 'border-[#1E2022] bg-[#F0F5F9] text-[#1E2022]' : 'border-slate-300 bg-white text-[#1E2022]'}`}
                        >
                          Light
                        </button>
                        <button
                          onClick={() => setEnhancementDepth('deep')}
                          className={`rounded-lg border px-3 py-2 text-sm ${enhancementDepth === 'deep' ? 'border-[#1E2022] bg-[#C9D6DF] text-[#1E2022]' : 'border-slate-300 bg-white text-[#1E2022]'}`}
                        >
                          Deep
                        </button>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={handleProcess}
                    disabled={processing}
                    className="w-full rounded-lg py-3 px-6 font-semibold border-2 border-[#1E2022] bg-[#1E2022] text-[#F0F5F9] hover:bg-[#52616B] hover:border-[#52616B] disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {processing ? 'Processing...' : 'Generate Notes'}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Processing Status */}
          {processing && (
            <ProcessingStatus
              progress={progress}
              filename={file?.name || ''}
              elapsedSeconds={elapsedSeconds}
              currentStage={currentStage}
              isLongRunning={isLongRunning}
            />
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded-r-xl">
              <div className="flex">
                <div className="flex-shrink-0">
                  <span className="text-xl font-bold text-red-600">!</span>
                </div>
                <div className="ml-3">
                  <h3 className="text-red-800 font-medium">Error</h3>
                  <p className="text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Results Display */}
          {result && (
            <NotesDisplay 
              result={result}
              onReset={() => {
                setFile(null)
                setResult(null)
                setProgress(0)
              }}
            />
          )}
        </div>
      </div>
    </div>
  )
}