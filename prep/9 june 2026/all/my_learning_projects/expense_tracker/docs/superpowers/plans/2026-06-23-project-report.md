# Financial Statement Parser — Project Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write `PROJECT_REPORT.md` in the project root — a 2,600–3,400 word, mixed-audience, layered-briefing report for the Financial Statement Parser project.

**Architecture:** One Markdown file, eight sections, plain English at the top progressively deepening to technical. Each task writes one section and commits. Task 9 does a final sweep.

**Tech Stack:** Markdown only. No code changes. Source of truth for all factual claims: the project source files at `src/`.

## Global Constraints

- **Output file:** `PROJECT_REPORT.md` in `/media/asterisk/1722F6694CF9F147/project/my_learning_projects/expense_tracker/`
- **Do NOT push to git.** Local commits only. Never run `git push`.
- **Abbreviation rule:** Every abbreviation is expanded on its **first use only** in the form `Full Term (ABBR)`. Never re-expand in a later section. The table below is the authority — deviate from it only if the section flow genuinely requires an earlier or later placement.
- **Abbreviation first-use assignment:**
  - Section 1: AI (Artificial Intelligence), API (Application Programming Interface), OCR (Optical Character Recognition), PDF (Portable Document Format), CSV (Comma-Separated Values)
  - Section 2: BYOK (Bring Your Own Key) — if it appears in Sec 2; else defer to Sec 8
  - Section 3: UI (User Interface)
  - Section 4: JSON (JavaScript Object Notation)
  - Section 5: WASM (WebAssembly), DOM (Document Object Model)
  - Section 7: CLI (Command-Line Interface)
- **Technical accuracy:** Every numeric value, code path, and formula must be verified against the actual source files before writing. The verified values are listed in each task below — use them verbatim.
- **Tone:** Sections 1–3 plain English (no unexplained jargon), Sections 4–5 technical, Section 6 plain-technical hybrid, Section 7 instructional (commands copy-pasteable), Section 8 portfolio-ready ("why X over Y").
- **Word count:** Each section must hit its target range. Total 2,600–3,400 words.
- **Heading level:** Section headings are `##`. Sub-headings are `###`. Tables use Markdown pipe syntax.
- **Section separator:** Each section ends with `---` (except the final footer line).
- **Footer line:** The document closes with: `*Report generated: 2026-06-23 | Author: Jaya Arun Kumar Tulluri | Project version: 1.3.1*`

---

## Task 1: Document Header + Section 1 — Executive Summary

**Files:**
- Create: `PROJECT_REPORT.md` (write from scratch)

**Interfaces:**
- Produces: Document header block + Section 1 content that later tasks append to

**Verified technical values for this task:**
- App version: 1.3.1 (from CHANGELOG.md)
- Project title: "Financial Statement Parser" (from README.md and package.json `name: "financial-parser"`)
- Supported file types: PNG, JPG, WEBP, PDF (from FileUpload.jsx)
- Max file size: 20 MB (from ocr.js:25)
- Export formats: CSV, Excel (.xlsx), PDF (from ExportButtons.jsx)
- Deployment: any static host, or locally with Node.js 18+

- [ ] **Step 1: Create PROJECT_REPORT.md with the header and Section 1**

Write the following content exactly to `PROJECT_REPORT.md`:

```markdown
# Financial Statement Parser — Project Report

> A privacy-first web application that extracts transactions from bank statements using Artificial Intelligence (AI) and exports them to spreadsheets and reports.

**Author:** Jaya Arun Kumar Tulluri
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

The Financial Statement Parser is a free, browser-based tool that turns bank statement images and Portable Document Format (PDF) files into structured, exportable data. Upload a scan or PDF of any bank statement, and the app reads it using Optical Character Recognition (OCR) — a technology that converts printed text in images into machine-readable characters — then passes the extracted text to Google's Gemini AI for transaction identification and categorisation. Within seconds, every transaction appears in an editable table ready to download as a Comma-Separated Values (CSV) file, a multi-sheet Excel workbook, or a formatted PDF report.

The defining characteristic of the project is its privacy-first architecture: the original file never leaves the user's browser. No server receives your financial documents. No account is required. The only external call the app makes is sending the OCR-extracted text (not the file itself) to Google's Gemini Application Programming Interface (API) — and even that requires the user to supply their own free API key, keeping the app entirely stateless and cost-free to run.

The tool is aimed at small business owners reconciling monthly expenses, freelancers preparing tax records, accountants processing client statements, and anyone who has ever spent an afternoon manually re-typing transactions from a scanned PDF.

---
```

- [ ] **Step 2: Verify Section 1**

Check:
- [ ] "Artificial Intelligence (AI)" expanded exactly once here
- [ ] "Portable Document Format (PDF)" expanded exactly once here
- [ ] "Optical Character Recognition (OCR)" expanded exactly once here
- [ ] "Comma-Separated Values (CSV)" expanded exactly once here
- [ ] "Application Programming Interface (API)" expanded exactly once here
- [ ] Word count for Section 1 body: approximately 180–200 words
- [ ] No jargon left unexplained

- [ ] **Step 3: Commit**

```bash
cd /media/asterisk/1722F6694CF9F147/project/my_learning_projects/expense_tracker
git add PROJECT_REPORT.md
git commit -m "docs(report): add header and Section 1 — Executive Summary"
```

---

## Task 2: Section 2 — Problem & Motivation

**Files:**
- Modify: `PROJECT_REPORT.md` (append Section 2)

**Interfaces:**
- Consumes: Document with header + Section 1 (Task 1)
- Produces: Section 2 appended; BYOK expanded here if it fits naturally, else defer to Section 8

**Verified technical values for this task:**
- The app has no backend server (README.md: "No server, no database, no data collection")
- File formats supported: PDF, PNG, JPG, WEBP (README.md features list)
- Competing tools mentioned in JOURNEY guide: Docparser, Tabula (PROJECT_JOURNEY_GUIDE.md monetisation context)

- [ ] **Step 1: Append Section 2 to PROJECT_REPORT.md**

Append the following after the `---` that closes Section 1:

```markdown
## 2. Problem & Motivation

### The Manual Problem

Every bank issues statements. Most arrive as PDFs or scanned images. For individuals reviewing a single monthly statement, this is manageable. For a freelancer reconciling three months of transactions before filing taxes, or an accountant processing twenty client PDFs in a week, it becomes a significant time sink: open the file, read each row, type the date, description, and amount into a spreadsheet, repeat. A typical bank statement has thirty to one hundred rows. Errors creep in. Numbers get transposed. The work is tedious and not where skilled time should go.

### Why Existing Approaches Fall Short

Several tools attempt to solve this problem, but each carries a meaningful trade-off:

- **Manual entry** is free but slow and error-prone at scale.
- **Bank-provided data exports** (where available) are inconsistently formatted, not available for older statements, and do not work for scanned paper documents.
- **Paid parsing services** such as Docparser or Tabula require subscriptions, handle limited formats, and — crucially — require uploading the document to a third-party server.
- **General-purpose AI tools** (ChatGPT, Gemini web interface) can extract transactions when given a PDF, but produce unstructured text that still needs manual reformatting before it can be used as data.

The common problem across all paid and server-based tools is privacy: financial statements contain account numbers, balances, transaction histories, and merchant details. Sending that data to an external service, even a reputable one, is a risk many users — and most compliance-conscious businesses — are unwilling to accept.

### The Gap This Project Fills

The Financial Statement Parser was built to close this gap: fully automated extraction with zero document upload, zero subscription cost, and AI-quality output. The Bring Your Own Key (BYOK) model means the user provides a free Google Gemini API key; the app itself has no server, no database, and no mechanism to receive or store anyone's data. Every document stays in the user's browser. The result is a tool that delivers the convenience of a paid SaaS product with the privacy guarantees of a local desktop app.

---
```

- [ ] **Step 2: Verify Section 2**

Check:
- [ ] "Bring Your Own Key (BYOK)" expanded here (first use)
- [ ] None of AI, PDF, OCR, CSV, API re-expanded
- [ ] Word count for Section 2 body: approximately 330–380 words
- [ ] Contains concrete real-world examples (freelancer, accountant)
- [ ] Names specific competing approaches and their trade-offs

- [ ] **Step 3: Commit**

```bash
git add PROJECT_REPORT.md
git commit -m "docs(report): add Section 2 — Problem & Motivation"
```

---

## Task 3: Section 3 — How It Works (Plain English)

**Files:**
- Modify: `PROJECT_REPORT.md` (append Section 3)

**Interfaces:**
- Consumes: Document through Section 2 (Task 2)
- Produces: Section 3 appended; UI expanded here (first use)

**Verified technical values for this task:**
- Four-step processing flow: upload → OCR → AI extraction → review/export (App.jsx processFile function)
- If PDF, pages are converted to images first before OCR (ocr.js:32–61)
- Only extracted text (not the file) is sent to Gemini (gemini.js:48)
- 14 categories: Food & Dining, Shopping, Transport, Utilities, Entertainment, Healthcare, Education, Subscriptions, Rent & Housing, Insurance, Transfers, Income, ATM, Other (gemini.js:12–27)
- costType values: "fixed" (recurring/essential) or "variable" (discretionary) (gemini.js prompt:38–39)
- Analytics: executive summary banner, 6 metric cards, category bar chart, fixed/variable pie chart (AnalyticsDashboard.jsx)
- Export formats: CSV, Excel (5 sheets), PDF (export.js, pdfExport.js)
- Verdict: results appear in an editable table (TransactionTable.jsx)

- [ ] **Step 1: Append Section 3 to PROJECT_REPORT.md**

Append the following after the `---` that closes Section 2:

```markdown
## 3. How It Works — Plain English

### The Photocopier Analogy

Think of OCR as a digital photocopier that reads printed text. When you scan a document, a photocopier captures a picture — OCR goes one step further and turns that picture into actual characters a computer can work with. The Financial Statement Parser uses this technology entirely inside your browser, so the image of your bank statement never needs to travel anywhere.

### The Four Steps

**Step 1 — Upload.** Drag your bank statement onto the app, or click to browse. The app accepts image files (PNG, JPG, WEBP) and PDF documents up to 20 MB. If you upload a PDF, the app converts each page to an image first, all within your browser, before any processing begins.

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
```

- [ ] **Step 2: Verify Section 3**

Check:
- [ ] "User Interface (UI)" expanded exactly once here
- [ ] None of AI, PDF, OCR, CSV, API, BYOK re-expanded
- [ ] All 14 categories listed correctly: Food & Dining, Shopping, Transport, Utilities, Entertainment, Healthcare, Education, Subscriptions, Rent & Housing, Insurance, Transfers, Income, ATM, Other
- [ ] Four steps accurately reflect App.jsx processing flow
- [ ] Word count for Section 3 body: approximately 390–440 words
- [ ] No unexplained jargon in this section

- [ ] **Step 3: Commit**

```bash
git add PROJECT_REPORT.md
git commit -m "docs(report): add Section 3 — How It Works (Plain English)"
```

---

## Task 4: Section 4 — System Architecture

**Files:**
- Modify: `PROJECT_REPORT.md` (append Section 4)

**Interfaces:**
- Consumes: Document through Section 3 (Task 3)
- Produces: Section 4 appended; JSON expanded here (first use)

**Verified technical values for this task:**
- All module paths verified against `find src/ -type f` output
- State values from App.jsx:33: `idle`, `reading`, `ocr`, `extracting`, `complete`, `error`
- Transaction shape from gemini.js:146–156: id, date, description, debit, credit, balance, reference, category, costType
- id format from gemini.js:147: `txn_${Date.now()}_${i}`
- Two external touch-points: Gemini API (HTTPS) and localStorage (API key)
- localStorage key: `gemini_api_key` (storage.js:6)
- Module responsibilities verified against actual source files

- [ ] **Step 1: Append Section 4 to PROJECT_REPORT.md**

Append the following after the `---` that closes Section 3:

```markdown
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
```

- [ ] **Step 2: Verify Section 4**

Check:
- [ ] "JavaScript Object Notation (JSON)" expanded exactly once here
- [ ] None of AI, PDF, OCR, CSV, API, BYOK, UI re-expanded
- [ ] All 17 module paths exist in the actual src/ directory (run `find src/ -type f -name "*.jsx" -o -name "*.js"` to confirm)
- [ ] State values match App.jsx:33 exactly: idle, reading, ocr, extracting, complete, error
- [ ] Transaction shape matches gemini.js:146–156 (id, date, description, debit, credit, balance, reference, category, costType)
- [ ] localStorage key name matches storage.js:6 (`gemini_api_key`)
- [ ] Word count for Section 4 body: approximately 380–450 words

- [ ] **Step 3: Commit**

```bash
git add PROJECT_REPORT.md
git commit -m "docs(report): add Section 4 — System Architecture"
```

---

## Task 5: Section 5 — Core Technical Components

**Files:**
- Modify: `PROJECT_REPORT.md` (append Section 5)

**Interfaces:**
- Consumes: Document through Section 4 (Task 4)
- Produces: Section 5 appended; WASM and DOM expanded here (first uses)

**Verified technical values for this task (verify each against source before writing):**
- Tesseract.js WASM: runs in browser, language 'eng' (ocr.js:47, 64)
- PDF OCR progress normalisation: PDF conversion = 0–30%, OCR = 30–100% (ocr.js:38, 51–52)
- OCR text cap: 8,000 characters (`ocrText.slice(0, 8000)` — gemini.js:32)
- Minimum OCR text threshold: 50 characters (ocr.js:77: `text.length < 50`)
- pdf.js worker loaded from jsDelivr CDN (pdf.js — verify by reading src/utils/pdf.js)
- Functions in pdf.js: `pdfToImages(file, onProgress)`, `isPDF(file)`, `getPDFPageCount(file)` (pdf.js)
- Gemini endpoint: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent` (gemini.js:6)
- temperature: 0.1 (gemini.js:54)
- maxOutputTokens: 16384 (gemini.js:55)
- responseMimeType: 'application/json' (gemini.js:56)
- JSON salvage Method 1: extract from markdown code blocks (gemini.js:86–88)
- JSON salvage Method 2: find outermost `{...}` by index (gemini.js:91–97)
- JSON salvage Method 3: truncation repair — find last `},`, close structure, set bankName/period null (gemini.js:102–132)
- HTTP 400 → "Invalid API key" (gemini.js:65–67)
- HTTP 429 → "Rate limit exceeded" (gemini.js:68–70)
- calculateStats inputs/outputs: verified from analytics.js
- updateStatus parameter: default true (App.jsx:48)
- isAddingMore state: separate boolean (App.jsx:29)
- Current transactions captured before async work: `const currentTransactions = [...transactions]` (App.jsx:118)

- [ ] **Step 1: Read source files to verify all values above before writing**

```bash
grep -n "slice" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/expense_tracker/src/utils/gemini.js
grep -n "text.length" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/expense_tracker/src/utils/ocr.js
grep -n "temperature\|maxOutputTokens\|responseMimeType" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/expense_tracker/src/utils/gemini.js
grep -n "updateStatus\|isAddingMore\|currentTransactions" /media/asterisk/1722F6694CF9F147/project/my_learning_projects/expense_tracker/src/App.jsx
```

Expected output confirms values listed above. If any differ, use the actual source values.

- [ ] **Step 2: Append Section 5 to PROJECT_REPORT.md**

Append the following after the `---` that closes Section 4:

```markdown
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

All analytics update reactively whenever the `transactions` array changes, including after the "Add More" flow appends additional file results.

### 5.5 "Add More Files" State Pattern

The v1.3.0 release introduced multiple-file support, but shipped with a bug: uploading a second file replaced the first file's results entirely. The root cause was a state-machine collision in `App.jsx`.

The inner function `processFileInternal(file, updateStatus)` was always setting the global `status` state. When called for a second file while results were displayed, it reset `status` to `'ocr'`, causing the UI to leave the results view — and since the results section only renders when `status === 'complete'`, all existing transactions disappeared from the Document Object Model (DOM).

The v1.3.1 fix added a boolean `updateStatus` parameter (default `true`). The "Add More" path calls `processFileInternal(file, false)`, leaving `status` at `'complete'` throughout. A separate `isAddingMore` boolean drives a non-destructive overlay banner. Critically, current transactions are captured into a local variable at the start of the function:

```javascript
const currentTransactions = [...transactions]
```

This snapshot prevents closure staleness from losing the existing data during the async processing loop.

---
```

- [ ] **Step 3: Verify Section 5**

Check:
- [ ] "WebAssembly (WASM)" expanded exactly once in 5.1
- [ ] "Document Object Model (DOM)" expanded exactly once in 5.5
- [ ] None of AI, PDF, OCR, CSV, API, BYOK, UI, JSON re-expanded
- [ ] OCR text cap is 8,000 characters — matches gemini.js:32
- [ ] Min text threshold is 50 characters — matches ocr.js:77
- [ ] Gemini endpoint URL is exactly `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`
- [ ] temperature is 0.1, maxOutputTokens is 16384 — matches gemini.js:54–55
- [ ] Three salvage methods described accurately match gemini.js:86–132
- [ ] HTTP 400 and 429 messages match gemini.js:65–70 exactly
- [ ] `updateStatus` default is `true` — matches App.jsx:48
- [ ] `currentTransactions` snapshot line matches App.jsx:118
- [ ] Word count for Section 5 body: approximately 520–620 words

- [ ] **Step 4: Commit**

```bash
git add PROJECT_REPORT.md
git commit -m "docs(report): add Section 5 — Core Technical Components"
```

---

## Task 6: Section 6 — Privacy & Security Design

**Files:**
- Modify: `PROJECT_REPORT.md` (append Section 6)

**Interfaces:**
- Consumes: Document through Section 5 (Task 5)
- Produces: Section 6 appended

**Verified technical values for this task:**
- File never sent to any server — only OCR text sent to Gemini (gemini.js:48)
- OCR text capped at 8,000 characters before sending (gemini.js:32)
- localStorage key: `gemini_api_key` (storage.js:6)
- Obfuscation method: reverse the string + base64 encode (storage.js:13: `btoa(key.split('').reverse().join(''))`)
- README explicitly states: "This prevents casual inspection but is NOT secure encryption"
- No analytics, no tracking, no telemetry (README.md Security section)
- Browser requirements: ES2020, Web Workers, Fetch API (README.md)
- Browser support: Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ (README.md)

- [ ] **Step 1: Append Section 6 to PROJECT_REPORT.md**

Append the following after the `---` that closes Section 5:

```markdown
## 6. Privacy & Security Design

### What Stays in the Browser

The original file — image or PDF — is processed entirely within the browser. It is never transmitted to any server, not even temporarily. PDF-to-image conversion runs via pdf.js in the browser; OCR runs via Tesseract.js in a Web Worker process that the browser manages locally.

The parsed transaction data, the results table, and the downloaded export files are all browser-local. Nothing is persisted to any remote database.

### What Leaves the Browser

Only one piece of data leaves the browser: the OCR-extracted text. This plain text — capped at 8,000 characters — is sent to Google's Gemini API over HTTPS to identify and categorise transactions. The original image or PDF is never included in this call.

The user's API key travels from `localStorage` on their device directly to Google's API. The application has no backend server of its own, so the key is never received, logged, or stored by anyone other than the user and Google.

### API Key Storage

The Gemini API key is stored in the browser's `localStorage` under the key `gemini_api_key`. Before storage, it is lightly obfuscated: the string is reversed and then base64-encoded. This prevents the key from being immediately readable by someone who opens the browser's developer tools.

This is **not encryption**. The README documents this explicitly: "This prevents casual inspection but is NOT secure encryption." The trade-off is intentional — the app targets a general audience, not a threat model that includes attackers with access to the user's device.

### No Tracking, No Telemetry

The app makes no analytics calls, no crash-reporting calls, and no usage-tracking calls. There is no app-controlled server to receive them. The only outbound network call the app ever makes is the Gemini API call described above.

### Browser Requirements

The app requires a modern browser with support for ES2020 syntax, Web Workers (required by Tesseract.js for background OCR processing), and the Fetch API (required for the Gemini API call). Supported browsers: Chrome 90+, Firefox 90+, Safari 15+, Edge 90+. Mobile browsers meeting these requirements are also supported.

---
```

- [ ] **Step 2: Verify Section 6**

Check:
- [ ] No abbreviations re-expanded (AI, PDF, OCR, CSV, API, BYOK, UI, JSON, WASM, DOM already used)
- [ ] Obfuscation method described accurately: reverse + base64 — matches storage.js:13
- [ ] localStorage key name `gemini_api_key` matches storage.js:6
- [ ] OCR text cap 8,000 characters mentioned — matches gemini.js:32
- [ ] "NOT secure encryption" statement included (matching README.md wording)
- [ ] Word count for Section 6 body: approximately 280–320 words

- [ ] **Step 3: Commit**

```bash
git add PROJECT_REPORT.md
git commit -m "docs(report): add Section 6 — Privacy & Security Design"
```

---

## Task 7: Section 7 — Usage Guide

**Files:**
- Modify: `PROJECT_REPORT.md` (append Section 7)

**Interfaces:**
- Consumes: Document through Section 6 (Task 6)
- Produces: Section 7 appended; CLI expanded here (first use)

**Verified technical values for this task:**
- Node.js requirement: 18+ (README.md Prerequisites)
- Dev server URL: http://localhost:5173 (README.md Quick Start)
- npm scripts from package.json: "dev": "vite", "build": "vite build", "preview": "vite preview"
- Production output: `dist/` folder (README.md)
- Vercel deploy: `npm install -g vercel && vercel` (README.md + JOURNEY guide)
- Docker base images: `node:18-alpine` (build), `nginx:alpine` (serve) (README.md)
- Docker expose port: 80 (README.md)
- docker run local port: 8080:80 (JOURNEY guide)
- File types accepted: PNG, JPG, WEBP, PDF (FileUpload.jsx)
- Max file size: 20 MB (ocr.js:25)
- Edit gesture: "click the pencil icon" (App.jsx:349)
- Export formats: CSV (flat), Excel (5 sheets: Summary, Categories, Transactions, Fixed Costs, Variable Costs), PDF (export.js + pdfExport.js)
- Free API key URL: https://aistudio.google.com/apikey (README.md)

- [ ] **Step 1: Append Section 7 to PROJECT_REPORT.md**

Append the following after the `---` that closes Section 6:

```markdown
## 7. Usage Guide

### Prerequisites

- **Node.js 18 or higher** — for local development and building
- **A free Google Gemini API key** — obtain one at [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey). Sign in with a Google account, click "Create API Key", and copy the result. No credit card is required.

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

Follow the prompts. No environment variables are needed — the Gemini API key is provided by the user at runtime, not at build time. The deployed app is publicly accessible immediately after deployment.

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
```

- [ ] **Step 2: Verify Section 7**

Check:
- [ ] "Command-Line Interface (CLI)" — verify this is the first use in the document (CLI not used in Sections 1–6). If not first use, remove the expansion and use CLI only.
- [ ] None of AI, PDF, OCR, CSV, API, BYOK, UI, JSON, WASM, DOM re-expanded
- [ ] `npm run dev` URL is `http://localhost:5173` — matches README.md
- [ ] Node.js requirement is 18+ — matches README.md
- [ ] Docker base images: `node:18-alpine` (build stage), `nginx:alpine` (serve stage) — matches README.md
- [ ] Docker run port is `8080:80` — matches JOURNEY guide
- [ ] File size limit is 20 MB — matches ocr.js:25
- [ ] Three export formats and 5 Excel sheets enumerated correctly
- [ ] All bash commands are copy-pasteable as written
- [ ] Word count for Section 7 body: approximately 340–400 words

- [ ] **Step 3: Commit**

```bash
git add PROJECT_REPORT.md
git commit -m "docs(report): add Section 7 — Usage Guide"
```

---

## Task 8: Section 8 — Tech Stack & Key Design Decisions + Footer

**Files:**
- Modify: `PROJECT_REPORT.md` (append Section 8 + footer)

**Interfaces:**
- Consumes: Document through Section 7 (Task 7)
- Produces: Complete document with footer

**Verified technical values for this task:**
- React version: 18.2.0 (package.json)
- Vite version: 5.0.10 (package.json)
- Tailwind CSS version: 3.4.0 (package.json)
- Tesseract.js version: 5.0.4 (package.json)
- pdfjs-dist version: 4.0.379 (package.json)
- Recharts version: 2.12.0 (package.json)
- xlsx version: 0.18.5 (package.json)
- jsPDF version: 2.5.1 (package.json)
- jspdf-autotable version: 3.8.1 (package.json)
- file-saver version: 2.0.5 (package.json)
- html2canvas version: 1.4.1 (package.json)
- Lucide React version: 0.303.0 (package.json)
- Tailwind production size: ~10 KB purged (README.md Performance section)
- OCR text cap (privacy rationale): 8,000 chars (gemini.js:32)
- BYOK model rationale: zero hosting cost, zero data liability
- updateStatus flag: v1.3.1 bug fix (CHANGELOG.md)
- html2canvas scale: 2× (pdfExport.js:21)
- Three-method JSON salvage (gemini.js:86–132)
- pdf.js worker from jsDelivr CDN (pdf.js)

- [ ] **Step 1: Append Section 8 and footer to PROJECT_REPORT.md**

Append the following after the `---` that closes Section 7:

```markdown
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
Sending the original image to a multimodal model would simplify the pipeline by one step: no OCR needed. The reason to keep OCR is privacy: a multimodal call uploads the full image to Google's servers. By running OCR in the browser first and sending only the extracted text (capped at 8,000 characters), the original financial document never leaves the user's device. Privacy wins over simplicity.

**2. The BYOK model.**
The app has no backend. The user supplies their own Google Gemini API key, which goes directly from their `localStorage` to Google's API. This means zero hosting infrastructure cost (the app is a static site), zero data liability on the app's side, and no rate-limit management required. The trade-off is a slightly higher setup friction for first-time users, mitigated by a link to Google AI Studio and live key validation on entry.

**3. Three-method JSON salvage for truncated AI responses.**
Gemini's 16,384-token output limit causes responses to be cut mid-JSON for large statements with many transactions. Rather than returning an error, the code attempts three recovery methods in sequence: strip markdown code fences, find the outermost `{...}` by character index, and — for structural truncation — find the last complete transaction object, close the JSON structure, and set `bankName` and `period` to `null`. This means a large statement produces partial results rather than a failure, which is more useful than nothing.

**4. The `updateStatus` flag for "Add More" file merging.**
The v1.3.0 "Add More" feature had a state-machine bug: the inner processing function always updated the global `status` variable, which caused the results UI to disappear when a second file was processed (the UI only renders results when `status === 'complete'`). The fix was a single boolean parameter — `processFileInternal(file, updateStatus = true)` — that, when set to `false`, bypasses all global status updates. The outer "Add More" path calls it with `false`, leaving the results view visible throughout. This is a pattern worth noting: when a shared state machine needs to run a sub-process without surfacing its intermediate states, a bypass flag is simpler and safer than splitting the function.

**5. html2canvas for PDF chart capture.**
jsPDF cannot render SVG graphics or React components directly. The solution is to capture the live Recharts chart elements from the DOM using html2canvas at 2× pixel density, convert them to PNG data URLs, and embed those images into the PDF. This gives the PDF report visual parity with the web dashboard at the cost of requiring the charts to be visible in the DOM at the moment of export — which is always the case since the user must be viewing the results screen to click the export button.

---

*Report generated: 2026-06-23 | Author: Jaya Arun Kumar Tulluri | Project version: 1.3.1*
```

- [ ] **Step 2: Verify Section 8**

Check:
- [ ] No abbreviations re-expanded (all already used in Sections 1–7)
- [ ] All version numbers match package.json exactly
- [ ] Tailwind production size "~10 KB" matches README.md Performance section
- [ ] OCR cap "8,000 characters" matches gemini.js:32
- [ ] html2canvas scale "2×" matches pdfExport.js:21
- [ ] updateStatus default parameter syntax `updateStatus = true` matches App.jsx:48
- [ ] Five design decisions each explain "why X over Y" not just "we used X"
- [ ] Footer line present and correctly formatted
- [ ] Word count for Section 8 body: approximately 370–430 words

- [ ] **Step 3: Commit**

```bash
git add PROJECT_REPORT.md
git commit -m "docs(report): add Section 8 — Tech Stack & Design Decisions + footer"
```

---

## Task 9: Final Review — Abbreviation Sweep + Technical Accuracy + Word Count

**Files:**
- Modify: `PROJECT_REPORT.md` (fixes only — no new sections)

**Interfaces:**
- Consumes: Complete document from Tasks 1–8
- Produces: Reviewed, corrected, final document

**What to check:**

### Abbreviation Sweep

Read the document top to bottom. For each abbreviation in the list below, record the section where it first appears and confirm it is expanded there and nowhere else:

| Abbreviation | Must first appear | Must NOT appear expanded again |
|---|---|---|
| AI | Section 1 | Sections 2–8 |
| PDF | Section 1 | Sections 2–8 |
| OCR | Section 1 | Sections 2–8 |
| CSV | Section 1 | Sections 2–8 |
| API | Section 1 | Sections 2–8 |
| BYOK | Section 2 | Sections 3–8 |
| UI | Section 3 | Sections 4–8 |
| JSON | Section 4 | Sections 5–8 |
| WASM | Section 5.1 | Sections 5.2–8 |
| DOM | Section 5.5 | Section 6–8 |
| CLI | Section 7 | Section 8 |

Also check:
- [ ] No abbreviation appears for the first time in unexpanded form
- [ ] Heading text does not re-expand abbreviations (e.g., "Section 7 — Command-Line Interface" would re-expand CLI — use "CLI" in headings after first expansion)

### Technical Accuracy Spot-Checks

Run these greps and compare output to what the document says:

```bash
# Confirm OCR text cap
grep -n "slice" src/utils/gemini.js

# Confirm min text threshold
grep -n "text.length\|< 50" src/utils/ocr.js

# Confirm Gemini endpoint
grep -n "GEMINI_API_URL\|generateContent" src/utils/gemini.js

# Confirm temperature and maxOutputTokens
grep -n "temperature\|maxOutputTokens" src/utils/gemini.js

# Confirm localStorage key name
grep -n "API_KEY_STORAGE_KEY\|gemini_api_key" src/utils/storage.js

# Confirm obfuscation method
grep -n "btoa\|reverse" src/utils/storage.js

# Confirm state values
grep -n "setStatus\|'idle'\|'reading'\|'ocr'\|'extracting'\|'complete'\|'error'" src/App.jsx | head -20

# Confirm updateStatus parameter
grep -n "updateStatus" src/App.jsx

# Confirm html2canvas scale
grep -n "scale" src/utils/pdfExport.js
```

If any value in the document does not match source, fix it.

### Structure Check

- [ ] Table of contents links work (anchors match heading text)
- [ ] Each section ends with `---` except the final footer
- [ ] Footer is the last line: `*Report generated: 2026-06-23 | Author: Jaya Arun Kumar Tulluri | Project version: 1.3.1*`
- [ ] All markdown tables render correctly (pipes aligned, header separator row present)

### Word Count

```bash
wc -w /media/asterisk/1722F6694CF9F147/project/my_learning_projects/expense_tracker/PROJECT_REPORT.md
```

Expected: 2,600–3,400 words. If under 2,600, identify the shortest section and expand with one or two additional paragraphs. If over 3,400, trim the longest section.

### Quality Check

- [ ] No jargon in Sections 1–3 left unexplained
- [ ] All commands in Section 7 are copy-pasteable (no `<placeholder>` except `<repo-url>` which is intentional)
- [ ] Section 8 design decisions each contain "why X over Y" reasoning
- [ ] No placeholder text (TBD, TODO, fill in later) anywhere

- [ ] **Step 1: Run all spot-checks above and fix any discrepancies**

- [ ] **Step 2: Commit final fixes**

```bash
git add PROJECT_REPORT.md
git commit -m "docs(report): final review — abbreviation sweep and accuracy fixes"
```

Report the following in your task output:
- Final word count
- Any fixes made and why
- Any values that differed from the plan and what the correct value was
- Confirmation that all abbreviation sweep checks passed
