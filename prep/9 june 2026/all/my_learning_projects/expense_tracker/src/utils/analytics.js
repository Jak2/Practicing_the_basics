/**
 * Analytics utilities for financial insights
 */

/**
 * Calculate spending velocity (daily burn rate)
 */
export function calculateBurnRate(transactions, periodDays = 30) {
  const totalDebit = transactions.reduce((sum, t) => sum + (t.debit || 0), 0)
  return periodDays > 0 ? totalDebit / periodDays : 0
}

/**
 * Get category totals sorted by amount (for Pareto chart)
 */
export function getCategoryTotals(transactions) {
  const totals = {}

  transactions.forEach(t => {
    const category = t.category || 'Other'
    const amount = t.debit || 0
    totals[category] = (totals[category] || 0) + amount
  })

  // Sort by amount descending
  return Object.entries(totals)
    .map(([category, amount]) => ({ category, amount }))
    .sort((a, b) => b.amount - a.amount)
}

/**
 * Get fixed vs variable cost breakdown
 */
export function getFixedVsVariable(transactions) {
  const fixed = { total: 0, items: [] }
  const variable = { total: 0, items: [] }

  transactions.forEach(t => {
    if (!t.debit) return

    if (t.costType === 'fixed') {
      fixed.total += t.debit
      fixed.items.push(t)
    } else {
      variable.total += t.debit
      variable.items.push(t)
    }
  })

  const totalExpenses = fixed.total + variable.total

  return {
    fixed,
    variable,
    totalExpenses,
    fixedPercent: totalExpenses > 0 ? (fixed.total / totalExpenses) * 100 : 0,
    variablePercent: totalExpenses > 0 ? (variable.total / totalExpenses) * 100 : 0
  }
}

/**
 * Calculate comprehensive summary statistics
 */
export function calculateStats(transactions) {
  const totalDebit = transactions.reduce((sum, t) => sum + (t.debit || 0), 0)
  const totalCredit = transactions.reduce((sum, t) => sum + (t.credit || 0), 0)
  const netFlow = totalCredit - totalDebit

  // Get date range
  const dates = transactions
    .map(t => t.date)
    .filter(d => d)
    .sort()

  const startDate = dates[0] || null
  const endDate = dates[dates.length - 1] || null

  // Calculate period in days
  let periodDays = 30
  if (startDate && endDate) {
    const start = new Date(startDate)
    const end = new Date(endDate)
    periodDays = Math.max(1, Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1)
  }

  // Category breakdown
  const categoryTotals = getCategoryTotals(transactions)
  const topCategory = categoryTotals[0] || { category: 'None', amount: 0 }

  // Fixed vs variable
  const costBreakdown = getFixedVsVariable(transactions)

  // Largest expense
  const largestExpense = transactions.reduce((max, t) => {
    return (t.debit || 0) > (max.debit || 0) ? t : max
  }, { debit: 0, description: 'None' })

  // Burn rate
  const dailyBurnRate = calculateBurnRate(transactions, periodDays)

  return {
    totalDebit,
    totalCredit,
    netFlow,
    transactionCount: transactions.length,
    startDate,
    endDate,
    periodDays,
    dailyBurnRate,
    topCategory,
    categoryTotals,
    costBreakdown,
    largestExpense,
    isPositive: netFlow >= 0
  }
}

/**
 * Generate executive summary text
 */
export function generateSummaryText(stats, bankName, period) {
  const flowStatus = stats.isPositive ? 'positive' : 'negative'
  const flowAmount = Math.abs(stats.netFlow).toFixed(2)

  let summary = `Statement Period: ${period || `${stats.startDate || 'N/A'} to ${stats.endDate || 'N/A'}`}. `

  if (stats.isPositive) {
    summary += `You are Cash Flow Positive by ${flowAmount}. `
  } else {
    summary += `You are Cash Flow Negative by ${flowAmount}. `
  }

  summary += `Your largest spending category is "${stats.topCategory.category}" at ${stats.topCategory.amount.toFixed(2)}. `

  if (stats.largestExpense.debit > 0) {
    summary += `Largest single expense: "${stats.largestExpense.description}" (${stats.largestExpense.debit.toFixed(2)}).`
  }

  return summary
}

/**
 * Format currency with locale
 */
export function formatCurrency(amount, currency = 'INR') {
  if (amount === null || amount === undefined) return '-'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2
  }).format(amount)
}

/**
 * Format date for display
 */
export function formatDate(dateString) {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch {
    return dateString
  }
}
