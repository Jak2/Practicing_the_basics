# Financial Statement Parser

> Extract transactions from bank statements (images & PDFs) using AI. Export to Excel/CSV.

A privacy-first web app that runs entirely in your browser. No server, no database, no data collection.

![React](https://img.shields.io/badge/React-18-blue)
![Vite](https://img.shields.io/badge/Vite-5-purple)
![Tailwind](https://img.shields.io/badge/Tailwind-3-cyan)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- **Drag & Drop Upload** - PNG, JPG, WEBP images and PDF files (max 20MB)
- **PDF Support** - Multi-page PDF processing with pdf.js
- **In-Browser OCR** - Text extraction using Tesseract.js
- **AI-Powered Parsing** - Transaction extraction via Google Gemini 2.5 Flash
- **Editable Results** - Review and correct data before export
- **Multiple Exports** - CSV and Excel (.xlsx) formats
- **100% Client-Side** - Your files never leave your browser

---

## Demo

```
1. Enter Gemini API key (free from Google)
2. Upload bank statement (image or PDF)
3. Review extracted transactions
4. Export to Excel or CSV
```

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| React 18 + Vite | Frontend framework & build tool |
| Tailwind CSS | Utility-first styling |
| Tesseract.js | In-browser OCR (WASM) |
| pdf.js | PDF to image conversion |
| Google Gemini 2.5 Flash | AI transaction extraction |
| xlsx + file-saver | Client-side Excel/CSV export |
| Lucide React | Icon library |

---

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Gemini API key ([Get free key](https://aistudio.google.com/apikey))

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd expenses

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

### Build for Production

```bash
npm run build
```

Output in `dist/` folder. Deploy to any static host.

---

## Project Structure

```
src/
├── components/              # React UI components
│   ├── ApiKeyInput.jsx      # API key entry form
│   ├── FileUpload.jsx       # Drag-drop file input (images + PDF)
│   ├── ProcessingStatus.jsx # Progress indicator
│   ├── TransactionTable.jsx # Editable data table
│   ├── Summary.jsx          # Financial totals
│   ├── ExportButtons.jsx    # CSV/Excel download
│   ├── Header.jsx           # App header
│   ├── SettingsModal.jsx    # Key management
│   └── index.js             # Barrel exports
│
├── utils/                   # Business logic
│   ├── storage.js           # localStorage helpers
│   ├── gemini.js            # Gemini API client
│   ├── ocr.js               # Tesseract.js wrapper
│   ├── pdf.js               # PDF to image conversion
│   ├── export.js            # File generation
│   └── index.js             # Barrel exports
│
├── App.jsx                  # Root component + state
├── main.jsx                 # Entry point
└── index.css                # Tailwind imports
```

---

## Architecture

### Processing Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌───────────┐    ┌─────────┐    ┌────────┐
│   Image/    │───▶│  PDF.js     │───▶│  OCR      │───▶│ Gemini  │───▶│ Table  │
│    PDF      │    │ (if PDF)    │    │ (Browser) │    │  API    │    │ View   │
└─────────────┘    └─────────────┘    └───────────┘    └─────────┘    └────────┘
      │                                                                    │
      │                                                                    ▼
      │                                                              ┌────────┐
      └──────────────────────────────────────────────────────────────│ Export │
                                                                     └────────┘
```

### Data Flow

```javascript
// 1. User uploads file (image or PDF)
onFileSelect(file)

// 2. If PDF, convert pages to images
const images = await pdfToImages(file, onProgress)

// 3. OCR extracts text from each page
const text = await performOCR(file, onProgress)

// 4. AI parses transactions
const result = await extractTransactions(text, apiKey)
// Returns: { transactions: [...], bankName, period }

// 5. Display in editable table
setTransactions(result.transactions)

// 6. User exports
exportToExcel(transactions, filename)
```

---

## Key Components

### FileUpload.jsx

Drag-and-drop file input with validation.

```jsx
// Accepts: PNG, JPG, WEBP, PDF
// Max size: 20MB
// Provides drag state feedback
```

### ApiKeyInput.jsx

Handles initial API key setup with validation.

```jsx
// Validates key format (starts with 'AIza')
// Tests key against Gemini API
// Stores in localStorage (obfuscated)
```

### TransactionTable.jsx

Editable table with sorting.

```jsx
// Sortable columns: date, description, debit, credit
// Inline editing with save/cancel
// Row deletion
```

---

## Utils API

### pdf.js

```javascript
import { pdfToImages, isPDF, getPDFPageCount } from './utils/pdf'

// Convert PDF to images for OCR
const images = await pdfToImages(file, onProgress)

// Check if file is PDF
const isPdfFile = isPDF(file)

// Get page count
const pages = await getPDFPageCount(file)
```

### ocr.js

```javascript
// Perform OCR on image or PDF file
const text = await performOCR(file, onProgress)
// Handles both images and multi-page PDFs
// onProgress: (percent) => void
```

### gemini.js

```javascript
// Extract transactions from OCR text
const result = await extractTransactions(ocrText, apiKey)
// Returns: { transactions, bankName, period }

// Validate API key
const { valid, error } = await testApiKey(apiKey)
```

### storage.js

```javascript
saveApiKey(key)       // Save to localStorage
getApiKey()           // Retrieve key
hasApiKey()           // Check if exists
removeApiKey()        // Delete key
isValidKeyFormat(key) // Validate format
```

### export.js

```javascript
exportToCSV(transactions, filename)
exportToExcel(transactions, filename)
const { totalDebit, totalCredit, netFlow, count } = calculateSummary(transactions)
formatCurrency(amount, 'INR')
formatDate(dateString)
```

---

## Gemini API Integration

### Endpoint

```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent
```

### Request Format

```javascript
{
  contents: [{
    parts: [{ text: prompt }]
  }],
  generationConfig: {
    temperature: 0.1,
    maxOutputTokens: 16384,
    responseMimeType: 'application/json'
  }
}
```

### Expected Response

```json
{
  "transactions": [
    {
      "date": "2024-01-15",
      "description": "AMAZON PAY",
      "debit": 2499.00,
      "credit": null,
      "balance": 45000.00
    }
  ],
  "bankName": "HDFC Bank",
  "period": "January 2024"
}
```

---

## State Management

Uses React's `useState` for simplicity:

```javascript
// Auth
const [isAuthenticated, setIsAuthenticated] = useState(hasApiKey())

// Processing
const [status, setStatus] = useState('idle')
// Values: idle | reading | ocr | extracting | complete | error

const [progress, setProgress] = useState(0)  // 0-100
const [error, setError] = useState(null)

// Data
const [transactions, setTransactions] = useState([])
const [bankName, setBankName] = useState(null)
const [period, setPeriod] = useState(null)
```

---

## Error Handling

### User Errors

| Error | Message |
|-------|---------|
| Invalid file type | "Please upload a PNG, JPG, WEBP image or PDF file" |
| File too large | "File too large. Maximum size is 20MB" |
| Invalid API key | Specific message from Google API |
| OCR failed | "Could not extract text. Please use a clearer image" |
| No transactions | "No transactions found in the document" |
| Truncated response | Partial results salvaged when possible |

### API Errors

```javascript
// Network error
{ valid: false, error: 'Network error. Check your connection.' }

// Invalid key
{ valid: false, error: 'API key not valid...' }

// Rate limit
{ valid: false, error: 'Rate limit exceeded...' }
```

---

## Security & Privacy

### API Key Storage

```javascript
// Key is obfuscated (not encrypted) in localStorage
// Obfuscation: reverse + base64
const encoded = btoa(key.split('').reverse().join(''))
```

**Note:** This prevents casual inspection but is NOT secure encryption.

### Data Privacy

- Files processed entirely in browser
- OCR runs in Web Worker (Tesseract.js)
- PDF conversion happens client-side (pdf.js)
- Only extracted text sent to Gemini API
- No data stored on any server
- No analytics or tracking

---

## Browser Support

| Browser | Supported |
|---------|-----------|
| Chrome 90+ | Yes |
| Firefox 90+ | Yes |
| Safari 15+ | Yes |
| Edge 90+ | Yes |
| Mobile browsers | Yes |

Requires: ES2020, Web Workers, Fetch API

---

## Performance

### Bundle Size (Production)

```
React + ReactDOM:  ~45 KB (gzipped)
Tesseract.js:      ~800 KB (lazy loaded)
pdf.js:            ~400 KB (lazy loaded)
xlsx:              ~200 KB (lazy loaded)
App code:          ~30 KB
Tailwind:          ~10 KB (purged)
```

### Processing Performance

- **Images**: 2-5 seconds OCR per image
- **PDFs**: 1-2 seconds per page (conversion) + OCR time
- First OCR run downloads language data (~5-10 seconds)

---

## Deployment

### Vercel (Recommended)

```bash
npm i -g vercel
vercel
```

### Netlify

```bash
npm run build
# Upload dist/ to Netlify
```

### Docker

```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

---

## Scripts

```json
{
  "dev": "vite",
  "build": "vite build",
  "preview": "vite preview"
}
```

---

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## License

MIT License - use it however you want.

---

## Acknowledgments

- [Tesseract.js](https://tesseract.projectnaptha.com/) - OCR engine
- [pdf.js](https://mozilla.github.io/pdf.js/) - PDF rendering
- [Google Gemini](https://ai.google.dev/) - AI extraction
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [Lucide](https://lucide.dev/) - Icons
- [SheetJS](https://sheetjs.com/) - Excel generation
