import { useState } from 'react'
import { FileSpreadsheet, FileText, FileDown, Loader2 } from 'lucide-react'
import { exportToCSV, exportToExcel } from '../utils/export'
import { exportToPDF } from '../utils/pdfExport'

/**
 * Export Buttons Component
 * Allows exporting transactions to CSV, Excel, or PDF
 */
export default function ExportButtons({ transactions, bankName = null, period = null }) {
  const [exporting, setExporting] = useState(null)

  const handleExport = async (format) => {
    if (transactions.length === 0) return

    setExporting(format)
    await new Promise(r => setTimeout(r, 200)) // Brief delay for UX

    const filename = `transactions_${new Date().toISOString().split('T')[0]}`

    try {
      if (format === 'csv') {
        exportToCSV(transactions, filename)
      } else if (format === 'excel') {
        exportToExcel(transactions, filename)
      } else if (format === 'pdf') {
        await exportToPDF(transactions, bankName, period, `financial-report_${new Date().toISOString().split('T')[0]}`)
      }
    } catch (error) {
      console.error('Export failed:', error)
    }

    setExporting(null)
  }

  const disabled = transactions.length === 0

  return (
    <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
      {/* CSV Export */}
      <button
        onClick={() => handleExport('csv')}
        disabled={disabled || exporting}
        className={`
          flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl
          border border-gray-300 bg-white
          text-sm font-medium text-gray-700
          transition-colors
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50 hover:border-gray-400'}
        `}
      >
        {exporting === 'csv' ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <FileText className="w-4 h-4" />
        )}
        CSV
      </button>

      {/* Excel Export */}
      <button
        onClick={() => handleExport('excel')}
        disabled={disabled || exporting}
        className={`
          flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl
          border border-green-300 bg-green-50
          text-sm font-medium text-green-700
          transition-colors
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-green-100 hover:border-green-400'}
        `}
      >
        {exporting === 'excel' ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <FileSpreadsheet className="w-4 h-4" />
        )}
        Excel
      </button>

      {/* PDF Report Export */}
      <button
        onClick={() => handleExport('pdf')}
        disabled={disabled || exporting}
        className={`
          flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl
          bg-blue-600 text-white
          text-sm font-medium
          transition-colors
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'}
        `}
      >
        {exporting === 'pdf' ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <FileDown className="w-4 h-4" />
        )}
        PDF Report
      </button>
    </div>
  )
}
