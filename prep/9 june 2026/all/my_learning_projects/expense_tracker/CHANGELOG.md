# Changelog

All notable changes to the Financial Statement Parser project are documented in this file.

## [1.3.1] - 2024-XX-XX

### Fixed
- **Add More Files Bug**: Fixed critical issue where adding a second file would replace the first file's data instead of merging
  - Root cause: `processFileInternal` was changing global `status` state, causing UI to re-render and lose context
  - Solution: Added `updateStatus` parameter to `processFileInternal` - when `false`, status remains 'complete' and results stay visible
  - Now properly captures current transactions before processing and merges new transactions correctly
  - Added `transactions` to `useCallback` dependency array for proper closure handling

### Changed
- `processFileInternal()` now accepts optional `updateStatus` parameter (default: `true`)
- `processAdditionalFiles()` preserves existing transactions during "Add More" processing

---

## [1.3.0] - 2024-XX-XX

### Added
- **Multiple File Upload**: Upload multiple bank statements at once
- **Add More Files**: Button to add additional files to existing results
- **Charts & Analytics Dashboard**: Visual representation of spending data
  - Category spending bar chart (Recharts)
  - Fixed vs Variable pie chart
  - Executive summary banner
  - 6 key metric cards
- **Enhanced Excel Export**: Multi-sheet workbook with 5 sheets
  - Summary sheet with key metrics
  - Categories breakdown sheet
  - Transactions sheet (matching webapp view)
  - Fixed Costs sheet
  - Variable Costs sheet
- **Improved PDF Export**: Cleaner layout matching webapp structure
  - Executive summary box with blue styling
  - Key metrics in 2-column layout
  - Category breakdown table
  - Visual analytics with captured charts
  - Transaction table with totals row
  - Page numbers on all pages

### Changed
- FileUpload component now supports multiple files
- Excel export includes category and costType columns
- CSV export includes category and costType columns
- PDF layout restructured to match webapp view

### Dependencies Added
- `recharts: ^2.12.0` - Charting library
- `html2canvas: ^1.4.1` - DOM element capture for PDF charts

---

## [1.2.0] - 2024-XX-XX

### Added
- **Category Classification**: AI automatically classifies transactions
  - 14 categories: Food & Dining, Shopping, Transport, Utilities, Entertainment, Healthcare, Education, Subscriptions, Rent & Housing, Insurance, Transfers, Income, ATM, Other
- **Cost Type Classification**: Fixed vs Variable cost categorization
- **Analytics Utilities** (`analytics.js`):
  - `calculateBurnRate()` - Daily spending velocity
  - `getCategoryTotals()` - Category spending breakdown
  - `getFixedVsVariable()` - Fixed/variable cost analysis
  - `calculateStats()` - Comprehensive statistics
  - `generateSummaryText()` - Executive summary text
- **PDF Export** (`pdfExport.js`): Formatted PDF reports with jsPDF

### Changed
- Gemini prompt updated to include category and costType in response
- Transaction model expanded with `category` and `costType` fields

### Dependencies Added
- `jspdf: ^2.5.1` - PDF generation
- `jspdf-autotable: ^3.8.1` - PDF tables

---

## [1.1.0] - 2024-XX-XX

### Added
- **PDF Support**: Upload and process PDF bank statements
  - Multi-page PDF processing
  - PDF to image conversion with pdf.js
  - Combined OCR for all pages
- **PDF Utilities** (`pdf.js`):
  - `pdfToImages()` - Convert PDF pages to images
  - `isPDF()` - Check if file is PDF
  - `getPDFPageCount()` - Get PDF page count

### Changed
- OCR utility updated to handle both images and PDFs
- FileUpload component accepts PDF files
- Max file size increased to 20MB

### Dependencies Added
- `pdfjs-dist: ^4.0.379` - PDF rendering

### Fixed
- PDF.js worker loading issues (switched to jsdelivr CDN)
- Gemini response truncation handling improved

---

## [1.0.0] - 2024-XX-XX

### Initial Release

#### Features
- **API Key Management**: BYOK (Bring Your Own Key) model
  - Gemini API key input with validation
  - Key stored in localStorage (obfuscated)
  - Settings modal for key management
- **File Upload**: Drag & drop image upload
  - Supports PNG, JPG, WEBP
  - Max 10MB file size
  - Visual feedback on drag
- **OCR Processing**: In-browser text extraction
  - Tesseract.js WASM engine
  - Progress tracking
- **AI Transaction Extraction**: Gemini 2.5 Flash
  - JSON response mode
  - Transaction parsing with structured output
  - Bank name and period detection
- **Results Table**: Editable transaction table
  - Sortable columns
  - Inline editing
  - Row deletion
- **Export Options**:
  - CSV export
  - Excel export (.xlsx)
- **Summary Cards**: Financial overview
  - Total Income
  - Total Expenses
  - Net Cash Flow
  - Transaction count

#### Technical Stack
- React 18
- Vite 5
- Tailwind CSS 3
- Tesseract.js 5
- SheetJS (xlsx)
- file-saver
- Lucide React icons

#### Architecture
- 100% client-side processing
- No backend/database required
- Privacy-first design (files never leave browser)

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.3.1 | TBD | Bug fix: Add More files now properly merges data |
| 1.3.0 | TBD | Multiple files, Charts, Enhanced exports |
| 1.2.0 | TBD | Categories, Cost types, PDF export |
| 1.1.0 | TBD | PDF support |
| 1.0.0 | TBD | Initial release |

---

## Migration Notes

### Upgrading to 1.3.0
```bash
npm install recharts html2canvas
```

### Upgrading to 1.2.0
```bash
npm install jspdf jspdf-autotable
```

### Upgrading to 1.1.0
```bash
npm install pdfjs-dist
```

---

## Known Issues

1. **PDF.js Worker**: May require hard refresh after first install
2. **Gemini Rate Limits**: Free tier has usage limits
3. **Large PDFs**: Processing time increases with page count
4. **OCR Quality**: Depends on image/PDF clarity

---

## Roadmap

### Planned Features
- [ ] Dark mode
- [ ] Multiple statement comparison
- [ ] Custom categories
- [ ] Transaction search/filter
- [ ] PWA support
- [ ] Data persistence (IndexedDB)
- [ ] Chart customization

### Under Consideration
- Receipt scanning
- Budget tracking
- Recurring transaction detection
- Multi-currency support
