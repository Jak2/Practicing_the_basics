/**
 * Gemini API integration for transaction extraction
 */

const GEMINI_API_URL =
  'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent'

/**
 * Extract transactions from OCR text using Gemini
 */
// Category definitions for classification
const CATEGORIES = [
  'Food & Dining',
  'Shopping',
  'Transport',
  'Utilities',
  'Entertainment',
  'Healthcare',
  'Education',
  'Subscriptions',
  'Rent & Housing',
  'Insurance',
  'Transfers',
  'Income',
  'ATM',
  'Other'
]

export async function extractTransactions(ocrText, apiKey) {
  // Limit OCR text to avoid token limits
  const truncatedText = ocrText.slice(0, 8000)

  const prompt = `Parse this bank statement and return JSON only.

Rules:
1. Classify each transaction into one category: ${CATEGORIES.join(', ')}
2. Mark costType as "fixed" for recurring bills (rent, insurance, subscriptions, utilities) or "variable" for discretionary spending
3. Use YYYY-MM-DD date format
4. Use numbers only for amounts (no currency symbols)

Format: {"transactions":[{"date":"YYYY-MM-DD","description":"text","debit":number|null,"credit":number|null,"balance":number|null,"category":"category","costType":"fixed|variable"}],"bankName":"name|null","period":"period|null"}

Text:
${truncatedText}

JSON:`

  const response = await fetch(`${GEMINI_API_URL}?key=${apiKey}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: {
        temperature: 0.1,
        maxOutputTokens: 16384,
        responseMimeType: 'application/json',
      },
    }),
  })

  if (!response.ok) {
    const error = await response.json()
    const message = error.error?.message || 'API request failed'

    if (response.status === 400) {
      throw new Error('Invalid API key. Please check your Gemini API key.')
    }
    if (response.status === 429) {
      throw new Error('Rate limit exceeded. Please try again in a moment.')
    }
    throw new Error(message)
  }

  const data = await response.json()
  const text = data.candidates?.[0]?.content?.parts?.[0]?.text

  if (!text) {
    throw new Error('No response from AI. Please try again.')
  }

  // Parse JSON from response - try multiple extraction methods
  let jsonText = text.trim()
  let result = null

  // Method 1: Try to extract from markdown code blocks
  const codeBlockMatch = text.match(/```(?:json)?\s*([\s\S]*?)\s*```/)
  if (codeBlockMatch) {
    jsonText = codeBlockMatch[1].trim()
  }

  // Method 2: Find JSON object that starts with { and ends with }
  if (!jsonText.startsWith('{')) {
    const jsonStart = text.indexOf('{')
    const jsonEnd = text.lastIndexOf('}')
    if (jsonStart !== -1 && jsonEnd !== -1 && jsonEnd > jsonStart) {
      jsonText = text.slice(jsonStart, jsonEnd + 1)
    }
  }

  try {
    result = JSON.parse(jsonText)
  } catch (e) {
    // Method 3: Try to fix common JSON issues including truncated responses
    try {
      let fixedJson = jsonText
        // Remove trailing commas before } or ]
        .replace(/,\s*}/g, '}')
        .replace(/,\s*]/g, ']')

      // Handle truncated JSON - find last complete transaction object
      if (!fixedJson.endsWith('}')) {
        // Find the last complete object in transactions array
        const lastCompleteObj = fixedJson.lastIndexOf('},')
        if (lastCompleteObj !== -1) {
          // Cut at last complete object and close the structure
          fixedJson = fixedJson.slice(0, lastCompleteObj + 1) + '],"bankName":null,"period":null}'
        } else {
          // Try to find any complete object
          const lastObj = fixedJson.lastIndexOf('}')
          if (lastObj !== -1) {
            fixedJson = fixedJson.slice(0, lastObj + 1)
            // Close any open arrays/objects
            const openBrackets = (fixedJson.match(/\[/g) || []).length
            const closeBrackets = (fixedJson.match(/\]/g) || []).length
            const openBraces = (fixedJson.match(/\{/g) || []).length
            const closeBraces = (fixedJson.match(/\}/g) || []).length
            fixedJson += ']'.repeat(openBrackets - closeBrackets)
            fixedJson += '}'.repeat(openBraces - closeBraces)
          }
        }
      }

      result = JSON.parse(fixedJson)
    } catch (e2) {
      console.error('Parse error:', e2, 'Original text:', text)
      throw new Error('Failed to parse AI response. Please try again.')
    }
  }

  // Validate result structure
  if (!result || typeof result !== 'object') {
    throw new Error('Invalid response format. Please try again.')
  }

  // Add IDs to transactions and ensure category/costType
  const transactions = (result.transactions || []).map((t, i) => ({
    id: `txn_${Date.now()}_${i}`,
    date: t.date || '',
    description: t.description || '',
    debit: t.debit,
    credit: t.credit,
    balance: t.balance,
    reference: t.reference,
    category: t.category || 'Other',
    costType: t.costType || 'variable',
  }))

  if (transactions.length === 0) {
    throw new Error('No transactions found in the document. Please try a clearer image.')
  }

  return {
    transactions,
    bankName: result.bankName || null,
    period: result.period || null,
  }
}

/**
 * Test if API key is valid
 * Returns { valid: boolean, error?: string }
 */
export async function testApiKey(apiKey) {
  try {
    const response = await fetch(`${GEMINI_API_URL}?key=${apiKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: 'Hi' }] }],
        generationConfig: { maxOutputTokens: 5 },
      }),
    })

    if (response.ok) {
      return { valid: true }
    }

    // Get error details
    const error = await response.json()
    const message = error.error?.message || 'Unknown error'
    console.error('API Key validation failed:', message)

    return { valid: false, error: message }
  } catch (err) {
    console.error('API Key test network error:', err)
    return { valid: false, error: 'Network error. Check your connection.' }
  }
}
