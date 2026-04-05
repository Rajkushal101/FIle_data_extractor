/**
 * API Client
 * Handles all backend communication
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  'https://file-data-extractor.onrender.com'
const DEFAULT_TIMEOUT_MS = 120000

interface ApiErrorPayload {
  detail?: string | { msg?: string }
  request_id?: string
  errors?: Array<{ msg?: string }>
}

function toErrorMessage(payload: ApiErrorPayload | null, fallback: string): string {
  if (!payload) return fallback

  const detail = payload.detail
  let message = fallback

  if (typeof detail === 'string' && detail.trim()) {
    message = detail
  } else if (detail && typeof detail === 'object' && typeof detail.msg === 'string') {
    message = detail.msg
  } else if (Array.isArray(payload.errors) && payload.errors.length > 0) {
    message = payload.errors[0]?.msg || fallback
  }

  return payload.request_id ? `${message} (request: ${payload.request_id})` : message
}

async function parseErrorResponse(response: Response, fallback: string): Promise<string> {
  try {
    const data = (await response.json()) as ApiErrorPayload
    return toErrorMessage(data, fallback)
  } catch {
    return fallback
  }
}

function createTimeoutSignal(timeoutMs: number): { signal: AbortSignal; cleanup: () => void } {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  return {
    signal: controller.signal,
    cleanup: () => clearTimeout(timer),
  }
}

function normalizeApiError(error: unknown, fallback: string): Error {
  if (error instanceof DOMException && error.name === 'AbortError') {
    return new Error('Request timed out. Large files may take longer. Please retry with the same file.')
  }

  if (error instanceof TypeError) {
    return new Error('Cannot reach backend API. Please check backend service availability and CORS settings.')
  }

  if (error instanceof Error && error.message.trim()) {
    return error
  }

  return new Error(fallback)
}

export interface ProcessingResult {
  success: boolean
  filename: string
  file_type: string
  raw_content: {
    text: string
    images: any[]
    metadata: any
    math_expressions?: string[]
    math_text?: string
  }
  structured_notes?: {
    markdown: string
    html: string
    style: string
  }
  metadata: any
  error?: string
}

export interface ProcessOptions {
  generateNotes?: boolean
  noteStyle?: string
  enhanceContent?: boolean
  enhancementDepth?: 'light' | 'deep'
  aiProvider?: 'nvidia' | 'groq' | 'gemini'
  strictProvider?: boolean
}

export const api = {
  /**
   * Process a document
   */
  async processDocument(
    file: File,
    options: ProcessOptions = {}
  ): Promise<ProcessingResult> {
    const formData = new FormData()
    formData.append('file', file)

    const {
      generateNotes = true,
      noteStyle = 'structured',
      enhanceContent = false,
      enhancementDepth = 'deep',
      aiProvider = 'nvidia',
      strictProvider = true,
    } = options

    const params = new URLSearchParams({
      generate_notes: String(generateNotes),
      note_style: noteStyle,
      enhance_content: String(enhanceContent),
      enhancement_depth: enhancementDepth,
      ai_provider: aiProvider,
      strict_provider: String(strictProvider),
    })

    const url = `${API_BASE_URL}/api/process-document?${params.toString()}`

    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(await parseErrorResponse(response, 'Processing failed'))
      }

      return response.json()
    } catch (error) {
      throw normalizeApiError(error, 'Processing failed')
    }
  },

  /**
   * Extract content only (no AI notes)
   */
  async extractOnly(file: File): Promise<ProcessingResult> {
    return this.processDocument(file, { generateNotes: false })
  },

  /**
   * Get supported formats
   */
  async getSupportedFormats() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/supported-formats`)
      if (!response.ok) {
        throw new Error(await parseErrorResponse(response, 'Unable to fetch supported formats'))
      }
      return response.json()
    } catch (error) {
      throw normalizeApiError(error, 'Unable to fetch supported formats')
    }
  },

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`)
      if (!response.ok) {
        throw new Error(await parseErrorResponse(response, 'Health check failed'))
      }
      return response.json()
    } catch (error) {
      throw normalizeApiError(error, 'Health check failed')
    }
  },

  /**
   * Export content as math-friendly plain text
   */
  async exportMathText(content: string, filename?: string) {
    const params = new URLSearchParams()
    if (filename) params.append('filename', filename)

    const url = `${API_BASE_URL}/api/export/math-text${params.toString() ? `?${params.toString()}` : ''}`
    const { signal, cleanup } = createTimeoutSignal(DEFAULT_TIMEOUT_MS)
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
        signal,
      })

      if (!response.ok) {
        throw new Error(await parseErrorResponse(response, 'Math text export failed'))
      }

      return response.blob()
    } catch (error) {
      throw normalizeApiError(error, 'Math text export failed')
    } finally {
      cleanup()
    }
  },

  /**
   * Enhance and verify plain text content deeply
   */
  async enhanceText(
    content: string,
    depth: 'light' | 'deep' = 'deep',
    aiProvider: 'nvidia' | 'groq' | 'gemini' = 'nvidia',
    strictProvider: boolean = true
  ) {
    const params = new URLSearchParams({
      depth,
      ai_provider: aiProvider,
      strict_provider: String(strictProvider),
    })

    const { signal, cleanup } = createTimeoutSignal(DEFAULT_TIMEOUT_MS)
    try {
      const response = await fetch(`${API_BASE_URL}/api/enhance-text?${params.toString()}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
        signal,
      })

      if (!response.ok) {
        throw new Error(await parseErrorResponse(response, 'Text enhancement failed'))
      }

      return response.json()
    } catch (error) {
      throw normalizeApiError(error, 'Text enhancement failed')
    } finally {
      cleanup()
    }
  }
}