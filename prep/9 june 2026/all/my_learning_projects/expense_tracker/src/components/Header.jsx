import { Settings, Key } from 'lucide-react'

/**
 * Header Component
 * Simple app header with settings access
 */
export default function Header({ onSettingsClick }) {
  return (
    <header className="sticky top-0 z-10 bg-white border-b border-gray-200">
      <div className="max-w-5xl mx-auto px-4 h-14 sm:h-16 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <span className="text-white font-bold">F</span>
          </div>
          <span className="font-semibold text-gray-900 hidden sm:inline">
            Financial Parser
          </span>
        </div>

        {/* Settings */}
        <button
          onClick={onSettingsClick}
          className="p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors"
          title="Settings"
        >
          <Settings className="w-5 h-5" />
        </button>
      </div>
    </header>
  )
}
