/**
 * OCR utilities using Tesseract.js
 * Supports both images and PDFs
 */

import Tesseract from 'tesseract.js'
import { pdfToImages, isPDF } from './pdf'

/**
 * Perform OCR on an image or PDF file
 * @param {File} file - Image or PDF file to process
 * @param {Function} onProgress - Progress callback (0-100)
 * @returns {Promise<string>} - Extracted text
 */
export async function performOCR(file, onProgress) {
  // Validate file type
  const validImageTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp']
  const isValidImage = validImageTypes.includes(file.type)
  const isValidPDF = isPDF(file)

  if (!isValidImage && !isValidPDF) {
    throw new Error('Please upload a PNG, JPG, WEBP image or PDF file.')
  }

  if (file.size > 20 * 1024 * 1024) {
    throw new Error('File too large. Maximum size is 20MB.')
  }

  try {
    let allText = ''

    if (isValidPDF) {
      // Handle PDF: convert pages to images, then OCR each
      if (onProgress) onProgress(5)

      const images = await pdfToImages(file, (pdfProgress) => {
        // PDF conversion is 0-30% of total progress
        if (onProgress) onProgress(Math.round(pdfProgress * 0.3))
      })

      if (images.length === 0) {
        throw new Error('Could not read PDF. The file may be corrupted.')
      }

      // OCR each page image
      const totalImages = images.length
      for (let i = 0; i < totalImages; i++) {
        const result = await Tesseract.recognize(images[i], 'eng', {
          logger: (m) => {
            if (m.status === 'recognizing text' && onProgress) {
              // OCR is 30-100% of total progress
              const pageProgress = (i + m.progress) / totalImages
              onProgress(30 + Math.round(pageProgress * 70))
            }
          },
        })

        if (result.data.text) {
          allText += result.data.text + '\n\n'
        }
      }
    } else {
      // Handle image directly
      const result = await Tesseract.recognize(file, 'eng', {
        logger: (m) => {
          if (m.status === 'recognizing text' && onProgress) {
            onProgress(Math.round(m.progress * 100))
          }
        },
      })

      allText = result.data.text || ''
    }

    const text = allText.trim()

    if (!text || text.length < 50) {
      throw new Error('Could not extract text. Please use a clearer image or PDF.')
    }

    return text
  } catch (error) {
    if (error.message) throw error
    throw new Error('OCR failed. Please try a different file.')
  }
}

/**
 * Perform OCR on a single image (data URL or File)
 * @param {string|File} image - Image data URL or File
 * @param {Function} onProgress - Progress callback (0-100)
 * @returns {Promise<string>} - Extracted text
 */
export async function ocrImage(image, onProgress) {
  const result = await Tesseract.recognize(image, 'eng', {
    logger: (m) => {
      if (m.status === 'recognizing text' && onProgress) {
        onProgress(Math.round(m.progress * 100))
      }
    },
  })

  return result.data.text || ''
}
