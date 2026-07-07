import { useState } from 'react'
import { Key, Eye, EyeOff, ExternalLink, Loader2, Check, AlertCircle } from 'lucide-react'
import { saveApiKey, isValidKeyFormat } from '../utils/storage'
import { testApiKey } from '../utils/gemini'

/**
 * API Key Input Component
 * Allows users to enter and validate their Gemini API key
 */
export default function ApiKeyInput({ onSuccess }) {
  const [apiKey, setApiKey] = useState('')
  const [showKey, setShowKey] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    const key = apiKey.trim()

    // Validate format
    if (!isValidKeyFormat(key)) {
      setError('Invalid format. Gemini keys start with "AIza" and are ~39 characters.')
      return
    }

    // Test the key
    setLoading(true)
    const result = await testApiKey(key)
    setLoading(false)

    if (!result.valid) {
      // Show specific error from API if available
      setError(result.error || 'Invalid API key. Please check and try again.')
      return
    }

    // Save and continue
    saveApiKey(key)
    onSuccess()
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex p-4 rounded-2xl bg-blue-100 mb-4">
            <Key className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Add Your Gemini API Key
          </h1>
          <p className="text-gray-600">
            Free from Google AI Studio. Your key stays in your browser.
          </p>
        </div>

        {/* Instructions */}
        <div className="bg-white rounded-xl p-4 mb-6 border border-gray-200">
          <h2 className="font-medium text-gray-900 mb-3">How to get your free key:</h2>
          <ol className="space-y-2 text-sm text-gray-600">
            <li className="flex gap-2">
              <span className="font-medium text-blue-600">1.</span>
              <span>
                Go to{' '}
                <a
                  href="https://aistudio.google.com/apikey"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline inline-flex items-center gap-1"
                >
                  Google AI Studio <ExternalLink className="w-3 h-3" />
                </a>
              </span>
            </li>
            <li className="flex gap-2">
              <span className="font-medium text-blue-600">2.</span>
              <span>Sign in with your Google account</span>
            </li>
            <li className="flex gap-2">
              <span className="font-medium text-blue-600">3.</span>
              <span>Click "Create API Key"</span>
            </li>
            <li className="flex gap-2">
              <span className="font-medium text-blue-600">4.</span>
              <span>Copy and paste the key below</span>
            </li>
          </ol>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-2">
              API Key
            </label>
            <div className="relative">
              <input
                id="apiKey"
                type={showKey ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="AIza..."
                className={`
                  w-full px-4 py-3 pr-12 rounded-xl border bg-white
                  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                  ${error ? 'border-red-300' : 'border-gray-300'}
                `}
                autoComplete="off"
                autoFocus
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600"
              >
                {showKey ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>

            {error && (
              <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                {error}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={!apiKey.trim() || loading}
            className={`
              w-full py-3 px-4 rounded-xl font-medium
              flex items-center justify-center gap-2
              transition-colors
              ${
                !apiKey.trim() || loading
                  ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }
            `}
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Validating...
              </>
            ) : (
              <>
                <Check className="w-5 h-5" />
                Continue
              </>
            )}
          </button>
        </form>

        {/* Privacy note */}
        <p className="mt-6 text-center text-xs text-gray-500">
          🔒 Your key is stored locally in your browser only.
          <br />
          It's never sent to our servers.
        </p>
      </div>
    </div>
  )
}
