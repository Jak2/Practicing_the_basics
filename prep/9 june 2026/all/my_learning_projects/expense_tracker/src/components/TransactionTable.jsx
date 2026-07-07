import { useState, useMemo } from 'react'
import { ArrowUpDown, Pencil, Trash2, Check, X } from 'lucide-react'
import { formatCurrency, formatDate } from '../utils/export'

/**
 * Transaction Table Component
 * Displays extracted transactions with sorting and editing
 */
export default function TransactionTable({ transactions, onUpdate, onDelete }) {
  const [sortField, setSortField] = useState('date')
  const [sortDir, setSortDir] = useState('desc')
  const [editingId, setEditingId] = useState(null)
  const [editValues, setEditValues] = useState({})

  // Sort transactions
  const sorted = useMemo(() => {
    return [...transactions].sort((a, b) => {
      let cmp = 0
      switch (sortField) {
        case 'date':
          cmp = new Date(a.date) - new Date(b.date)
          break
        case 'description':
          cmp = (a.description || '').localeCompare(b.description || '')
          break
        case 'debit':
          cmp = (a.debit || 0) - (b.debit || 0)
          break
        case 'credit':
          cmp = (a.credit || 0) - (b.credit || 0)
          break
        default:
          cmp = 0
      }
      return sortDir === 'asc' ? cmp : -cmp
    })
  }, [transactions, sortField, sortDir])

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDir('asc')
    }
  }

  const startEdit = (t) => {
    setEditingId(t.id)
    setEditValues({
      date: t.date,
      description: t.description,
      debit: t.debit,
      credit: t.credit,
    })
  }

  const saveEdit = () => {
    if (editingId) {
      onUpdate(editingId, editValues)
      setEditingId(null)
    }
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditValues({})
  }

  const SortHeader = ({ field, children, className = '' }) => (
    <th className={`pb-3 font-medium ${className}`}>
      <button
        onClick={() => handleSort(field)}
        className="flex items-center gap-1 hover:text-gray-900 transition-colors"
      >
        {children}
        <ArrowUpDown className={`w-3 h-3 ${sortField === field ? 'text-blue-600' : 'text-gray-300'}`} />
      </button>
    </th>
  )

  if (transactions.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No transactions found
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[600px]">
        <thead>
          <tr className="border-b text-left text-sm text-gray-500">
            <SortHeader field="date">Date</SortHeader>
            <SortHeader field="description">Description</SortHeader>
            <SortHeader field="debit" className="text-right">Debit</SortHeader>
            <SortHeader field="credit" className="text-right">Credit</SortHeader>
            <th className="pb-3 font-medium text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {sorted.map((t) => (
            <tr key={t.id} className="hover:bg-gray-50 transition-colors">
              {editingId === t.id ? (
                // Edit mode
                <>
                  <td className="py-3 pr-4">
                    <input
                      type="date"
                      value={editValues.date || ''}
                      onChange={(e) => setEditValues({ ...editValues, date: e.target.value })}
                      className="w-full px-2 py-1 border rounded text-sm"
                    />
                  </td>
                  <td className="py-3 pr-4">
                    <input
                      type="text"
                      value={editValues.description || ''}
                      onChange={(e) => setEditValues({ ...editValues, description: e.target.value })}
                      className="w-full px-2 py-1 border rounded text-sm"
                    />
                  </td>
                  <td className="py-3 pr-4">
                    <input
                      type="number"
                      value={editValues.debit ?? ''}
                      onChange={(e) => setEditValues({ ...editValues, debit: e.target.value ? Number(e.target.value) : null })}
                      className="w-full px-2 py-1 border rounded text-sm text-right"
                      placeholder="0"
                    />
                  </td>
                  <td className="py-3 pr-4">
                    <input
                      type="number"
                      value={editValues.credit ?? ''}
                      onChange={(e) => setEditValues({ ...editValues, credit: e.target.value ? Number(e.target.value) : null })}
                      className="w-full px-2 py-1 border rounded text-sm text-right"
                      placeholder="0"
                    />
                  </td>
                  <td className="py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={saveEdit}
                        className="p-1.5 text-green-600 hover:bg-green-100 rounded"
                      >
                        <Check className="w-4 h-4" />
                      </button>
                      <button
                        onClick={cancelEdit}
                        className="p-1.5 text-gray-500 hover:bg-gray-100 rounded"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </>
              ) : (
                // Display mode
                <>
                  <td className="py-3 pr-4 text-sm text-gray-700">
                    {formatDate(t.date)}
                  </td>
                  <td className="py-3 pr-4 text-sm text-gray-900 max-w-xs truncate">
                    {t.description}
                  </td>
                  <td className="py-3 pr-4 text-sm text-right text-red-600">
                    {t.debit ? formatCurrency(t.debit) : '-'}
                  </td>
                  <td className="py-3 pr-4 text-sm text-right text-green-600">
                    {t.credit ? formatCurrency(t.credit) : '-'}
                  </td>
                  <td className="py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={() => startEdit(t)}
                        className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                        title="Edit"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => onDelete(t.id)}
                        className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
