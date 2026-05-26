import { useCallback, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { api, getErrorMessage } from '../api/client'
import { StatusBadge } from '../components/StatusBadge'

const TABS = [
  { id: 'sap', label: 'SAP (Scope 1)', desc: 'MSEG/MKPF/MAKT CSV — fuel & procurement (flat file export)' },
  {
    id: 'utility',
    label: 'Utility (Scope 2)',
    desc: 'Portal CSV — ENERGY STAR or supplier bill export (kWh, billing period)',
  },
  {
    id: 'travel',
    label: 'Travel (Scope 3)',
    desc: 'Airline flight CSV or Concur/Navan-style travel export',
  },
] as const

type TabId = (typeof TABS)[number]['id']

interface UploadResult {
  id: number
  rows_parsed: number
  rows_failed: number
  rows_suspicious: number
  rows_truncated?: boolean
  issues_count?: number
  filename?: string
}

interface RawIssue {
  id: number
  row_number: number
  parse_status: string
  parse_error: string
  raw_data: Record<string, string>
}

export function IngestionPage() {
  const [tab, setTab] = useState<TabId>('sap')
  const [dragOver, setDragOver] = useState(false)
  const [lastUploadId, setLastUploadId] = useState<number | null>(null)
  const qc = useQueryClient()

  const { data: recentUploads } = useQuery({
    queryKey: ['uploads', tab],
    queryFn: async () => {
      const { data } = await api.get<{ data: UploadResult[] | { results: UploadResult[] } }>(
        '/uploads/',
        { params: { source_type: tab } }
      )
      const payload = data.data
      return Array.isArray(payload) ? payload : payload.results ?? []
    },
  })

  const { data: issuesData, isLoading: issuesLoading } = useQuery({
    queryKey: ['upload-issues', lastUploadId],
    queryFn: async () => {
      const { data } = await api.get<{
        data: { upload: UploadResult; issues: RawIssue[] }
      }>(`/uploads/${lastUploadId}/issues/`)
      return data.data
    },
    enabled: !!lastUploadId,
  })

  const upload = useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData()
      form.append('file', file)
      const { data } = await api.post(`/upload/${tab}/`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data.data as UploadResult
    },
    onSuccess: (d) => {
      setLastUploadId(d.id)
      const msg = [
        `${d.rows_parsed} clean`,
        d.rows_suspicious ? `${d.rows_suspicious} suspicious` : null,
        d.rows_failed ? `${d.rows_failed} failed` : null,
      ]
        .filter(Boolean)
        .join(', ')
      toast.success(`Upload complete: ${msg}`)
      if (d.rows_truncated) {
        toast('Large file truncated to 5,000 rows — upload in batches if needed.', { icon: '⚠️' })
      }
      qc.invalidateQueries({ queryKey: ['stats'] })
      qc.invalidateQueries({ queryKey: ['records'] })
      qc.invalidateQueries({ queryKey: ['uploads'] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const onFile = useCallback(
    (file: File | null) => {
      if (!file) return
      if (!file.name.endsWith('.csv')) {
        toast.error('Please upload a CSV file.')
        return
      }
      upload.mutate(file)
    },
    [upload]
  )

  return (
    <div className="space-y-md">
      <div className="mb-lg">
        <h1 className="font-headline-lg text-headline-lg text-on-background">Data Ingestion</h1>
        <p className="font-body-sm text-on-surface-variant mt-1">
          Upload client exports → system validates &amp; calculates kg CO₂e → suspicious/failed rows
          surface for analyst review.
        </p>
      </div>

      <div className="flex flex-wrap gap-xs border-b border-outline-variant mb-md">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => {
              setTab(t.id)
              setLastUploadId(null)
            }}
            className={`px-md py-sm font-label-md rounded-t-xl border-b-2 transition-colors ${
              tab === t.id
                ? 'border-primary text-primary'
                : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>
      <p className="font-body-sm text-on-surface-variant mb-sm">{TABS.find((t) => t.id === tab)?.desc}</p>

      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          onFile(e.dataTransfer.files[0] ?? null)
        }}
        className={`border-2 border-dashed rounded-xl p-xl flex flex-col items-center justify-center gap-sm transition-colors ${
          dragOver ? 'border-primary bg-primary-container/20' : 'border-outline-variant bg-surface-container-low'
        }`}
      >
        <span className="material-symbols-outlined text-4xl text-primary">cloud_upload</span>
        <p className="font-body-md text-on-background">Drag and drop your CSV here</p>
        <label className="bg-primary text-on-primary font-label-md px-lg py-sm rounded-xl cursor-pointer hover:opacity-90">
          {upload.isPending ? 'Uploading…' : 'Browse Files'}
          <input
            type="file"
            accept=".csv"
            className="hidden"
            disabled={upload.isPending}
            onChange={(e) => onFile(e.target.files?.[0] ?? null)}
          />
        </label>
      </div>

      {lastUploadId && issuesData && (
        <div className="bg-surface-container-lowest rounded-xl border border-outline-variant overflow-hidden">
          <div className="px-md py-sm border-b border-outline-variant flex flex-wrap gap-sm items-center justify-between">
            <h2 className="font-headline-sm text-headline-sm">Last upload — issues</h2>
            <div className="flex gap-sm font-label-sm">
              <span className="text-status-approved">{issuesData.upload.rows_parsed} clean</span>
              <span className="text-status-flagged">{issuesData.upload.rows_suspicious} suspicious</span>
              <span className="text-status-failed">{issuesData.upload.rows_failed} failed</span>
            </div>
          </div>
          {issuesLoading ? (
            <p className="p-md font-body-sm text-on-surface-variant">Loading issues…</p>
          ) : issuesData.issues.length === 0 ? (
            <p className="p-md font-body-sm text-status-approved">No failed or suspicious rows — all clean.</p>
          ) : (
            <div className="overflow-x-auto max-h-[320px] overflow-y-auto">
              <table className="w-full text-left">
                <thead className="bg-bg-subtle sticky top-0">
                  <tr>
                    <th className="font-label-md px-md py-xs">Row</th>
                    <th className="font-label-md px-md py-xs">Status</th>
                    <th className="font-label-md px-md py-xs">Reason</th>
                    <th className="font-label-md px-md py-xs">Raw snippet</th>
                  </tr>
                </thead>
                <tbody>
                  {issuesData.issues.map((row) => (
                    <tr key={row.id} className="border-t border-outline-variant">
                      <td className="font-body-sm px-md py-xs">{row.row_number}</td>
                      <td className="px-md py-xs">
                        <StatusBadge status={row.parse_status} />
                      </td>
                      <td className="font-body-sm px-md py-xs text-status-flagged max-w-[240px]">
                        {row.parse_error || '—'}
                      </td>
                      <td className="font-body-sm px-md py-xs text-on-surface-variant max-w-[280px] truncate">
                        {JSON.stringify(row.raw_data).slice(0, 120)}…
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <p className="px-md py-sm font-label-sm text-on-surface-variant border-t border-outline-variant">
            Suspicious rows appear in Review as <strong>FLAGGED</strong>. Failed rows have no emissions record.
          </p>
        </div>
      )}

      {recentUploads && recentUploads.length > 0 && (
        <div className="bg-surface-container-lowest rounded-xl border border-outline-variant p-md">
          <h2 className="font-headline-sm text-headline-sm mb-sm">Recent uploads ({tab})</h2>
          <ul className="space-y-xs">
            {recentUploads.slice(0, 5).map((u) => (
              <li key={u.id} className="flex flex-wrap gap-sm justify-between font-body-sm border-b border-outline-variant py-xs">
                <button
                  type="button"
                  className="text-primary hover:underline text-left"
                  onClick={() => setLastUploadId(u.id)}
                >
                  {u.filename || `Upload #${u.id}`}
                </button>
                <span className="text-on-surface-variant">
                  {u.rows_parsed} ok · {u.rows_suspicious} suspicious · {u.rows_failed} failed
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
