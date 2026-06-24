# Financial Statement Parser
## React · Vite · Tesseract.js (WASM) · pdf.js · Google Gemini 2.5 Flash · SheetJS · jsPDF

---

## Elevator Pitch (30 seconds)

> "I built a privacy-first browser app that converts bank statement images and PDFs into structured, exportable data. The key constraint: the original file never leaves the user's browser. I run OCR entirely in-browser using Tesseract.js compiled to WebAssembly, extract only the text (not the file), and send that to Gemini for transaction categorisation. The user gets CSV, Excel, and PDF exports with analytics — zero server, zero subscription, zero data liability."

---

## The Problem

Every bank issues statements as PDFs or scanned images. For a freelancer reconciling three months of transactions before filing taxes, or an accountant processing 20 client PDFs in a week, re-typing rows is a significant time sink with error-prone results.

**Why existing tools fall short:**
- Manual entry: free but slow
- Bank exports: inconsistent, unavailable for older/scanned statements
- Paid parsing services (Docparser, Tabula): subscriptions + they receive your financial documents on their servers
- General-purpose AI (ChatGPT web): can extract but returns unstructured text needing manual reformatting

The gap: fully automated extraction with zero document upload, zero cost, zero server.

---

## Architecture — The Privacy-First Constraint

```
User uploads file (PNG/JPG/WEBP/PDF, ≤20MB)
   ↓
If PDF: pdf.js renders each page → canvas → PNG data URL (browser-local)
   ↓
Tesseract.js WASM: OCR on image/canvas → raw text (browser-local)
   ↓
Text capped at 8,000 chars → sent to Gemini API over HTTPS (text only, never file)
   ↓
Gemini 2.5 Flash: identifies transactions, categorises into 14 types, labels fixed/variable
   ↓
App state (App.jsx): transactions array → analytics engine → editable table
   ↓
User edits → exports: CSV | Excel (5-sheet) | PDF report
```

**Two external touch-points only:**
1. Gemini API — receives OCR text (≤8,000 chars), never the original file
2. localStorage — user's API key stored on their own device

---

## The Key Design Decisions

### 1. Send OCR text to AI, not the raw image

A multimodal call (sending the image directly to Gemini) would eliminate the OCR step but uploads the original financial document to Google's servers. Running OCR locally via Tesseract.js first and sending only the extracted text (≤8,000 chars) keeps the document on the user's device.

*Privacy wins over simplicity.* This is the defining architectural decision of the entire project.

### 2. BYOK (Bring Your Own Key) model

The app has no backend. The user's Gemini API key goes directly from localStorage to Google's API. Zero hosting cost, zero data liability, no server-side rate-limit management. The key is lightly obfuscated (string reversed + base64 encoded) — not encryption, but prevents casual inspection in DevTools. The README is transparent about this.

### 3. Three-method JSON salvage for truncated responses

Gemini's 16,384-token output limit truncates responses for large statements. Rather than returning an error:
1. **Code-block extraction** — strip markdown ` ```json ``` ` fences if present
2. **Index-based boundary** — find first `{` and last `}` by character index
3. **Truncation repair** — find the last complete `},` in the transactions array, close the JSON structure, set `bankName`/`period` to null

Partial results are more useful than a failure for an accountant mid-session.

### 4. The `updateStatus` flag for "Add More" file merging

v1.3.0 shipped "Add More Files" support but had a bug: uploading a second file cleared the first file's results. Root cause: the inner `processFileInternal()` function always set the global `status` state. When called for a second file while results were displayed, it reset `status` to `'ocr'`, causing the results section (which only renders when `status === 'complete'`) to unmount.

v1.3.1 fix: added `updateStatus` boolean parameter (default `true`). The "Add More" path passes `false`, keeping `status` at `'complete'` throughout. A separate `isAddingMore` boolean drives a non-destructive overlay banner. Critically:

```javascript
const currentTransactions = [...transactions]  // snapshot prevents closure staleness
```

This captures existing transactions at function start so the async loop doesn't lose them.

### 5. html2canvas for PDF chart capture

jsPDF cannot render SVG or React components. html2canvas captures the live Recharts DOM nodes at 2× pixel density and converts them to PNG data URLs for embedding in the PDF report. Charts must be visible in DOM at export time — always true since export is only available from the results screen.

---

## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Framework | React 18 + Vite 5 | Fast HMR; native ES modules; minimal config |
| Styling | Tailwind CSS 3 | Utility-first; ~10KB purged CSS in production |
| OCR | Tesseract.js 5 | Runs fully in-browser via WASM — zero server dependency |
| PDF rendering | pdf.js (pdfjs-dist) 4 | Mozilla's production-grade renderer; canvas output feeds Tesseract |
| AI extraction | Gemini 2.5 Flash | Free tier; structured JSON output mode; `temperature: 0.1` |
| Charts | Recharts 2 | React-native composable charts; DOM refs for html2canvas capture |
| Excel export | SheetJS | Client-side .xlsx with multi-sheet workbook support |
| PDF export | jsPDF + jspdf-autotable | Pure JavaScript; no OS-level binary dependencies |
| Chart capture | html2canvas | Renders live DOM chart elements to PNG for PDF embedding |

---

## What the App Produces

**Analytics dashboard:**
- Executive summary banner (cash flow, top category, daily burn rate)
- 6 metric cards: Total Income, Expenses, Net Cash Flow, Daily Burn Rate, Fixed Costs, Period
- Category bar chart (Pareto ordered)
- Fixed vs variable cost pie chart

**14 spending categories:** Food & Dining, Shopping, Transport, Utilities, Entertainment, Healthcare, Education, Subscriptions, Rent & Housing, Insurance, Transfers, Income, ATM, Other

**3 export formats:**
- CSV — flat file for accounting software
- Excel (.xlsx) — 5 sheets: Summary, Categories, Transactions, Fixed Costs, Variable Costs
- PDF — formatted report with charts, tables, and totals

---

## Anticipated Interview Questions

**Q: Why run OCR in the browser instead of server-side?**
> Financial documents are sensitive. Running Tesseract.js compiled to WebAssembly means the original file is processed entirely on the user's device. Nothing is sent to any server. The only outbound call is OCR-extracted plain text to Gemini's API — not the file itself. Privacy wins over the simplicity of a server-side OCR solution.

**Q: What is WASM and why does it matter here?**
> WebAssembly is a binary instruction format that runs inside the browser at near-native speed without any server-side process. Tesseract is a C++ OCR engine. Compiling it to WASM lets it run in the browser with full performance — the same capability you'd get from a server-side OCR service, but entirely local.

**Q: What's the risk of the BYOK model?**
> The trade-off is first-run friction. Users must get their own Gemini API key from Google AI Studio. The benefit: the app has no backend at all. No server to breach, no API keys to protect on the server side, no hosting cost, no data liability. I mitigated the friction by providing a direct link to AI Studio and doing live key validation before storing it.

**Q: How did you debug the "Add More" state machine bug?**
> The root cause was closure staleness in an async function — `status` was being read from the outer scope rather than captured at function start. The fix had two parts: the `updateStatus=false` flag to prevent the global state machine from resetting during a secondary file processing run, and the `const currentTransactions = [...transactions]` snapshot to capture the existing array at function entry rather than reading from a potentially stale closure.

**Q: How do you handle statements too large for Gemini's token limit?**
> Three recovery methods in sequence. First, strip markdown code fences if the model wrapped JSON in them. Second, find the outermost `{...}` by character index in case there's surrounding text. Third, find the last complete transaction object — the last `},` in the array — close the JSON structure manually and set bank metadata to null. Partial results are returned rather than an error, which is what a user actually needs mid-session.
