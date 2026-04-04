/**
 * TypeScript Type Definitions
 */

export interface FileUploadState {
  file: File | null
  uploading: boolean
  processing: boolean
  progress: number
  result: ProcessingResult | null
  error: string | null
}

export interface ProcessingResult {
  success: boolean
  filename: string
  file_type: string
  raw_content: RawContent
  structured_notes?: StructuredNotes
  metadata: Record<string, any> & {
    enhancement_applied?: boolean
    enhancement_depth?: 'light' | 'deep' | null
    ai_provider?: string
    strict_provider?: boolean
    warnings?: string[]
  }
  error?: string
}

export interface RawContent {
  text: string
  images: ImageData[]
  metadata: Record<string, any>
  math_expressions?: string[]
  math_text?: string
}

export interface ImageData {
  page?: number
  data: string
  bbox?: number[]
}

export interface StructuredNotes {
  markdown: string
  html: string
  style: string
  word_count?: number
}

export type NoteStyle = 'structured' | 'cornell' | 'outline' | 'mindmap'