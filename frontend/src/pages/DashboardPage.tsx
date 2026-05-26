import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { ScopeBadge, StatusBadge } from '../components/StatusBadge'
import type { StatsData } from '../types'

export function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const res = await api.get<{ success: boolean; data: StatsData }>('/records/stats/')
      return res.data.data
    },
  })

  if (isLoading) {
    return <div className="font-body-md text-on-surface-variant">Loading dashboard…</div>
  }

  const s = data?.summary

  const cards = [
    { label: 'Total Records', value: s?.total ?? 0, icon: 'inventory_2', color: 'text-on-surface' },
    { label: 'Pending Review', value: s?.pending ?? 0, icon: 'pending', color: 'text-status-pending' },
    { label: 'Approved', value: s?.approved ?? 0, icon: 'check_circle', color: 'text-status-approved' },
    { label: 'Flagged', value: s?.flagged ?? 0, icon: 'flag', color: 'text-status-flagged' },
  ]

  return (
    <div className="space-y-md">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-lg">
        <div>
          <h1 className="font-headline-lg text-headline-lg text-on-background">Overview</h1>
          <p className="font-body-sm text-on-surface-variant mt-1">
            Carbon emissions data ingestion and analyst review platform
          </p>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-sm">
        {cards.map((c) => (
          <div
            key={c.label}
            className="bg-surface-container-lowest rounded-xl p-md border border-outline-variant shadow-[0_2px_4px_rgba(31,41,55,0.05)]"
          >
            <div className="flex items-center justify-between mb-sm">
              <span className="font-label-md text-label-md text-on-surface-variant">{c.label}</span>
              <span className={`material-symbols-outlined ${c.color}`}>{c.icon}</span>
            </div>
            <p className={`font-headline-md text-headline-md ${c.color}`}>{c.value.toLocaleString()}</p>
          </div>
        ))}
      </div>
      <div className="bg-surface-container-lowest rounded-xl p-md border border-outline-variant">
        <h2 className="font-headline-sm text-headline-sm mb-sm">Total Emissions (kg CO₂e)</h2>
        <p className="font-headline-lg text-primary">
          {(s?.total_emissions_kgco2e ?? 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}
        </p>
      </div>
      <div className="bg-surface-container-lowest rounded-xl border border-outline-variant overflow-hidden">
        <div className="px-md py-sm border-b border-outline-variant">
          <h2 className="font-headline-sm text-headline-sm">Recent Activity</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-bg-subtle">
                <th className="font-label-md text-label-md px-md py-sm">Source</th>
                <th className="font-label-md text-label-md px-md py-sm">Description</th>
                <th className="font-label-md text-label-md px-md py-sm">Scope</th>
                <th className="font-label-md text-label-md px-md py-sm text-right">kg CO₂e</th>
                <th className="font-label-md text-label-md px-md py-sm">Status</th>
              </tr>
            </thead>
            <tbody>
              {(data?.recent ?? []).map((r) => (
                <tr key={r.id} className="border-b border-outline-variant hover:bg-bg-subtle">
                  <td className="px-md py-sm">
                    <span className="font-label-sm text-label-sm capitalize">{r.source_type}</span>
                  </td>
                  <td className="font-body-sm px-md py-sm max-w-[320px] truncate">{r.description}</td>
                  <td className="px-md py-sm">
                    <ScopeBadge scope={r.scope} />
                  </td>
                  <td className="font-body-sm px-md py-sm text-right">
                    {r.emission_kgco2e ? Number(r.emission_kgco2e).toFixed(2) : '—'}
                  </td>
                  <td className="px-md py-sm">
                    <StatusBadge status={r.review_status} />
                  </td>
                </tr>
              ))}
              {!data?.recent?.length && (
                <tr>
                  <td colSpan={5} className="px-md py-lg text-center font-body-sm text-on-surface-variant">
                    No records yet. Upload data from Data Ingestion.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
