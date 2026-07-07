import { Loader2, FileText, ScanSearch, Brain, CheckCircle, AlertCircle } from 'lucide-react'

const STEPS = [
  { id: 'reading', label: 'Reading file', icon: FileText },
  { id: 'ocr', label: 'Extracting text (OCR)', icon: ScanSearch },
  { id: 'extracting', label: 'Analyzing with AI', icon: Brain },
  { id: 'complete', label: 'Done', icon: CheckCircle },
]

/**
 * Processing Status Component
 * Shows progress during file processing
 */
export default function ProcessingStatus({ status, progress, error }) {
  const currentIndex = STEPS.findIndex(s => s.id === status)

  return (
    <div className="w-full max-w-md mx-auto p-6">
      {/* Progress bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-500 mb-2">
          <span>Processing...</span>
          <span>{progress}%</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-300 ${
              error ? 'bg-red-500' : 'bg-blue-600'
            }`}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-3">
        {STEPS.map((step, index) => {
          const Icon = step.icon
          const isComplete = currentIndex > index || status === 'complete'
          const isCurrent = currentIndex === index && status !== 'complete'
          const isError = isCurrent && error

          return (
            <div
              key={step.id}
              className={`
                flex items-center gap-3 p-3 rounded-xl transition-colors
                ${isComplete ? 'bg-green-50 text-green-700' : ''}
                ${isCurrent && !error ? 'bg-blue-50 text-blue-700' : ''}
                ${isError ? 'bg-red-50 text-red-700' : ''}
                ${!isComplete && !isCurrent ? 'text-gray-400' : ''}
              `}
            >
              <div className="w-6 h-6 flex items-center justify-center">
                {isCurrent && !error ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : isError ? (
                  <AlertCircle className="w-5 h-5" />
                ) : isComplete ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <Icon className="w-5 h-5" />
                )}
              </div>
              <span className={`text-sm ${isCurrent ? 'font-medium' : ''}`}>
                {step.label}
              </span>
            </div>
          )
        })}
      </div>

      {/* Error message */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}
    </div>
  )
}
