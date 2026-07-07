import { ArrowUpRight, ArrowDownLeft, TrendingUp, Hash } from 'lucide-react'
import { formatCurrency, calculateSummary } from '../utils/export'

/**
 * Summary Cards Component
 * Shows financial summary of transactions
 */
export default function Summary({ transactions, bankName, period }) {
  const summary = calculateSummary(transactions)

  return (
    <div className="space-y-4">
      {/* Bank info */}
      {(bankName || period) && (
        <div className="text-sm text-gray-500">
          {bankName && <span className="font-medium text-gray-700">{bankName}</span>}
          {bankName && period && ' • '}
          {period && <span>{period}</span>}
        </div>
      )}

      {/* Summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {/* Total Debit */}
        <div className="p-4 rounded-xl bg-red-50 border border-red-100">
          <div className="flex items-center gap-2 text-red-600 mb-2">
            <ArrowUpRight className="w-4 h-4" />
            <span className="text-xs sm:text-sm font-medium">Total Debit</span>
          </div>
          <p className="text-lg sm:text-xl font-bold text-red-700">
            {formatCurrency(summary.totalDebit)}
          </p>
        </div>

        {/* Total Credit */}
        <div className="p-4 rounded-xl bg-green-50 border border-green-100">
          <div className="flex items-center gap-2 text-green-600 mb-2">
            <ArrowDownLeft className="w-4 h-4" />
            <span className="text-xs sm:text-sm font-medium">Total Credit</span>
          </div>
          <p className="text-lg sm:text-xl font-bold text-green-700">
            {formatCurrency(summary.totalCredit)}
          </p>
        </div>

        {/* Net Flow */}
        <div className="p-4 rounded-xl bg-blue-50 border border-blue-100">
          <div className="flex items-center gap-2 text-blue-600 mb-2">
            <TrendingUp className="w-4 h-4" />
            <span className="text-xs sm:text-sm font-medium">Net Flow</span>
          </div>
          <p className={`text-lg sm:text-xl font-bold ${
            summary.netFlow >= 0 ? 'text-green-700' : 'text-red-700'
          }`}>
            {summary.netFlow >= 0 ? '+' : ''}{formatCurrency(summary.netFlow)}
          </p>
        </div>

        {/* Count */}
        <div className="p-4 rounded-xl bg-gray-100 border border-gray-200">
          <div className="flex items-center gap-2 text-gray-600 mb-2">
            <Hash className="w-4 h-4" />
            <span className="text-xs sm:text-sm font-medium">Transactions</span>
          </div>
          <p className="text-lg sm:text-xl font-bold text-gray-900">
            {summary.count}
          </p>
        </div>
      </div>
    </div>
  )
}
