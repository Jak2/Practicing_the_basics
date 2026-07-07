# Design Spec — Financial Statement Parser Project Report

**Date:** 2026-06-23
**Author:** Claude Code (brainstorming skill)
**Deliverable:** `PROJECT_REPORT.md` in the project root
**Approach:** Layered Briefing — plain English opening, progressively technical, single document, mixed audience

---

## Document Identity

- **Title:** Financial Statement Parser — Project Report
- **Subtitle:** A technical and contextual account of design, motivation, and implementation
- **Author:** Jaya Arun Kumar Tulluri — v1.0, June 2026
- **Format:** Markdown (`PROJECT_REPORT.md`)
- **Tone:** Plain English first, deepening technically; no jargon left unexplained in Sections 1–3
- **Length:** ~2,600–3,400 words

---

## Abbreviation Expansion List

Each abbreviation is expanded on its **first use only**, in the form `Full Term (ABBR)`. Never re-expand later.

| Abbreviation | Full form | First used in |
|---|---|---|
| AI | Artificial Intelligence | Section 1 |
| API | Application Programming Interface | Section 1 |
| OCR | Optical Character Recognition | Section 1 |
| PDF | Portable Document Format | Section 1 |
| CSV | Comma-Separated Values | Section 1 |
| UI | User Interface | Section 3 or 4 |
| BYOK | Bring Your Own Key | Section 2 or 8 |
| WASM | WebAssembly | Section 5 |
| DOM | Document Object Model | Section 5 |
| JSON | JavaScript Object Notation | Section 4 |
| CLI | Command-Line Interface | Section 7 |

Always expand domain-specific terms (Tesseract.js, pdf.js, Recharts, jsPDF, SheetJS) by writing the full library name on first use and noting its role.

---

## Section Specifications

### Section 1 — Executive Summary
**Audience:** Non-technical (compliance, recruiters, PMs, executives)
**Length:** 150–200 words
**Content:**
- One-paragraph plain-English description: what the tool does (upload a bank statement, AI extracts every transaction, review and export)
- Key capability highlights: Optical Character Recognition (OCR) in the browser, Artificial Intelligence (AI)-powered categorisation, three export formats (CSV, Excel, PDF)
- The defining constraint that makes it non-trivial: 100% client-side — files never leave the user's browser, no server, no sign-up, no cost
- Who uses it and in what context: small business owners, freelancers, accountants, anyone digitising paper bank statements
- How to access it: web app deployable to any static host, or run locally with Node.js

---

### Section 2 — Problem & Motivation
**Audience:** All
**Length:** 300–400 words
**Content:**
- The problem: bank statements arrive as PDFs or scanned images; manually re-entering each transaction into a spreadsheet is slow and error-prone at scale
- Real-world examples: a freelancer reconciling 3 months of statements before tax filing; an accountant processing 20 client PDFs per month
- Why existing tools fall short:
  - Paid tools (Docparser, Tabula, etc.) require subscriptions
  - Bank-provided exports are inconsistently formatted or unavailable for older statements
  - Uploading statements to third-party servers exposes sensitive financial data
- The regulatory and privacy dimension: financial documents contain sensitive personal data — a tool that never leaves the browser is meaningfully safer
- The specific gap filled: automated, zero-cost, privacy-preserving extraction with AI-powered categorisation, requiring only a free Google Gemini Application Programming Interface (API) key

---

### Section 3 — How It Works (Plain English)
**Audience:** Non-technical / general
**Length:** 350–450 words
**Content:**
- The "photocopier analogy": think of OCR as a photocopier that reads the text off a printed page — the app does this inside your browser, so the file never moves
- The four-step flow in plain prose:
  1. **Upload** — drag your bank statement image or PDF onto the app
  2. **Read** — the app uses OCR to extract all the text from the document (if it's a PDF, it converts each page to an image first)
  3. **Parse** — only the extracted text (not the original file) is sent to Google's Gemini AI, which identifies each transaction: date, description, amount, and category
  4. **Review and export** — transactions appear in an editable table; you can correct any mistakes before downloading to CSV, Excel, or PDF
- What the 14 categories mean: Food & Dining, Shopping, Transport, Utilities, Entertainment, Healthcare, Education, Subscriptions, Rent & Housing, Insurance, Transfers, Income, ATM, Other
- Fixed vs Variable cost classification: the AI flags whether each expense is recurring/essential (fixed) or discretionary (variable)
- What the analytics dashboard shows: cash flow summary, six metric cards (total income, total expenses, net cash flow, daily spend rate, fixed costs, period), a category bar chart, and a fixed vs variable pie chart
- What happens after: three export options — plain CSV, a five-sheet Excel workbook, or a formatted PDF report

---

### Section 4 — System Architecture
**Audience:** Engineers / technical reviewers
**Length:** 400–500 words
**Content:**

**Module map table** (path | responsibility):

| Module | Responsibility |
|---|---|
| `src/App.jsx` | Root component; owns all application state; orchestrates the processing pipeline |
| `src/components/ApiKeyInput.jsx` | First-run screen; validates and stores the Gemini API key |
| `src/components/FileUpload.jsx` | Drag-and-drop file input; validates type (PNG/JPG/WEBP/PDF) and size (≤20 MB) |
| `src/components/ProcessingStatus.jsx` | Progress bar and status messages during OCR and AI extraction |
| `src/components/TransactionTable.jsx` | Sortable, inline-editable results table with row deletion |
| `src/components/ExportButtons.jsx` | Triggers CSV, Excel, and PDF downloads |
| `src/components/SettingsModal.jsx` | API key management (view obfuscated key, delete key) |
| `src/components/charts/AnalyticsDashboard.jsx` | Orchestrates the executive summary banner and metric cards |
| `src/components/charts/CategoryChart.jsx` | Recharts bar chart for category spending breakdown |
| `src/components/charts/CostBreakdownChart.jsx` | Recharts pie chart for fixed vs variable split |
| `src/utils/storage.js` | localStorage helpers for API key read/write/delete with base64 obfuscation |
| `src/utils/ocr.js` | Tesseract.js wrapper; handles both images and multi-page PDFs |
| `src/utils/pdf.js` | pdf.js wrapper; converts PDF pages to canvas images for OCR |
| `src/utils/gemini.js` | Gemini API client; prompt construction, JSON parsing, truncation recovery |
| `src/utils/analytics.js` | Statistics engine: burn rate, category totals, fixed/variable split, summary text |
| `src/utils/export.js` | CSV and Excel (five-sheet) export via SheetJS |
| `src/utils/pdfExport.js` | PDF report generator via jsPDF + jspdf-autotable + html2canvas |

**Processing state machine:**
```
idle → reading → ocr → extracting → complete
                                   → error
```
Status values are string literals managed in `App.jsx` state (`useState`).

**Client-side constraint:** everything runs inside the browser process — no server, no database, no backend. The only network calls are:
1. Outbound HTTPS POST to `generativelanguage.googleapis.com` (only extracted text, not the original file)
2. Read/write to `localStorage` (API key, stored locally on the user's device)

**Key data shape** (transaction object):
```json
{
  "id": "txn_1719100000000_0",
  "date": "2024-01-15",
  "description": "AMAZON PAY",
  "debit": 2499.00,
  "credit": null,
  "balance": 45000.00,
  "category": "Shopping",
  "costType": "variable"
}
```
This shape is consumed by the table, analytics engine, and all three export paths — it is the single data contract across the app.

---

### Section 5 — Core Technical Components
**Audience:** Engineers
**Length:** 500–700 words
**Content — one subsection per component:**

**5.1 OCR Pipeline (Tesseract.js)**
- Tesseract.js runs the Tesseract OCR engine compiled to WebAssembly (WASM) — no native binary, no server
- For images: `Tesseract.recognize(file, 'eng', { logger })` directly
- For PDFs: pdf.js converts each page to a canvas image; `ocr.js` iterates pages and concatenates text
- Progress normalisation: PDF conversion occupies 0–30% of the progress bar; OCR for all pages occupies 30–100%
- Output text is sliced at 8,000 characters before being sent to Gemini to stay within token budget
- Minimum text threshold: if extracted text is under 50 characters, the pipeline throws "Could not extract text. Please use a clearer image or PDF."

**5.2 PDF-to-Image Conversion (pdf.js)**
- `pdfjs-dist` renders each page to an HTML canvas at the page's native dimensions
- The canvas `toDataURL('image/png')` output is passed directly to Tesseract.js
- The pdf.js worker is loaded from the jsDelivr CDN to avoid bundling the worker binary
- Functions exposed: `pdfToImages(file, onProgress)`, `isPDF(file)`, `getPDFPageCount(file)`

**5.3 Gemini AI Integration**
- Endpoint: `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`
- Prompt instructs Gemini to return JSON only (no prose), with `responseMimeType: 'application/json'` enforced in `generationConfig`
- `temperature: 0.1` — near-deterministic output; `maxOutputTokens: 16384`
- The prompt embeds the 14 category names and fixed/variable classification rules
- **Three-method JSON salvage** for truncated responses:
  1. Extract from markdown code blocks (` ```json ... ``` `)
  2. Find the outermost `{...}` by index
  3. Truncation repair: find the last complete `},` in the transactions array, close the structure, and set `bankName`/`period` to null
- Error handling distinguishes HTTP 400 (invalid key), 429 (rate limit exceeded), and generic API errors

**5.4 Analytics Engine (`analytics.js`)**
- `calculateStats(transactions)` — the central aggregator; computes total debit, total credit, net cash flow, period in days (from min/max transaction dates), daily burn rate, category totals (sorted descending), fixed/variable split, largest single expense
- `getCategoryTotals(transactions)` — groups debits by category, returns array sorted by amount descending (Pareto order)
- `getFixedVsVariable(transactions)` — splits by `costType` field; returns totals, item lists, and percentages
- `calculateBurnRate(transactions, periodDays)` — `totalDebit / periodDays`; defaults to 30 days if no date range available
- `generateSummaryText(stats, bankName, period)` — produces the executive summary string used in both the dashboard banner and the PDF report header

**5.5 "Add More Files" State Pattern**
- The v1.3.0 bug: `processFileInternal()` always set global `status` state; when called for a second file, the UI re-rendered into "processing" mode and lost the first file's results
- The v1.3.1 fix: added `updateStatus` boolean parameter (default `true`) to `processFileInternal()`
- When `processAdditionalFiles()` calls `processFileInternal(file, false)`, the global status stays `'complete'`, results remain visible, and a separate `isAddingMore` boolean drives a non-destructive "Processing additional files..." overlay
- Current transactions are captured into a local variable before any async work begins, preventing closure staleness from overwriting them

---

### Section 6 — Privacy & Security Design
**Audience:** Compliance, legal, privacy-conscious users
**Length:** 200–250 words
**Content:**
- The privacy-first architecture decision: the original file (image or PDF) is processed entirely in the browser — it is never uploaded to any server
- What does leave the browser: only the OCR-extracted text (plain text, not the file) is sent to Google's Gemini API over HTTPS. The text is capped at 8,000 characters
- What stays local: the original file, the parsed transaction data, and the API key — all remain in the user's browser session or `localStorage`
- API key storage: the key is reversed and base64-encoded before being written to `localStorage` under the key `gemini_api_key`. This prevents casual inspection of browser storage but is explicitly not cryptographic encryption — the README documents this limitation
- BYOK model: the user provides their own Google Gemini key. The app never sees, stores, or transmits the key to any server the app controls — the key goes directly from `localStorage` to Google's API
- No analytics, no tracking, no telemetry: the app makes no tracking calls; there is no app-side server to receive them
- Browser requirements: ES2020, Web Workers (required by Tesseract.js), Fetch API — supported in Chrome 90+, Firefox 90+, Safari 15+, Edge 90+

---

### Section 7 — Usage Guide
**Audience:** Engineers, practitioners
**Length:** 300–400 words
**Content:**

**Prerequisites:**
- Node.js 18 or higher
- A free Google Gemini API key (from Google AI Studio at aistudio.google.com/apikey)

**Local development:**
```bash
git clone <repo-url>
cd expenses
npm install
npm run dev        # → http://localhost:5173
```

**Production build:**
```bash
npm run build      # outputs to dist/
npm run preview    # serve the built output locally
```

**Deploy to Vercel (recommended for static hosting):**
```bash
npm install -g vercel
vercel             # follow prompts; no environment variables needed
```

**Deploy with Docker:**
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

**First-run flow:**
1. Open the app — the API key input screen appears
2. Enter a Gemini key (validated live against the API before storing)
3. Upload a bank statement — drag-and-drop or click to browse; accepts PNG, JPG, WEBP, PDF up to 20 MB
4. Watch the three-stage progress bar: OCR → AI extraction
5. Review extracted transactions in the editable table; click the pencil icon to edit any row
6. Export: CSV (flat file), Excel (five-sheet workbook), or PDF (formatted report)

**Export format comparison:**

| Format | Sheets / Pages | Best for |
|---|---|---|
| CSV | 1 flat file | Importing into accounting software |
| Excel (.xlsx) | 5 sheets: Summary, Categories, Transactions, Fixed Costs, Variable Costs | Analysis, filtering, sharing with accountants |
| PDF | Cover + category table + charts + transactions | Presenting to clients or filing with records |

---

### Section 8 — Tech Stack & Key Design Decisions
**Audience:** Portfolio / recruiters / engineers
**Length:** 300–400 words
**Content:**

**Tech stack table:**

| Layer | Technology | Reason chosen |
|---|---|---|
| Framework | React 18 + Vite 5 | Fast HMR in development; minimal config; native ES modules in production |
| Styling | Tailwind CSS 3 | Utility-first; no runtime overhead; purged CSS in production (~10 KB) |
| OCR | Tesseract.js 5 (WASM) | Runs fully in browser — no server-side OCR dependency |
| PDF rendering | pdf.js (pdfjs-dist 4) | Mozilla's battle-tested renderer; canvas output feeds directly into Tesseract |
| AI extraction | Google Gemini 2.5 Flash | Free tier available; structured JSON output mode; low temperature for deterministic parsing |
| Charts | Recharts 2.12 | React-native charting; composable; refs expose DOM nodes for html2canvas capture |
| Excel export | SheetJS (xlsx 0.18) | Client-side .xlsx generation; multi-sheet workbook support |
| PDF export | jsPDF 2.5 + jspdf-autotable 3.8 | Pure JavaScript PDF generation; no OS-level binary dependencies |
| Chart capture | html2canvas 1.4 | Renders live DOM chart elements to PNG for embedding in the PDF report |
| Downloads | file-saver 2 | Cross-browser `saveAs()` abstraction |
| Icons | Lucide React 0.303 | Consistent icon set; tree-shakeable |

**Five non-obvious design decisions:**

1. **OCR text to Gemini, not the raw image.** Sending the original image to a multimodal model would be simpler, but would upload the user's financial document to Google's servers. Sending only the OCR text preserves the privacy-first constraint while still enabling AI-quality extraction.

2. **BYOK model.** The app has no backend — the user's Gemini key goes directly from their `localStorage` to Google's API. Zero hosting cost, zero data liability, no rate-limit management needed on the app side.

3. **Three-method JSON salvage for Gemini truncation.** The 16,384-token output limit causes responses to be cut mid-JSON for large statements. Rather than failing, the code attempts three recovery methods in order: code-block extraction, index-based boundary detection, and structural repair from the last complete transaction object.

4. **`updateStatus` flag for "Add More" merge.** The v1.3.0 bug was a state-machine collision: the inner processing function updated global `status`, causing the UI to leave the results view and lose context. The fix added a boolean parameter so the inner function can run silently while the outer UI stays in the `'complete'` state.

5. **html2canvas chart capture for PDF export.** jsPDF cannot render SVG or React components. html2canvas renders the live Recharts DOM nodes to PNG at 2× scale, which jsPDF then embeds as raster images — allowing the PDF to mirror the web dashboard's visual analytics.

---

## Out of Scope

- API reference (Gemini API documented by Google)
- Automated test suite (none exists in the current codebase)
- Monetisation strategy (documented in PROJECT_JOURNEY_GUIDE.md)
- Detailed browser-compatibility matrix beyond the summary in Section 6

---

## File Output

- **Path:** `/media/asterisk/1722F6694CF9F147/project/my_learning_projects/expense_tracker/PROJECT_REPORT.md`
- **Commit:** Yes, after writing each section
