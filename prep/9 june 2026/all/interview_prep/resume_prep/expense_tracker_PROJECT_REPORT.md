# Financial Statement Parser — Project Report

> A privacy-first web application that extracts transactions from bank statements using AI and exports them to spreadsheets and reports.

**Author:** user
**Version:** 1.3.1 — June 2026
**Project:** Financial Statement Parser

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem & Motivation](#2-problem--motivation)
3. [How It Works — Plain English](#3-how-it-works--plain-english)
4. [System Architecture](#4-system-architecture)
5. [Core Technical Components](#5-core-technical-components)
6. [Privacy & Security Design](#6-privacy--security-design)
7. [Usage Guide](#7-usage-guide)
8. [Tech Stack & Key Design Decisions](#8-tech-stack--key-design-decisions)

---

## 1. Executive Summary

The Financial Statement Parser is a free, browser-based tool that turns bank statement images and Portable Document Format (PDF) files into structured, exportable data. Upload a scan or PDF of any bank statement, and the app reads it using Optical Character Recognition (OCR) — a technology that converts printed text in images into machine-readable characters — then passes the extracted text to Google's Gemini Artificial Intelligence (AI) for transaction identification and categorisation. Within seconds, every transaction appears in an editable table ready to download as a Comma-Separated Values (CSV) file, a multi-sheet Excel workbook, or a formatted PDF report.

The defining characteristic of the project is its privacy-first architecture: the original file never leaves the user's browser. No server receives your financial documents. No account is required. The only external call the app makes is sending the OCR-extracted text (not the file itself) to Google's Gemini Application Programming Interface (API) — and even that requires the user to supply their own free API key, keeping the app entirely stateless and cost-free to run.

The tool targets small business owners reconciling monthly expenses, freelancers preparing tax records, accountants processing client statements, and anyone who has spent an afternoon re-typing transactions from a scanned PDF.

---

## 2. Problem & Motivation

### The Manual Problem

Every bank issues statements. Most arrive as PDFs or scanned images. For a freelancer reconciling three months of transactions before filing taxes, or an accountant processing twenty client PDFs in a week, this becomes a significant time sink: open the file, read each row, type the date, description, and amount into a spreadsheet, repeat. A typical bank statement has thirty to one hundred rows. Errors creep in; numbers get transposed. Tedious work that skilled time should not go toward.

### Why Existing Approaches Fall Short

Several tools attempt to solve this problem, but each carries a meaningful trade-off:

- **Manual entry** is free but slow and error-prone at scale.
- **Bank-provided data exports** (where available) are inconsistently formatted, not available for older statements, and do not work for scanned paper documents.
- **Paid parsing services** such as Docparser or Tabula require subscriptions, handle limited formats, and — crucially — require uploading the document to a third-party server.
- **General-purpose AI tools** (ChatGPT, Gemini web interface) can extract transactions when given a PDF, but produce unstructured text that still needs manual reformatting before it can be used as data.

The common thread across paid and server-based tools is privacy: financial statements contain account numbers, balances, and merchant details. Sending that data to an external service — even a reputable one — is a risk most compliance-conscious users are unwilling to accept.

### The Gap This Project Fills

The Financial Statement Parser closes this gap: fully automated extraction with zero document upload, zero subscription cost, and AI-quality output. The Bring Your Own Key (BYOK) model means the user supplies a free Google Gemini API key; the app has no server, no database, and no mechanism to receive anyone's data. Every document stays in the browser — the convenience of a paid SaaS product with the privacy guarantees of a local desktop app.

---

## 3. How It Works — Plain English

### The Photocopier Analogy

Think of OCR as a digital photocopier that reads printed text. A photocopier captures a picture — OCR goes one step further and turns that picture into actual characters a computer can work with. The Financial Statement Parser runs this entirely inside your browser, so your bank statement image never travels anywhere.

### The Four Steps

**Step 1 — Upload.** Drag your bank statement onto the app, or click to browse. The app accepts PNG, JPG, WEBP, and PDF up to 20 MB. PDFs are converted page-by-page to images within the browser before processing begins.

**Step 2 — Read.** The app runs OCR on the image, extracting all the text it can see: dates, merchant names, amounts, balances. This text is processed locally. The original file stays on your device.

**Step 3 — Parse.** Only the extracted text — not the original image or PDF — is sent to Google's Gemini AI. The AI reads the text the way an accountant would: it identifies each transaction, records the date, description, debit, credit, and balance, and classifies every line into one of fourteen categories.

**Step 4 — Review and export.** The transactions appear in an editable table in the User Interface (UI). You can sort by any column, edit any cell, or delete rows before exporting. Nothing is permanent until you choose to download.

### Categories and Cost Types

The AI assigns each transaction one of fourteen spending categories: Food & Dining, Shopping, Transport, Utilities, Entertainment, Healthcare, Education, Subscriptions, Rent & Housing, Insurance, Transfers, Income, ATM, or Other. It also labels each expense as either *fixed* (recurring or essential — rent, insurance, subscriptions) or *variable* (discretionary — groceries, entertainment, shopping).

### The Analytics Dashboard

Once extraction is complete, a dashboard appears above the transaction table showing:
- An **executive summary banner** describing your cash flow position, top spending category, and daily spend rate
- **Six metric cards**: Total Income, Total Expenses, Net Cash Flow, Daily Burn Rate, Fixed Costs, and Period (number of days covered)
- A **category bar chart** showing spending ranked from largest to smallest
- A **fixed vs variable pie chart** showing the split between essential and discretionary spending

### What You Get at the End

Three export options are available from the results screen:
- **CSV** — a flat file for importing into accounting software
- **Excel (.xlsx)** — a five-sheet workbook with a summary page, category breakdown, full transaction list, fixed costs sheet, and variable costs sheet
- **PDF** — a formatted report with executive summary, metric tables, captured charts, and a full transaction listing with totals

---

## 4. System Architecture

### Module Map

The application is divided into two layers: components (UI rendering) and utils (business logic). All state lives in `App.jsx` — nothing is stored in a database or remote server.

| Module | Responsibility |
|---|---|
| `src/App.jsx` | Root component; owns all application state; orchestrates the processing pipeline |
| `src/components/ApiKeyInput.jsx` | First-run screen; validates and stores the Gemini API key |
| `src/components/FileUpload.jsx` | Drag-and-drop file input; validates type and size (≤ 20 MB) |
| `src/components/ProcessingStatus.jsx` | Progress bar and status messages during OCR and AI extraction |
| `src/components/TransactionTable.jsx` | Sortable, inline-editable results table with row deletion |
| `src/components/ExportButtons.jsx` | Triggers CSV, Excel, and PDF downloads |
| `src/components/SettingsModal.jsx` | API key management (view obfuscated key, delete key) |
| `src/components/charts/AnalyticsDashboard.jsx` | Orchestrates the executive summary banner and metric cards |
| `src/components/charts/CategoryChart.jsx` | Bar chart for category spending breakdown |
| `src/components/charts/CostBreakdownChart.jsx` | Pie chart for fixed vs variable cost split |
| `src/utils/storage.js` | localStorage helpers for API key read/write/delete with base64 obfuscation |
| `src/utils/ocr.js` | Tesseract.js wrapper; handles both images and multi-page PDFs |
| `src/utils/pdf.js` | pdf.js wrapper; converts PDF pages to canvas images for OCR |
| `src/utils/gemini.js` | Gemini API client; prompt construction, JavaScript Object Notation (JSON) parsing, truncation recovery |
| `src/utils/analytics.js` | Statistics engine: burn rate, category totals, fixed/variable split, summary text |
| `src/utils/export.js` | CSV and Excel (five-sheet) export via SheetJS |
| `src/utils/pdfExport.js` | PDF report generator via jsPDF, jspdf-autotable, and html2canvas |

### Processing State Machine

`App.jsx` drives the UI through six named states:

```
idle → reading → ocr → extracting → complete
                                   ↘ error
```

The `status` variable is a string (`useState`). Transitions are linear except for the `error` branch, which can occur at any processing stage. UI sections are conditionally rendered based on this value.

### Client-Side Boundary

The entire application runs inside the browser. The only two external touch-points are:

1. **Gemini API** — an outbound HTTPS POST to `generativelanguage.googleapis.com` carrying only the OCR-extracted text. The original file is never sent.
2. **localStorage** — the user's Gemini API key is stored under the key `gemini_api_key` on the user's own device.

No app-controlled server exists. No analytics or telemetry calls are made.

### Central Data Contract

Every component and export path consumes transactions in this shared shape:

```json
{
  "id": "txn_1719100000000_0",
  "date": "2024-01-15",
  "description": "AMAZON PAY",
  "debit": 2499.00,
  "credit": null,
  "balance": 45000.00,
  "reference": null,
  "category": "Shopping",
  "costType": "variable"
}
```

This is the single data contract across the table, analytics engine, and all three export paths. Adding a field here propagates automatically to all consumers.

---

## 5. Core Technical Components

### 5.1 OCR Pipeline

The OCR pipeline uses Tesseract.js, a port of the Tesseract OCR engine compiled to WebAssembly (WASM) — a binary instruction format that runs inside the browser at near-native speed without any server-side process. The result is full OCR capability entirely within the user's browser tab.

For image files (PNG, JPG, WEBP), the file is passed directly to `Tesseract.recognize(file, 'eng', { logger })`. For PDFs, each page is first converted to a canvas image by pdf.js, and Tesseract processes each page in sequence, concatenating the text output.

Progress is normalised across both paths: PDF page conversion occupies 0–30% of the progress bar; OCR over all pages occupies 30–100%. Before sending to the AI, the extracted text is capped at 8,000 characters to stay within the Gemini API's token budget. If fewer than 50 characters are recovered, the pipeline raises an error: "Could not extract text. Please use a clearer image or PDF."

### 5.2 PDF-to-Image Conversion

The `src/utils/pdf.js` module wraps pdf.js (pdfjs-dist), Mozilla's production-grade PDF renderer. Each PDF page is rendered to an HTML canvas element at the page's native dimensions, then exported as a PNG data URL via `canvas.toDataURL('image/png')`. That data URL is passed directly to Tesseract.js.

The pdf.js worker script is loaded from the jsDelivr content delivery network rather than bundled — this keeps the production build lean and avoids WebAssembly loader conflicts. Three utility functions are exported: `pdfToImages(file, onProgress)`, `isPDF(file)`, and `getPDFPageCount(file)`.

### 5.3 Gemini AI Integration

The Gemini integration in `src/utils/gemini.js` calls the `gemini-2.5-flash` model via a direct HTTPS POST:

```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent
```

Key generation parameters:
- `temperature: 0.1` — near-deterministic output; reduces hallucinated transactions
- `maxOutputTokens: 16384`
- `responseMimeType: 'application/json'` — instructs the model to return only valid JSON

The prompt embeds all fourteen category names and the fixed/variable classification rules. It instructs the model to return JSON only, using the exact schema the app expects.

**Three-method JSON salvage** handles truncated responses (which occur when a statement has more transactions than fit in the output token limit):

1. **Code-block extraction** — strip markdown ` ```json ``` ` fences if present
2. **Index-based boundary** — find the first `{` and last `}` by character index
3. **Truncation repair** — find the last complete `},` in the transactions array, close the JSON structure, and set `bankName` and `period` to `null`

HTTP error codes are mapped to user-facing messages: HTTP 400 → "Invalid API key. Please check your Gemini API key."; HTTP 429 → "Rate limit exceeded. Please try again in a moment."

### 5.4 Analytics Engine

The `src/utils/analytics.js` module is a pure-function statistics engine. Its central function, `calculateStats(transactions)`, produces:

- **totalDebit / totalCredit** — simple sum reductions
- **netFlow** — `totalCredit - totalDebit`
- **periodDays** — derived from the earliest and latest transaction dates; defaults to 30 if no dates are available
- **dailyBurnRate** — `totalDebit / periodDays`
- **categoryTotals** — grouped by `category` field, sorted descending (Pareto order)
- **costBreakdown** — split by `costType`; includes totals, item lists, and percentages for both fixed and variable
- **largestExpense** — the single transaction with the highest debit value
- **topCategory** — the first entry in `categoryTotals`

All analytics update reactively whenever the `transactions` array changes, including after the "Add More" flow appends results from additional files.

### 5.5 "Add More Files" State Pattern

The v1.3.0 release introduced multiple-file support, but shipped with a bug: uploading a second file replaced the first file's results entirely. The root cause was a state-machine collision in `App.jsx`.

The inner function `processFileInternal(file, updateStatus)` was always setting the global `status` state. When called for a second file while results were displayed, it reset `status` to `'ocr'`, causing the UI to leave the results view — and since the results section only renders when `status === 'complete'`, all existing transactions disappeared from the Document Object Model (DOM).

The v1.3.1 fix added a boolean `updateStatus` parameter (default `true`). The "Add More" path calls `processFileInternal(file, false)`, leaving `status` at `'complete'` throughout. A separate `isAddingMore` boolean drives a non-destructive overlay banner. Critically, current transactions are captured into a local variable at the start of the function:

```javascript
const currentTransactions = [...transactions]
```

This snapshot prevents closure staleness from losing the existing data during the async processing loop.

---

## 6. Privacy & Security Design

### What Stays in the Browser

The original file — image or PDF — is processed entirely within the browser and never transmitted to any server. PDF-to-image conversion runs via pdf.js; OCR runs via Tesseract.js in a browser-managed Web Worker. The parsed transaction data, results table, and downloaded exports are all browser-local.

### What Leaves the Browser

Only the OCR-extracted text leaves the browser — plain text capped at 8,000 characters — sent to Google's Gemini API over HTTPS to identify and categorise transactions. The original file is never included. The user's API key travels from `localStorage` directly to Google's API; the app has no backend to receive or log it.

### API Key Storage

The Gemini API key is stored in `localStorage` under the key `gemini_api_key`. Before storage it is lightly obfuscated: the string is reversed and then base64-encoded, preventing casual inspection in browser developer tools.

This is **not encryption**. The README states: "This prevents casual inspection but is NOT secure encryption." The trade-off is intentional — the app targets a general audience, not a threat model involving physical device access.

### No Tracking, No Telemetry

The app makes no analytics, crash-reporting, or telemetry calls — no app-controlled server exists to receive them. The only outbound network call is the Gemini API request described above.

### Browser Requirements

Requires ES2020, Web Workers (Tesseract.js), and the Fetch API. Supported: Chrome 90+, Firefox 90+, Safari 15+, Edge 90+, and compatible mobile browsers.

---

## 7. Usage Guide

### Prerequisites

- **Node.js 18 or higher** — for local development and building
- **A free Google Gemini API key** — obtain one at [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey). Sign in, click "Create API Key", and copy the result. No credit card required.

### Local Development (Command-Line Interface)

```bash
git clone <repo-url>
cd expenses
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### Production Build

```bash
npm run build      # outputs to dist/
npm run preview    # serve the production build locally for testing
```

The `dist/` folder contains a fully static site. Deploy it to any static host.

### Deploy to Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

Follow the prompts. No environment variables are needed — the Gemini API key is provided by the user at runtime, not at build time. The deployed app is publicly accessible immediately.

### Deploy with Docker

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

```bash
docker build -t financial-parser .
docker run -p 8080:80 financial-parser
```

The app is then accessible at [http://localhost:8080](http://localhost:8080).

### First-Run Flow

1. **Enter API key** — on first load, the API key input screen appears. Paste your Gemini key; the app validates it live against the API before storing it.
2. **Upload a statement** — drag a bank statement image or PDF onto the upload area, or click to browse. Accepted: PNG, JPG, WEBP, PDF up to 20 MB.
3. **Wait for processing** — a three-stage progress bar shows: OCR text extraction (10–50%), AI analysis (50–90%), then complete (100%).
4. **Review** — transactions appear in the analytics dashboard and editable table. Click the pencil icon on any row to edit the date, description, amounts, or category.
5. **Export** — click CSV, Excel, or PDF to download. Edits are included in all exports.

To process additional statements and combine them with the current results, click **Add More** while results are displayed.

### Export Format Comparison

| Format | Contents | Best for |
|---|---|---|
| CSV | Single flat file with all columns | Importing into accounting software |
| Excel (.xlsx) | 5 sheets: Summary, Categories, Transactions, Fixed Costs, Variable Costs | Analysis, filtering, sharing with accountants |
| PDF | Cover summary, category table, captured charts, full transaction listing with totals | Client-ready reports, filing with financial records |

---

## 8. Tech Stack & Key Design Decisions

### Tech Stack

| Layer | Technology | Version | Reason chosen |
|---|---|---|---|
| Framework | React + Vite | 18.2 + 5.0.10 | Fast HMR in development; native ES modules; minimal config |
| Styling | Tailwind CSS | 3.4.0 | Utility-first; zero runtime overhead; ~10 KB purged CSS in production |
| OCR | Tesseract.js | 5.0.4 | Runs fully in-browser via WASM — no server-side OCR dependency |
| PDF rendering | pdf.js (pdfjs-dist) | 4.0.379 | Mozilla's production-grade renderer; canvas output feeds directly into Tesseract |
| AI extraction | Google Gemini 2.5 Flash | — | Free tier available; structured JSON output mode; low temperature for deterministic parsing |
| Charts | Recharts | 2.12.0 | React-native composable charts; DOM refs expose nodes for html2canvas capture |
| Excel export | SheetJS (xlsx) | 0.18.5 | Client-side .xlsx generation with multi-sheet workbook support |
| PDF export | jsPDF + jspdf-autotable | 2.5.1 + 3.8.1 | Pure JavaScript PDF generation; no OS-level binary dependencies |
| Chart capture | html2canvas | 1.4.1 | Renders live DOM chart elements to PNG for embedding in PDF reports |
| File download | file-saver | 2.0.5 | Cross-browser `saveAs()` abstraction |
| Icons | Lucide React | 0.303.0 | Consistent, tree-shakeable icon set |

### Five Non-Obvious Design Decisions

**1. Send OCR text to the AI, not the raw image.**
A multimodal call would eliminate the OCR step but uploads the original file to Google's servers. Running OCR in the browser first and sending only the extracted text (capped at 8,000 characters) keeps the document local. Privacy wins over simplicity.

**2. The BYOK model.**
The app has no backend. The user's Gemini API key goes directly from `localStorage` to Google's API — zero hosting cost, zero data liability, no server-side rate-limit management. The trade-off is slightly higher first-run setup friction, offset by a direct link to Google AI Studio and live key validation.

**3. Three-method JSON salvage for truncated AI responses.**
Gemini's 16,384-token output limit truncates responses for large statements. Rather than returning an error, the code attempts three recovery methods in sequence: strip markdown code fences, find the outermost `{...}` by character index, then find the last complete transaction object and close the structure. Partial results are more useful than a failure.

**4. The `updateStatus` flag for "Add More" file merging.**
The v1.3.0 "Add More" feature hid results when a second file was processed — the inner function reset the global `status`, causing the results section to unmount. The fix: `processFileInternal(file, updateStatus = true)`. Passing `false` bypasses all status updates so the results view stays visible. A useful pattern when a sub-process must run silently inside an active state machine.

**5. html2canvas for PDF chart capture.**
jsPDF cannot render SVG or React components. html2canvas captures the live Recharts DOM nodes at 2× pixel density and converts them to PNG data URLs for embedding. The charts must be visible in the DOM at export time — which is always true since export is only available from the results screen.

---

*Report generated: 2026-06-23 | Author: Jaya Arun Kumar Tulluri | Project version: 1.3.1*
