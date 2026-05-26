import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import type { AuditLogEntry } from '../types'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export function AuditPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['audit'],
    queryFn: async () => {
      const { data: res } = await api.get<{ results: AuditLogEntry[] }>('/audit-log/')
      return (res.results ?? res) as AuditLogEntry[]
    },
  })

  return (
    <div>
      <div className="flex flex-col md:flex-row justify-between mb-lg gap-sm">
        <div>
          <h1 className="font-headline-lg text-headline-lg text-on-background">Audit Log</h1>
          <p className="font-body-sm text-on-surface-variant">
            Read-only trail of locked records and system actions.
          </p>
        </div>
        <a
          href={`${API_BASE}/api/audit-log/export/`}
          onClick={(e) => {
            e.preventDefault()
            const token = localStorage.getItem('access_token')
            fetch(`${API_BASE}/api/audit-log/export/`, {
              headers: { Authorization: `Bearer ${token}` },
            })
              .then((r) => r.blob())
              .then((blob) => {
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = 'audit_export.csv'
                a.click()
              })
          }}
          className="bg-primary text-on-primary font-label-md py-sm px-lg rounded-xl inline-flex items-center gap-xs"
        >
          <span className="material-symbols-outlined text-[20px]">download</span>
          Export CSV
        </a>
      </div>
      {isLoading ? (
        <p className="font-body-sm text-on-surface-variant">Loading audit log…</p>
      ) : (
        <div className="bg-surface-container-lowest rounded-xl border border-outline-variant overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-outline-variant bg-bg-subtle">
                <th className="font-label-md text-label-md px-md py-sm text-left">Time</th>
                <th className="font-label-md text-label-md px-md py-sm text-left">Action</th>
                <th className="font-label-md text-label-md px-md py-sm text-left">Record</th>
                <th className="font-label-md text-label-md px-md py-sm text-left">By</th>
                <th className="font-label-md text-label-md px-md py-sm text-left">Message</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((entry) => (
                <tr key={entry.id} className="border-b border-outline-variant hover:bg-bg-subtle">
                  <td className="font-body-sm px-md py-sm whitespace-nowrap">
                    {new Date(entry.performed_at).toLocaleString()}
                  </td>
                  <td className="font-body-sm px-md py-sm">{entry.action}</td>
                  <td className="font-body-sm px-md py-sm">{entry.record_description || '—'}</td>
                  <td className="font-body-sm px-md py-sm">{entry.performed_by_name}</td>
                  <td className="font-body-sm px-md py-sm text-on-surface-variant">{entry.message}</td>
                </tr>
              ))}
              {!data?.length && (
                <tr>
                  <td colSpan={5} className="text-center py-lg font-body-sm text-on-surface-variant">
                    No audit entries yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
