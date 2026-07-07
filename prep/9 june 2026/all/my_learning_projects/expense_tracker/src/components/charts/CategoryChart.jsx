import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { getCategoryTotals } from '../../utils/analytics'

// Color palette for categories
const COLORS = [
  '#3B82F6', // blue
  '#10B981', // green
  '#F59E0B', // amber
  '#EF4444', // red
  '#8B5CF6', // violet
  '#EC4899', // pink
  '#06B6D4', // cyan
  '#F97316', // orange
  '#6366F1', // indigo
  '#84CC16', // lime
  '#14B8A6', // teal
  '#A855F7', // purple
  '#64748B', // slate
  '#78716C', // stone
]

/**
 * Category spending bar chart
 */
export default function CategoryChart({ transactions }) {
  const categoryData = getCategoryTotals(transactions)
    .filter(c => c.amount > 0)
    .slice(0, 8) // Top 8 categories for readability

  if (categoryData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No spending data available
      </div>
    )
  }

  // Calculate total for percentage
  const total = categoryData.reduce((sum, c) => sum + c.amount, 0)

  // Format data with percentages
  const chartData = categoryData.map(c => ({
    ...c,
    percent: ((c.amount / total) * 100).toFixed(1),
    shortName: c.category.length > 12 ? c.category.slice(0, 10) + '...' : c.category
  }))

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value)
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="font-medium text-gray-900">{data.category}</p>
          <p className="text-sm text-gray-600">{formatCurrency(data.amount)}</p>
          <p className="text-xs text-gray-500">{data.percent}% of total</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-64" id="category-chart">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
          <XAxis
            type="number"
            tickFormatter={formatCurrency}
            tick={{ fontSize: 11 }}
          />
          <YAxis
            type="category"
            dataKey="shortName"
            width={80}
            tick={{ fontSize: 11 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="amount" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
