import { useState, useCallback } from 'react'
import { RotateCcw, Plus, Loader2 } from 'lucide-react'

// Components
import ApiKeyInput from './components/ApiKeyInput'
import Header from './components/Header'
import FileUpload from './components/FileUpload'
import ProcessingStatus from './components/ProcessingStatus'
import TransactionTable from './components/TransactionTable'
import ExportButtons from './components/ExportButtons'
import SettingsModal from './components/SettingsModal'
import { AnalyticsDashboard } from './components/charts'

// Utils
import { hasApiKey, getApiKey } from './utils/storage'
import { performOCR } from './utils/ocr'
import { extractTransactions } from './utils/gemini'

/**
 * Main App Component
 * Orchestrates the entire application flow
 */
export default function App() {
  // Auth state
  const [isAuthenticated, setIsAuthenticated] = useState(hasApiKey())

  // UI state
  const [showSettings, setShowSettings] = useState(false)
  const [isAddingMore, setIsAddingMore] = useState(false)

  // Processing state
  const [status, setStatus] = useState('idle') // idle, reading, ocr, extracting, complete, error
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState(null)
  const [processingFile, setProcessingFile] = useState(null) // Current file being processed

  // Data state
  const [transactions, setTransactions] = useState([])
  const [bankName, setBankName] = useState(null)
  const [period, setPeriod] = useState(null)
  const [filesProcessed, setFilesProcessed] = useState(0)

  /**
   * Process a single file and return transactions
   * @param {File} file - The file to process
   * @param {boolean} updateStatus - Whether to update global status (false for "Add More")
   */
  const processFileInternal = async (file, updateStatus = true) => {
    setProcessingFile(file.name)

    // Step 1: OCR
    if (updateStatus) setStatus('ocr')
    const ocrText = await performOCR(file, (p) => {
      setProgress(10 + Math.round(p * 0.4)) // 10-50%
    })
    setProgress(50)

    // Step 2: Extract with AI
    if (updateStatus) setStatus('extracting')
    setProgress(55)

    const apiKey = getApiKey()
    if (!apiKey) {
      throw new Error('API key not found. Please add your key.')
    }

    const result = await extractTransactions(ocrText, apiKey)
    setProgress(90)

    return result
  }

  /**
   * Process uploaded file(s)
   */
  const processFile = useCallback(async (file) => {
    // Reset state
    setStatus('reading')
    setProgress(10)
    setError(null)
    setTransactions([])
    setBankName(null)
    setPeriod(null)
    setFilesProcessed(0)

    try {
      const result = await processFileInternal(file)

      // Validate results
      if (!result.transactions || result.transactions.length === 0) {
        throw new Error('No transactions found. Please try a clearer image.')
      }

      // Success
      setTransactions(result.transactions)
      setBankName(result.bankName)
      setPeriod(result.period)
      setFilesProcessed(1)
      setStatus('complete')
      setProgress(100)

    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.')
      setStatus('error')
    } finally {
      setProcessingFile(null)
    }
  }, [])

  /**
   * Process additional files and append to existing transactions
   */
  const processAdditionalFiles = useCallback(async (files) => {
    setIsAddingMore(true)
    setError(null)

    // Store current transactions to ensure we preserve them
    const currentTransactions = [...transactions]

    try {
      let newTransactions = []
      let newBankName = bankName
      let newPeriod = period

      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        setProcessingFile(file.name)
        setProgress(Math.round(((i + 1) / files.length) * 100))

        try {
          // Pass false to NOT update global status (keeps results visible)
          const result = await processFileInternal(file, false)

          if (result.transactions && result.transactions.length > 0) {
            // Add unique IDs with file index to avoid conflicts
            const txnsWithIds = result.transactions.map((t, idx) => ({
              ...t,
              id: `txn_${Date.now()}_${filesProcessed + i + 1}_${idx}`
            }))
            newTransactions = [...newTransactions, ...txnsWithIds]

            // Update bank name and period if not set
            if (!newBankName && result.bankName) newBankName = result.bankName
            if (!newPeriod && result.period) newPeriod = result.period
          }
        } catch (err) {
          console.error(`Error processing ${file.name}:`, err)
          // Continue with other files
        }
      }

      if (newTransactions.length > 0) {
        // Merge current transactions with new ones
        setTransactions([...currentTransactions, ...newTransactions])
        setFilesProcessed(prev => prev + files.length)
        if (newBankName && !bankName) setBankName(newBankName)
        if (newPeriod && !period) setPeriod(newPeriod)
      }

      setProgress(100)
    } catch (err) {
      setError(err.message || 'Error adding files.')
    } finally {
      setIsAddingMore(false)
      setProcessingFile(null)
    }
  }, [bankName, period, filesProcessed, transactions])

  /**
   * Reset to initial state
   */
  const reset = useCallback(() => {
    setStatus('idle')
    setProgress(0)
    setError(null)
    setTransactions([])
    setBankName(null)
    setPeriod(null)
    setFilesProcessed(0)
    setProcessingFile(null)
  }, [])

  /**
   * Update a transaction
   */
  const updateTransaction = useCallback((id, updates) => {
    setTransactions(prev =>
      prev.map(t => t.id === id ? { ...t, ...updates } : t)
    )
  }, [])

  /**
   * Delete a transaction
   */
  const deleteTransaction = useCallback((id) => {
    setTransactions(prev => prev.filter(t => t.id !== id))
  }, [])

  /**
   * Handle API key removed
   */
  const handleKeyRemoved = useCallback(() => {
    setIsAuthenticated(false)
    reset()
  }, [reset])

  // Show API key input if not authenticated
  if (!isAuthenticated) {
    return <ApiKeyInput onSuccess={() => setIsAuthenticated(true)} />
  }

  const isProcessing = status !== 'idle' && status !== 'complete' && status !== 'error'
  const hasResults = status === 'complete' && transactions.length > 0

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onSettingsClick={() => setShowSettings(true)} />

      <main className="max-w-5xl mx-auto px-4 py-6 sm:py-8">
        {/* Upload Section */}
        {status === 'idle' && (
          <div className="max-w-xl mx-auto">
            <div className="text-center mb-6">
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
                Upload Bank Statement
              </h1>
              <p className="text-gray-600">
                Drop your bank statement images or PDFs to extract transactions
              </p>
            </div>
            <FileUpload onFileSelect={processFile} disabled={isProcessing} multiple={false} />
          </div>
        )}

        {/* Processing Section */}
        {isProcessing && (
          <div>
            <ProcessingStatus status={status} progress={progress} error={error} />
            {processingFile && (
              <p className="text-center text-sm text-gray-500 mt-2">
                Processing: {processingFile}
              </p>
            )}
          </div>
        )}

        {/* Error with Retry */}
        {status === 'error' && (
          <div className="max-w-md mx-auto text-center">
            <ProcessingStatus status={status} progress={progress} error={error} />
            <button
              onClick={reset}
              className="mt-6 inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-300 hover:bg-gray-100 transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              Try Again
            </button>
          </div>
        )}

        {/* Results Section */}
        {hasResults && (
          <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h1 className="text-xl sm:text-2xl font-bold text-gray-900">
                  Extracted Transactions
                </h1>
                <p className="text-sm text-gray-500">
                  {transactions.length} transactions from {filesProcessed} file{filesProcessed > 1 ? 's' : ''} • Review, edit, then export
                </p>
              </div>

              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                {/* Add More Button */}
                <label
                  className={`
                    flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl
                    border border-dashed border-blue-300 bg-blue-50
                    text-sm font-medium text-blue-600
                    cursor-pointer transition-colors
                    ${isAddingMore ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-100 hover:border-blue-400'}
                  `}
                >
                  {isAddingMore ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Plus className="w-4 h-4" />
                  )}
                  Add More
                  <input
                    type="file"
                    className="hidden"
                    accept="image/png,image/jpeg,image/jpg,image/webp,application/pdf,.pdf"
                    onChange={(e) => {
                      const files = Array.from(e.target.files || [])
                      if (files.length > 0) processAdditionalFiles(files)
                      e.target.value = ''
                    }}
                    disabled={isAddingMore}
                    multiple
                  />
                </label>

                {/* New Upload Button */}
                <button
                  onClick={reset}
                  className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-gray-300 hover:bg-gray-100 text-sm font-medium transition-colors"
                >
                  <RotateCcw className="w-4 h-4" />
                  New Upload
                </button>

                {/* Export Buttons */}
                <ExportButtons transactions={transactions} bankName={bankName} period={period} />
              </div>
            </div>

            {/* Adding More Indicator */}
            {isAddingMore && (
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center gap-3">
                <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                <div>
                  <p className="text-sm font-medium text-blue-900">Processing additional files...</p>
                  {processingFile && (
                    <p className="text-xs text-blue-600">{processingFile}</p>
                  )}
                </div>
              </div>
            )}

            {/* Analytics Dashboard */}
            <AnalyticsDashboard
              transactions={transactions}
              bankName={bankName}
              period={period}
            />

            {/* Table */}
            <div className="bg-white rounded-2xl border border-gray-200 p-4 sm:p-6 overflow-hidden">
              <TransactionTable
                transactions={transactions}
                onUpdate={updateTransaction}
                onDelete={deleteTransaction}
              />
            </div>

            {/* Help text */}
            <p className="text-center text-sm text-gray-500">
              Click the pencil icon to edit any transaction. Changes are included in exports.
            </p>
          </div>
        )}
      </main>

      {/* Settings Modal */}
      {showSettings && (
        <SettingsModal
          onClose={() => setShowSettings(false)}
          onKeyRemoved={handleKeyRemoved}
        />
      )}
    </div>
  )
}
