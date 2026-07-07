/**
 * PDF Export utility for generating formatted financial reports
 * Layout designed to match the webapp view structure
 */

import jsPDF from 'jspdf'
import 'jspdf-autotable'
import html2canvas from 'html2canvas'
import { calculateStats, generateSummaryText, formatCurrency } from './analytics'

/**
 * Capture a DOM element as an image
 */
async function captureElement(elementId) {
  const element = document.getElementById(elementId)
  if (!element) return null

  try {
    const canvas = await html2canvas(element, {
      scale: 2,
      backgroundColor: '#ffffff',
      logging: false
    })
    return canvas.toDataURL('image/png')
  } catch (error) {
    console.warn(`Failed to capture ${elementId}:`, error)
    return null
  }
}

/**
 * Generate a formatted PDF report matching webapp view
 */
export async function exportToPDF(transactions, bankName = null, period = null, filename = 'financial-report') {
  const doc = new jsPDF()
  const stats = calculateStats(transactions)
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const margin = 14

  let yPos = 20

  // === PAGE 1: SUMMARY ===

  // Title
  doc.setFontSize(22)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(17, 24, 39) // gray-900
  doc.text('Financial Summary Report', pageWidth / 2, yPos, { align: 'center' })
  yPos += 10

  // Subtitle - Bank name and period
  doc.setFontSize(11)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(107, 114, 128) // gray-500
  const bankLine = bankName || 'Bank Statement Analysis'
  doc.text(bankLine, pageWidth / 2, yPos, { align: 'center' })
  yPos += 5

  if (period) {
    doc.text(period, pageWidth / 2, yPos, { align: 'center' })
    yPos += 5
  }

  doc.setFontSize(9)
  doc.text(`Generated: ${new Date().toLocaleDateString('en-IN')}`, pageWidth / 2, yPos, { align: 'center' })
  yPos += 12

  // === EXECUTIVE SUMMARY BOX (Blue gradient style) ===
  doc.setFillColor(59, 130, 246) // blue-600
  doc.roundedRect(margin, yPos, pageWidth - 2 * margin, 28, 3, 3, 'F')

  doc.setFontSize(11)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(255, 255, 255)
  doc.text('Executive Summary', margin + 8, yPos + 8)

  doc.setFontSize(9)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(219, 234, 254) // blue-100
  const summaryText = generateSummaryText(stats, bankName, period)
  const splitSummary = doc.splitTextToSize(summaryText, pageWidth - 2 * margin - 16)
  doc.text(splitSummary, margin + 8, yPos + 16)

  yPos += 35

  // === KEY METRICS GRID (2 columns) ===
  doc.setFontSize(12)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(17, 24, 39)
  doc.text('Key Metrics', margin, yPos)
  yPos += 8

  const metricsLeft = [
    ['Total Income', formatCurrency(stats.totalCredit)],
    ['Total Expenses', formatCurrency(stats.totalDebit)],
    ['Net Cash Flow', formatCurrency(stats.netFlow)],
  ]

  const metricsRight = [
    ['Daily Burn Rate', `${formatCurrency(stats.dailyBurnRate)}/day`],
    ['Fixed Costs', `${formatCurrency(stats.costBreakdown.fixed.total)} (${stats.costBreakdown.fixedPercent.toFixed(0)}%)`],
    ['Variable Costs', `${formatCurrency(stats.costBreakdown.variable.total)} (${stats.costBreakdown.variablePercent.toFixed(0)}%)`],
  ]

  // Left metrics table
  doc.autoTable({
    startY: yPos,
    body: metricsLeft,
    theme: 'plain',
    styles: { fontSize: 10, cellPadding: 3 },
    columnStyles: {
      0: { fontStyle: 'bold', textColor: [75, 85, 99], cellWidth: 45 },
      1: { halign: 'right', textColor: [17, 24, 39], cellWidth: 45 }
    },
    margin: { left: margin, right: pageWidth / 2 + 5 }
  })

  // Right metrics table
  doc.autoTable({
    startY: yPos,
    body: metricsRight,
    theme: 'plain',
    styles: { fontSize: 10, cellPadding: 3 },
    columnStyles: {
      0: { fontStyle: 'bold', textColor: [75, 85, 99], cellWidth: 45 },
      1: { halign: 'right', textColor: [17, 24, 39], cellWidth: 45 }
    },
    margin: { left: pageWidth / 2, right: margin }
  })

  yPos = doc.lastAutoTable.finalY + 15

  // === CATEGORY BREAKDOWN ===
  doc.setFontSize(12)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(17, 24, 39)
  doc.text('Spending by Category', margin, yPos)
  yPos += 6

  const categoryData = stats.categoryTotals
    .filter(c => c.amount > 0)
    .slice(0, 10)
    .map(c => [
      c.category,
      formatCurrency(c.amount),
      stats.totalDebit > 0 ? `${((c.amount / stats.totalDebit) * 100).toFixed(1)}%` : '0%'
    ])

  if (categoryData.length > 0) {
    doc.autoTable({
      startY: yPos,
      head: [['Category', 'Amount', '% of Total']],
      body: categoryData,
      theme: 'striped',
      headStyles: { fillColor: [34, 197, 94], fontSize: 9, fontStyle: 'bold', textColor: 255 },
      bodyStyles: { fontSize: 9 },
      alternateRowStyles: { fillColor: [249, 250, 251] },
      columnStyles: {
        0: { cellWidth: 65 },
        1: { halign: 'right', cellWidth: 45 },
        2: { halign: 'right', cellWidth: 35 }
      },
      margin: { left: margin, right: pageWidth / 2 + 10 }
    })
  }

  // === CHARTS (capture from DOM if visible) ===
  const categoryChartImage = await captureElement('category-chart')
  const costChartImage = await captureElement('cost-breakdown-chart')

  if (categoryChartImage || costChartImage) {
    yPos = doc.lastAutoTable ? doc.lastAutoTable.finalY + 15 : yPos + 15

    if (yPos > 180) {
      doc.addPage()
      yPos = 20
    }

    doc.setFontSize(12)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(17, 24, 39)
    doc.text('Visual Analytics', margin, yPos)
    yPos += 8

    const chartWidth = 85
    const chartHeight = 55

    if (categoryChartImage) {
      doc.addImage(categoryChartImage, 'PNG', margin, yPos, chartWidth, chartHeight)
    }

    if (costChartImage) {
      doc.addImage(costChartImage, 'PNG', pageWidth / 2 + 5, yPos, chartWidth, chartHeight)
    }
  }

  // === PAGE 2+: TRANSACTIONS ===
  doc.addPage()
  yPos = 20

  doc.setFontSize(14)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(17, 24, 39)
  doc.text('Transaction Details', margin, yPos)

  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(107, 114, 128)
  doc.text(`${transactions.length} transactions`, margin + 90, yPos)
  yPos += 8

  const txnData = transactions.map(t => [
    t.date || '-',
    (t.description || '').substring(0, 32),
    t.category || 'Other',
    t.debit ? formatCurrency(t.debit) : '-',
    t.credit ? formatCurrency(t.credit) : '-'
  ])

  doc.autoTable({
    startY: yPos,
    head: [['Date', 'Description', 'Category', 'Debit', 'Credit']],
    body: txnData,
    foot: [['', 'TOTAL', '', formatCurrency(stats.totalDebit), formatCurrency(stats.totalCredit)]],
    theme: 'striped',
    headStyles: { fillColor: [71, 85, 105], fontSize: 9, fontStyle: 'bold', textColor: 255 },
    bodyStyles: { fontSize: 8 },
    footStyles: { fillColor: [243, 244, 246], fontStyle: 'bold', fontSize: 9, textColor: [17, 24, 39] },
    alternateRowStyles: { fillColor: [249, 250, 251] },
    columnStyles: {
      0: { cellWidth: 24 },
      1: { cellWidth: 58 },
      2: { cellWidth: 32 },
      3: { halign: 'right', cellWidth: 28 },
      4: { halign: 'right', cellWidth: 28 }
    },
    margin: { left: margin, right: margin },
    didDrawPage: () => {
      // Page number footer on every page
      doc.setFontSize(8)
      doc.setTextColor(156, 163, 175)
      doc.text(
        `Page ${doc.internal.getNumberOfPages()}`,
        pageWidth / 2,
        pageHeight - 10,
        { align: 'center' }
      )
    }
  })

  // Final footer
  const finalY = doc.lastAutoTable.finalY + 12
  if (finalY < pageHeight - 25) {
    doc.setFontSize(8)
    doc.setTextColor(156, 163, 175)
    doc.text('Generated by Financial Statement Parser', margin, finalY)
  }

  // Save
  doc.save(`${filename}.pdf`)
}
