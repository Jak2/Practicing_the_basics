/**
 * PDF utilities using pdf.js
 * Converts PDF pages to images for OCR processing
 */

import * as pdfjsLib from 'pdfjs-dist/legacy/build/pdf.mjs'

// Set worker source using jsdelivr CDN (most reliable for pdf.js)
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdn.jsdelivr.net/npm/pdfjs-dist@${pdfjsLib.version}/legacy/build/pdf.worker.min.mjs`

/**
 * Convert PDF file to array of image data URLs
 * @param {File} file - PDF file
 * @param {Function} onProgress - Progress callback (0-100)
 * @returns {Promise<string[]>} - Array of image data URLs
 */
export async function pdfToImages(file, onProgress) {
  const arrayBuffer = await file.arrayBuffer()
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise

  const totalPages = pdf.numPages
  const images = []

  for (let pageNum = 1; pageNum <= totalPages; pageNum++) {
    const page = await pdf.getPage(pageNum)

    // Use higher scale for better OCR results
    const scale = 2.0
    const viewport = page.getViewport({ scale })

    // Create canvas
    const canvas = document.createElement('canvas')
    const context = canvas.getContext('2d')
    canvas.width = viewport.width
    canvas.height = viewport.height

    // Render page to canvas
    await page.render({
      canvasContext: context,
      viewport: viewport
    }).promise

    // Convert to image data URL
    const imageDataUrl = canvas.toDataURL('image/png')
    images.push(imageDataUrl)

    // Report progress
    if (onProgress) {
      onProgress(Math.round((pageNum / totalPages) * 100))
    }
  }

  return images
}

/**
 * Check if file is a PDF
 * @param {File} file
 * @returns {boolean}
 */
export function isPDF(file) {
  return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
}

/**
 * Get PDF page count
 * @param {File} file - PDF file
 * @returns {Promise<number>}
 */
export async function getPDFPageCount(file) {
  const arrayBuffer = await file.arrayBuffer()
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise
  return pdf.numPages
}
