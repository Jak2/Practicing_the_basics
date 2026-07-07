/**
 * Export utilities for CSV and Excel
 */

import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import { calculateStats, getCategoryTotals, getFixedVsVariable } from './analytics'

/**
 * Format currency for display
 */
export function formatCurrency(amount, currency = 'INR') {
  if (amount === null || amount === undefined) return '-'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
  }).format(amount)
}

/**
 * Format date for display
 */
export function formatDate(dateStr) {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return dateStr
  }
}

/**
 * Calculate summary from transactions
 */
export function calculateSummary(transactions) {
  const totalDebit = transactions.reduce((sum, t) => sum + (t.debit || 0), 0)
  const totalCredit = transactions.reduce((sum, t) => sum + (t.credit || 0), 0)

  return {
    totalDebit,
    totalCredit,
    netFlow: totalCredit - totalDebit,
    count: transactions.length,
  }
}

/**
 * Export transactions to CSV (includes category and costType)
 */
export function exportToCSV(transactions, filename = 'transactions') {
  const headers = ['Date', 'Description', 'Category', 'Cost Type', 'Debit', 'Credit', 'Balance', 'Reference']

  const rows = transactions.map(t => [
    t.date,
    t.description,
    t.category || 'Other',
    t.costType || 'variable',
    t.debit ?? '',
    t.credit ?? '',
    t.balance ?? '',
    t.reference ?? '',
  ])

  const csv = [
    headers.join(','),
    ...rows.map(row =>
      row.map(cell => {
        const str = String(cell)
        return str.includes(',') || str.includes('"')
          ? `"${str.replace(/"/g, '""')}"`
          : str
      }).join(',')
    ),
  ].join('\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  saveAs(blob, `${filename}.csv`)
}

/**
 * Export transactions to Excel with multiple sheets (matching webapp view)
 */
export function exportToExcel(transactions, filename = 'transactions') {
  const wb = XLSX.utils.book_new()
  const stats = calculateStats(transactions)

  // === SHEET 1: Summary (matches webapp analytics dashboard) ===
  const summaryData = [
    ['FINANCIAL SUMMARY REPORT'],
    ['Generated:', new Date().toLocaleDateString('en-IN')],
    [''],
    ['KEY METRICS'],
    ['Total Income', stats.totalCredit],
    ['Total Expenses', stats.totalDebit],
    ['Net Cash Flow', stats.netFlow],
    ['Daily Burn Rate', stats.dailyBurnRate],
    ['Transaction Count', stats.transactionCount],
    ['Period (Days)', stats.periodDays],
    [''],
    ['COST BREAKDOWN'],
    ['Fixed Costs', stats.costBreakdown.fixed.total, `${stats.costBreakdown.fixedPercent.toFixed(1)}%`],
    ['Variable Costs', stats.costBreakdown.variable.total, `${stats.costBreakdown.variablePercent.toFixed(1)}%`],
    [''],
    ['EXECUTIVE SUMMARY'],
    [stats.isPositive
      ? `Cash Flow Positive by ${formatCurrency(Math.abs(stats.netFlow))}`
      : `Cash Flow Negative by ${formatCurrency(Math.abs(stats.netFlow))}`
    ],
    [`Top spending category: ${stats.topCategory.category} (${formatCurrency(stats.topCategory.amount)})`],
  ]

  const wsSummary = XLSX.utils.aoa_to_sheet(summaryData)
  wsSummary['!cols'] = [{ wch: 25 }, { wch: 20 }, { wch: 15 }]
  XLSX.utils.book_append_sheet(wb, wsSummary, 'Summary')

  // === SHEET 2: Category Breakdown ===
  const categoryTotals = getCategoryTotals(transactions)
  const categoryData = [
    ['SPENDING BY CATEGORY'],
    ['Category', 'Amount', '% of Total'],
    ...categoryTotals
      .filter(c => c.amount > 0)
      .map(c => [
        c.category,
        c.amount,
        stats.totalDebit > 0 ? `${((c.amount / stats.totalDebit) * 100).toFixed(1)}%` : '0%'
      ])
  ]

  const wsCategory = XLSX.utils.aoa_to_sheet(categoryData)
  wsCategory['!cols'] = [{ wch: 20 }, { wch: 15 }, { wch: 12 }]
  XLSX.utils.book_append_sheet(wb, wsCategory, 'Categories')

  // === SHEET 3: Transactions (main data matching webapp table) ===
  const txnHeaders = ['Date', 'Description', 'Category', 'Cost Type', 'Debit', 'Credit', 'Balance']
  const txnData = [
    txnHeaders,
    ...transactions.map(t => [
      t.date || '',
      t.description || '',
      t.category || 'Other',
      t.costType || 'variable',
      t.debit || '',
      t.credit || '',
      t.balance || '',
    ]),
    [], // Empty row before totals
    ['', 'TOTALS', '', '', stats.totalDebit, stats.totalCredit, '']
  ]

  const wsTransactions = XLSX.utils.aoa_to_sheet(txnData)
  wsTransactions['!cols'] = [
    { wch: 12 },  // Date
    { wch: 40 },  // Description
    { wch: 15 },  // Category
    { wch: 10 },  // Cost Type
    { wch: 12 },  // Debit
    { wch: 12 },  // Credit
    { wch: 12 },  // Balance
  ]
  XLSX.utils.book_append_sheet(wb, wsTransactions, 'Transactions')

  // === SHEET 4: Fixed Costs ===
  const fixedData = [
    ['FIXED COSTS (Recurring/Essential)'],
    ['Date', 'Description', 'Category', 'Amount'],
    ...stats.costBreakdown.fixed.items.map(t => [
      t.date || '',
      t.description || '',
      t.category || '',
      t.debit || 0
    ]),
    [],
    ['', '', 'TOTAL', stats.costBreakdown.fixed.total]
  ]

  const wsFixed = XLSX.utils.aoa_to_sheet(fixedData)
  wsFixed['!cols'] = [{ wch: 12 }, { wch: 40 }, { wch: 15 }, { wch: 12 }]
  XLSX.utils.book_append_sheet(wb, wsFixed, 'Fixed Costs')

  // === SHEET 5: Variable Costs ===
  const variableData = [
    ['VARIABLE COSTS (Discretionary)'],
    ['Date', 'Description', 'Category', 'Amount'],
    ...stats.costBreakdown.variable.items.map(t => [
      t.date || '',
      t.description || '',
      t.category || '',
      t.debit || 0
    ]),
    [],
    ['', '', 'TOTAL', stats.costBreakdown.variable.total]
  ]

  const wsVariable = XLSX.utils.aoa_to_sheet(variableData)
  wsVariable['!cols'] = [{ wch: 12 }, { wch: 40 }, { wch: 15 }, { wch: 12 }]
  XLSX.utils.book_append_sheet(wb, wsVariable, 'Variable Costs')

  // Write file
  const buffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  const blob = new Blob([buffer], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  })
  saveAs(blob, `${filename}.xlsx`)
}
