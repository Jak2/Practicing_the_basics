import { TrendingUp, TrendingDown, Wallet, Calendar, Target, PiggyBank } from 'lucide-react'
import { calculateStats, formatCurrency } from '../../utils/analytics'
import CategoryChart from './CategoryChart'
import CostBreakdownChart from './CostBreakdownChart'

/**
 * Analytics Dashboard with charts and key metrics
 */
export default function AnalyticsDashboard({ transactions, bankName, period }) {
  const stats = calculateStats(transactions)

  const MetricCard = ({ icon: Icon, label, value, subtext, color = 'blue' }) => {
    const colorClasses = {
      blue: 'bg-blue-50 text-blue-600',
      green: 'bg-green-50 text-green-600',
      red: 'bg-red-50 text-red-600',
      amber: 'bg-amber-50 text-amber-600',
      violet: 'bg-violet-50 text-violet-600'
    }

    return (
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
            <Icon className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
            <p className="text-lg font-semibold text-gray-900 truncate">{value}</p>
            {subtext && <p className="text-xs text-gray-500">{subtext}</p>}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6" id="analytics-dashboard">
      {/* Executive Summary */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-6 text-white">
        <h2 className="text-lg font-semibold mb-2">Executive Summary</h2>
        <p className="text-blue-100 text-sm leading-relaxed">
          {stats.isPositive ? (
            <>
              You are <span className="font-semibold text-green-300">Cash Flow Positive</span> by{' '}
              {formatCurrency(Math.abs(stats.netFlow))}.
            </>
          ) : (
            <>
              You are <span className="font-semibold text-red-300">Cash Flow Negative</span> by{' '}
              {formatCurrency(Math.abs(stats.netFlow))}.
            </>
          )}
          {' '}Your largest spending category is "{stats.topCategory.category}" at{' '}
          {formatCurrency(stats.topCategory.amount)}.
          {stats.dailyBurnRate > 0 && (
            <> Daily spending rate: {formatCurrency(stats.dailyBurnRate)}/day.</>
          )}
        </p>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <MetricCard
          icon={TrendingUp}
          label="Total Income"
          value={formatCurrency(stats.totalCredit)}
          color="green"
        />
        <MetricCard
          icon={TrendingDown}
          label="Total Expenses"
          value={formatCurrency(stats.totalDebit)}
          color="red"
        />
        <MetricCard
          icon={Wallet}
          label="Net Cash Flow"
          value={formatCurrency(stats.netFlow)}
          color={stats.isPositive ? 'green' : 'red'}
        />
        <MetricCard
          icon={Target}
          label="Daily Burn Rate"
          value={formatCurrency(stats.dailyBurnRate)}
          subtext="per day"
          color="amber"
        />
        <MetricCard
          icon={PiggyBank}
          label="Fixed Costs"
          value={formatCurrency(stats.costBreakdown.fixed.total)}
          subtext={`${stats.costBreakdown.fixedPercent.toFixed(0)}% of expenses`}
          color="violet"
        />
        <MetricCard
          icon={Calendar}
          label="Period"
          value={`${stats.periodDays} days`}
          subtext={`${stats.transactionCount} transactions`}
          color="blue"
        />
      </div>

      {/* Charts Row */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="bg-white rounded-2xl border border-gray-200 p-4 sm:p-6">
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            Spending by Category
          </h3>
          <CategoryChart transactions={transactions} />
        </div>

        {/* Fixed vs Variable */}
        <div className="bg-white rounded-2xl border border-gray-200 p-4 sm:p-6">
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            Fixed vs Variable Costs
          </h3>
          <CostBreakdownChart transactions={transactions} />

          {/* Legend explanation */}
          <div className="mt-4 grid grid-cols-2 gap-3 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span className="text-gray-600">Fixed: Rent, Bills, Insurance</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-gray-600">Variable: Food, Shopping, etc.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
