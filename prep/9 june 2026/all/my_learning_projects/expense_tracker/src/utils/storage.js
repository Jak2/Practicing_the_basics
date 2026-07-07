/**
 * Local Storage utilities for API key management
 * Keys are stored locally and never sent to any server
 */

const API_KEY_STORAGE_KEY = 'gemini_api_key'

/**
 * Save API key to localStorage
 */
export function saveApiKey(key) {
  try {
    // Basic obfuscation (not encryption - just prevents casual viewing)
    const encoded = btoa(key.split('').reverse().join(''))
    localStorage.setItem(API_KEY_STORAGE_KEY, encoded)
    return true
  } catch (error) {
    console.error('Failed to save API key:', error)
    return false
  }
}

/**
 * Get API key from localStorage
 */
export function getApiKey() {
  try {
    const encoded = localStorage.getItem(API_KEY_STORAGE_KEY)
    if (!encoded) return null
    return atob(encoded).split('').reverse().join('')
  } catch (error) {
    console.error('Failed to get API key:', error)
    return null
  }
}

/**
 * Check if API key exists
 */
export function hasApiKey() {
  return localStorage.getItem(API_KEY_STORAGE_KEY) !== null
}

/**
 * Remove API key from localStorage
 */
export function removeApiKey() {
  localStorage.removeItem(API_KEY_STORAGE_KEY)
}

/**
 * Validate API key format (Gemini keys start with 'AIza')
 */
export function isValidKeyFormat(key) {
  return key && key.trim().length >= 30 && key.trim().startsWith('AIza')
}
