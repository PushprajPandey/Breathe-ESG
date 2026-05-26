import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { api, getErrorMessage } from '../api/client'
import { RecordActions } from '../components/RecordActions'
import {
  getColumnsForSource,
  getTableTitle,
  ScopeColumnCell,
  showScopeColumn,
  type SourceFilter,
} from '../components/reviewColumns'
import type { NormalizedRecord } from '../types'

const PAGE_SIZE = 20

interface PaginatedRecords {
  count: number
  next: string | null
  previous: string | null
  results: NormalizedRecord[]
}

export function ReviewPage() {
  const [statusFilter, setStatusFilter] = useState('')
  const [sourceFilter, setSourceFilter] = useState<SourceFilter>('')
  const [selected, setSelected] = useState<number[]>([])
  const [page, setPage] = useState(1)
  const qc = useQueryClient()

  const columns = getColumnsForSource(sourceFilter)
  const includeScope = showScopeColumn(sourceFilter)

  useEffect(() => {
    setPage(1)
    setSelected([])
  }, [statusFilter, sourceFilter])

  const { data, isLoading } = useQuery({
    queryKey: ['records', statusFilter, sourceFilter, page],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: PAGE_SIZE }
      if (statusFilter) params.review_status = statusFilter
      if (sourceFilter) params.source_type = sourceFilter
      const { data: res } = await api.get<PaginatedRecords>('/records/', { params })
      return res
    },
  })

  const records = data?.results ?? []
  const totalCount = data?.count ?? 0
  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE))

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['records'] })
    qc.invalidateQueries({ queryKey: ['stats'] })
    qc.invalidateQueries({ queryKey: ['audit'] })
  }

  const approve = useMutation({
    mutationFn: (id: number) => api.patch(`/records/${id}/approve/`),
    onSuccess: () => {
      toast.success('Record approved')
      invalidate()
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  })

  const flag = useMutation({
    mutationFn: (id: number) => api.patch(`/records/${id}/flag/`),
    onSuccess: () => {
      toast.success('Record flagged')
      invalidate()
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  })

  const reject = useMutation({
    mutationFn: (id: number) => api.patch(`/records/${id}/reject/`),
    onSuccess: () => {
      toast.success('Record rejected')
      invalidate()
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  })

  const bulkApprove = useMutation({
    mutationFn: (ids: number[]) => api.patch('/records/bulk-approve/', { ids }),
    onSuccess: (res) => {
      toast.success(`Approved ${res.data.count} records`)
      setSelected([])
      invalidate()
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  })

  const toggle = (id: number) => {
    setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]))
  }

  const colSpan = columns.length + (includeScope ? 1 : 0) + 2

  return (
    <div>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-lg gap-sm">
        <div>
          <h2 className="font-headline-md text-headline-md text-on-background">Review Data Entries</h2>
          <p className="font-body-sm text-on-surface-variant">
            Analyst view: validate ingested emissions data before ledger commitment.
          </p>
        </div>
        <button
          type="button"
          disabled={!selected.length || bulkApprove.isPending}
          onClick={() => bulkApprove.mutate(selected)}
          className="bg-primary text-on-primary font-label-md py-sm px-lg rounded-xl flex items-center gap-xs disabled:opacity-50"
        >
          <span className="material-symbols-outlined text-[20px]">done_all</span>
          Bulk Approve
        </button>
      </div>
      <div className="bg-surface-container-lowest rounded-xl p-sm border border-outline-variant mb-lg flex flex-wrap gap-sm items-center">
        <div className="flex items-center gap-xs text-on-surface-variant font-label-sm border-r border-outline-variant pr-sm mr-xs">
          <span className="material-symbols-outlined text-[18px]">filter_list</span>
          FILTERS
        </div>
        <select
          value={sourceFilter}
          onChange={(e) => setSourceFilter(e.target.value as SourceFilter)}
          className="border border-outline-variant rounded-lg px-sm py-xs font-body-sm bg-surface-container-low"
        >
          <option value="">Source: All</option>
          <option value="sap">SAP (Scope 1)</option>
          <option value="utility">Utility (Scope 2)</option>
          <option value="travel">Travel (Scope 3)</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="border border-outline-variant rounded-lg px-sm py-xs font-body-sm bg-surface-container-low"
        >
          <option value="">Status: All</option>
          <option value="PENDING">Pending</option>
          <option value="APPROVED">Approved</option>
          <option value="FLAGGED">Flagged</option>
        </select>
        <span className="font-label-sm text-on-surface-variant ml-auto">{getTableTitle(sourceFilter)}</span>
      </div>
      {isLoading ? (
        <p className="font-body-sm text-on-surface-variant">Loading records…</p>
      ) : (
        <>
          <div className="bg-surface-container-lowest rounded-xl border border-outline-variant overflow-x-auto shadow-[0_2px_4px_rgba(31,41,55,0.05)]">
            <table className="w-full min-w-[900px] text-left border-collapse">
              <thead>
                <tr className="border-b border-outline-variant bg-surface-container-low text-on-surface-variant font-label-md text-label-md uppercase tracking-wider">
                  <th className="p-sm pl-md w-10" />
                  {columns.map((col) => (
                    <th
                      key={col.id}
                      className={`p-sm font-semibold ${col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'}`}
                    >
                      {col.label}
                    </th>
                  ))}
                  {includeScope && <th className="p-sm font-semibold text-center">Scope</th>}
                  <th className="p-sm pr-md font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="font-body-sm text-body-sm">
                {records.map((r) => (
                  <tr key={r.id} className="border-b border-outline-variant hover:bg-bg-subtle transition-colors">
                    <td className="p-sm pl-md">
                      {!r.is_locked && (
                        <input
                          type="checkbox"
                          checked={selected.includes(r.id)}
                          onChange={() => toggle(r.id)}
                          className="rounded text-primary"
                        />
                      )}
                    </td>
                    {columns.map((col) => (
                      <td
                        key={col.id}
                        className={`p-sm ${col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : ''} ${col.className ?? ''}`}
                      >
                        {col.render(r)}
                      </td>
                    ))}
                    {includeScope && (
                      <td className="p-sm text-center">
                        <ScopeColumnCell scope={r.scope} />
                      </td>
                    )}
                    <td className="p-sm pr-md text-right">
                      {!r.is_locked && (
                        <RecordActions
                          disabled={approve.isPending || flag.isPending || reject.isPending}
                          onApprove={() => approve.mutate(r.id)}
                          onFlag={() => flag.mutate(r.id)}
                          onReject={() => reject.mutate(r.id)}
                        />
                      )}
                    </td>
                  </tr>
                ))}
                {!records.length && (
                  <tr>
                    <td colSpan={colSpan} className="text-center py-lg font-body-sm text-on-surface-variant">
                      No records match filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          {totalCount > 0 && (
            <div className="flex items-center justify-between mt-md px-sm">
              <p className="font-body-sm text-on-surface-variant">
                Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, totalCount)} of {totalCount}
              </p>
              <div className="flex items-center gap-sm">
                <button
                  type="button"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="w-9 h-9 flex items-center justify-center rounded-lg border border-outline-variant bg-surface-container-lowest disabled:opacity-40 hover:bg-surface-variant transition-colors"
                  aria-label="Previous page"
                >
                  <span className="material-symbols-outlined">chevron_left</span>
                </button>
                <span className="font-label-md text-label-md text-on-background min-w-[100px] text-center">
                  {page} of {totalPages}
                </span>
                <button
                  type="button"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  className="w-9 h-9 flex items-center justify-center rounded-lg border border-outline-variant bg-surface-container-lowest disabled:opacity-40 hover:bg-surface-variant transition-colors"
                  aria-label="Next page"
                >
                  <span className="material-symbols-outlined">chevron_right</span>
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
