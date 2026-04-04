'use client'

import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { formatFileSize } from '@/lib/utils'

interface FileUploaderProps {
  onFileSelect: (file: File) => void
}

export default function FileUploader({ onFileSelect }: FileUploaderProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0])
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg']
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024 // 50MB
  })

  const file = acceptedFiles[0]

  return (
    <div>
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all ${
          isDragActive 
            ? 'border-[#1E2022] bg-[#F0F5F9]' 
            : 'border-[#C9D6DF] hover:border-[#52616B] bg-[#F8FBFD]'
        }`}
      >
        <input {...getInputProps()} />
        
        <div className="mx-auto mb-4 h-12 w-12 rounded-xl bg-[#F0F5F9] border border-[#C9D6DF] flex items-center justify-center">
          <span className="h-5 w-5 rounded-sm border-2 border-slate-700" />
        </div>
        
        {isDragActive ? (
          <p className="text-lg text-slate-900 font-medium">
            Drop your file here...
          </p>
        ) : (
          <div>
            <p className="text-lg text-slate-800 font-medium mb-2">
              Step 1: Upload your file
            </p>
            <p className="text-sm text-[#1E2022] mb-4">
              Drag and drop here, or click to browse.
            </p>
            <p className="text-xs text-[#52616B]">
              Supported: PDF, DOCX, PPTX, PNG, JPG (Max 50MB)
            </p>
          </div>
        )}
      </div>

      {file && (
        <div className="mt-4 p-4 rounded-2xl border border-[#C9D6DF] bg-white shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="h-10 w-10 rounded-xl bg-slate-900 text-white flex items-center justify-center text-sm font-bold">
                {file.name.split('.').pop()?.toUpperCase()}
              </span>
              <div>
                <p className="font-medium text-slate-900">{file.name}</p>
                <p className="text-sm text-slate-600">{formatFileSize(file.size)}</p>
              </div>
            </div>
            <span className="text-emerald-700 font-medium">Ready</span>
          </div>
        </div>
      )}
    </div>
  )
}