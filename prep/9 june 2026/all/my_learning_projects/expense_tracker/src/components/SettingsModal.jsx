import { useState } from 'react'
import { X, Key, Trash2, ExternalLink } from 'lucide-react'
import { getApiKey, removeApiKey, hasApiKey } from '../utils/storage'

/**
 * Settings Modal Component
 * Allows users to manage their API key
 */
export default function SettingsModal({ onClose, onKeyRemoved }) {
  const [showConfirm, setShowConfirm] = useState(false)
  const hasKey = hasApiKey()
  const maskedKey = hasKey ? `AIza****${getApiKey()?.slice(-4) || ''}` : null

  const handleRemoveKey = () => {
    removeApiKey()
    onKeyRemoved()
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-md bg-white rounded-2xl shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Settings</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* API Key Section */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">API Key</h3>

            {hasKey ? (
              <div className="p-4 bg-gray-50 rounded-xl">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <Key className="w-4 h-4 text-green-600" />
                    </div>
                    <div>
                      <p className="font-mono text-sm text-gray-700">{maskedKey}</p>
                      <p className="text-xs text-gray-500">Stored locally</p>
                    </div>
                  </div>

                  {showConfirm ? (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={handleRemoveKey}
                        className="px-3 py-1.5 text-xs bg-red-600 text-white rounded-lg hover:bg-red-700"
                      >
                        Confirm
                      </button>
                      <button
                        onClick={() => setShowConfirm(false)}
                        className="px-3 py-1.5 text-xs border rounded-lg hover:bg-gray-100"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setShowConfirm(true)}
                      className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg"
                      title="Remove API key"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
                <p className="text-sm text-yellow-800">
                  No API key saved. Add one to start extracting transactions.
                </p>
              </div>
            )}
          </div>

          {/* Get new key link */}
          <a
            href="https://aistudio.google.com/apikey"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-blue-600 hover:underline"
          >
            Get a free API key from Google AI Studio
            <ExternalLink className="w-3 h-3" />
          </a>

          {/* Privacy info */}
          <div className="pt-4 border-t">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Privacy</h3>
            <ul className="space-y-2 text-xs text-gray-500">
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                Files are processed in your browser only
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                Your API key never leaves your device
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                No data is stored on any server
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
