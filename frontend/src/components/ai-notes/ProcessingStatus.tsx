interface ProcessingStatusProps {
  progress: number
  filename: string
  elapsedSeconds?: number
  currentStage?: string
  isLongRunning?: boolean
}

export default function ProcessingStatus({
  progress,
  filename,
  elapsedSeconds = 0,
  currentStage,
  isLongRunning = false,
}: ProcessingStatusProps) {
  const stageLabel = currentStage || 'Processing pipeline'

  return (
    <div className="rounded-2xl shadow-md p-6 mb-6 border border-[#C9D6DF] bg-white">
      <div className="text-center mb-6">
        <div className="inline-block animate-spin h-12 w-12 rounded-full border-4 border-slate-300 border-t-slate-900 mb-4" />
        <h3 className="text-xl font-semibold text-gray-900">
          Processing {filename}
        </h3>
        <p className="text-[#1E2022] mt-2 font-medium">
          {stageLabel}
        </p>
        <p className="text-sm text-gray-600 mt-1">
          Elapsed: {formatDuration(elapsedSeconds)}
        </p>
        {isLongRunning ? (
          <p className="text-sm text-[#52616B] mt-2">
            This is still running on the server. Please keep this tab open while extraction completes.
          </p>
        ) : null}
        <div className="mt-3 rounded-lg bg-[#F0F5F9] px-3 py-2 text-xs text-[#1E2022] border border-[#C9D6DF]">
          Do not refresh or close the page during processing.
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-[#E5EDF2] rounded-full h-4 overflow-hidden border border-[#C9D6DF]">
        <div
          className="bg-[#52616B] h-full rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="text-center text-sm text-gray-600 mt-2">
        {progress}% Complete
      </p>

      {/* Status Steps */}
      <div className="mt-6 space-y-2">
        <StatusStep 
          completed={progress > 20} 
          active={progress <= 20}
          text="Uploading file..."
        />
        <StatusStep 
          completed={progress > 40} 
          active={progress > 20 && progress <= 40}
          text="Extracting text and images..."
        />
        <StatusStep 
          completed={progress > 70} 
          active={progress > 40 && progress <= 70}
          text="Detecting mathematical equations..."
        />
        <StatusStep 
          completed={progress > 90} 
          active={progress > 70 && progress <= 90}
          text="Generating structured notes..."
        />
        <StatusStep 
          completed={progress === 100} 
          active={progress > 90}
          text="Finalizing..."
        />
      </div>
    </div>
  )
}

function formatDuration(totalSeconds: number): string {
  const mins = Math.floor(totalSeconds / 60)
  const secs = totalSeconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function StatusStep({ completed, active, text }: { completed: boolean, active: boolean, text: string }) {
  return (
    <div className="flex items-center space-x-3">
      <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
        completed ? 'bg-green-500' :
        active ? 'bg-blue-500 animate-pulse' :
        'bg-gray-300'
      }`}>
        {completed ? <span className="text-white text-sm">✓</span> : null}
      </div>
      <span className={`text-sm ${completed || active ? 'text-gray-900' : 'text-[#52616B]'}`}>
        {text}
      </span>
    </div>
  )
}