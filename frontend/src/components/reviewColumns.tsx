import type { ReactNode } from 'react'
import type { NormalizedRecord } from '../types'
import { ScopeBadge, StatusBadge } from './StatusBadge'

export type SourceFilter = '' | 'sap' | 'utility' | 'travel'

export interface ReviewColumn {
  id: string
  label: string
  align?: 'left' | 'right' | 'center'
  className?: string
  render: (record: NormalizedRecord) => ReactNode
}

const fmtDate = (d: string | null) =>
  d ? new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'

const fmtNum = (v: string | null | undefined, digits = 2) =>
  v != null && v !== '' ? Number(v).toLocaleString(undefined, { maximumFractionDigits: digits }) : '—'

const raw = (r: NormalizedRecord) => r.raw_data ?? {}

const SOURCE_LABELS: Record<string, string> = {
  sap: 'SAP',
  utility: 'Utility',
  travel: 'Travel',
}

function sourceBadge(source: string) {
  const colors: Record<string, string> = {
    sap: 'bg-scope-1/10 text-scope-1',
    utility: 'bg-scope-2/10 text-scope-2',
    travel: 'bg-scope-3/10 text-scope-3',
  }
  return (
    <span className={`inline-flex px-2 py-0.5 rounded-full font-label-sm text-label-sm ${colors[source] ?? ''}`}>
      {SOURCE_LABELS[source] ?? source}
    </span>
  )
}

const reviewNoteColumn: ReviewColumn = {
  id: 'review_note',
  label: 'Review note',
  render: (r) => {
    if (r.review_status === 'FLAGGED' && r.parse_error) {
      return <span className="text-status-flagged text-body-sm max-w-[200px] block">{r.parse_error}</span>
    }
    if (r.parse_status === 'SUSPICIOUS' && r.parse_error) {
      return <span className="text-on-surface-variant text-body-sm">{r.parse_error}</span>
    }
    return <span className="text-on-surface-variant">—</span>
  },
}

const sharedTail: ReviewColumn[] = [
  {
    id: 'emissions',
    label: 'kg CO₂e',
    align: 'right',
    className: 'font-mono',
    render: (r) => fmtNum(r.emission_kgco2e),
  },
  reviewNoteColumn,
  {
    id: 'status',
    label: 'Status',
    align: 'center',
    render: (r) => <StatusBadge status={r.review_status} />,
  },
]

/** Stitch-style unified view when no source filter is selected */
export const allSourcesColumns: ReviewColumn[] = [
  {
    id: 'source',
    label: 'Source',
    render: (r) => sourceBadge(r.source_type),
  },
  {
    id: 'date',
    label: 'Date',
    render: (r) => <span className="text-on-surface-variant">{fmtDate(r.activity_date)}</span>,
  },
  {
    id: 'description',
    label: 'Description',
    render: (r) => <span className="max-w-[280px] truncate block">{r.description}</span>,
  },
  {
    id: 'quantity',
    label: 'Quantity',
    align: 'right',
    className: 'font-mono',
    render: (r) => fmtNum(r.quantity, 3),
  },
  { id: 'unit', label: 'Unit', render: (r) => r.unit || '—' },
  ...sharedTail,
]

export const sapColumns: ReviewColumn[] = [
  {
    id: 'document',
    label: 'Document',
    render: (r) => <span className="font-mono text-body-sm">{raw(r).MBLNR || '—'}</span>,
  },
  {
    id: 'posting_date',
    label: 'Posting Date',
    render: (r) => {
      const budat = raw(r).BUDAT
      if (budat?.length === 8) {
        return `${budat.slice(0, 4)}-${budat.slice(4, 6)}-${budat.slice(6, 8)}`
      }
      return fmtDate(r.activity_date)
    },
  },
  {
    id: 'material',
    label: 'Material',
    render: (r) => (
      <div>
        <div className="font-medium">{raw(r).MAKTX || raw(r).MATNR || '—'}</div>
        {raw(r).MATNR && <div className="text-on-surface-variant text-label-sm">{raw(r).MATNR}</div>}
      </div>
    ),
  },
  {
    id: 'plant',
    label: 'Plant',
    render: (r) => raw(r).WERKS || '—',
  },
  {
    id: 'quantity',
    label: 'Qty',
    align: 'right',
    className: 'font-mono',
    render: (r) => fmtNum(r.quantity ?? raw(r).MENGE, 3),
  },
  { id: 'unit', label: 'UoM', render: (r) => r.unit || raw(r).MEINS || '—' },
  ...sharedTail,
]

export const utilityColumns: ReviewColumn[] = [
  {
    id: 'account',
    label: 'Account / Meter',
    render: (r) => (
      <div>
        <div>{raw(r).account_number || '—'}</div>
        <div className="text-on-surface-variant text-label-sm">{raw(r).meter_id || ''}</div>
      </div>
    ),
  },
  {
    id: 'site',
    label: 'Site',
    render: (r) => raw(r).site_name || r.description.split('—')[0]?.replace('Electricity - ', '') || '—',
  },
  {
    id: 'billing',
    label: 'Billing Period',
    render: (r) => {
      const start = raw(r).billing_period_start || raw(r)['Start Date']
      const end = raw(r).billing_period_end || raw(r)['End Date']
      if (start && end) return `${start} → ${end}`
      return fmtDate(r.activity_date)
    },
  },
  {
    id: 'consumption',
    label: 'Consumption',
    align: 'right',
    className: 'font-mono',
    render: (r) => {
      const kwh = raw(r).consumption_kwh || raw(r).Usage || r.quantity
      return kwh ? `${fmtNum(String(kwh), 0)} kWh` : '—'
    },
  },
  {
    id: 'cost',
    label: 'Total Cost',
    align: 'right',
    render: (r) => {
      const cost = raw(r).total_cost_usd || raw(r).Cost
      return cost ? fmtNum(String(cost), 2) : '—'
    },
  },
  {
    id: 'estimation',
    label: 'Est.',
    align: 'center',
    render: (r) => {
      const est = (raw(r).estimation || raw(r).Estimation || 'No').toString()
      return est.toLowerCase() === 'yes' ? (
        <span className="text-status-flagged font-label-sm">Yes</span>
      ) : (
        <span className="text-on-surface-variant">No</span>
      )
    },
  },
  ...sharedTail,
]

export const travelColumns: ReviewColumn[] = [
  {
    id: 'airline',
    label: 'Airline / Trip',
    render: (r) => {
      const rd = raw(r)
      if (rd.airline) {
        return (
          <div>
            <div className="font-medium">{rd.airline}</div>
            <div className="text-on-surface-variant text-label-sm">{rd.flight || rd.trip_id || ''}</div>
          </div>
        )
      }
      return rd.trip_id || r.description.slice(0, 40)
    },
  },
  {
    id: 'route',
    label: 'Route',
    render: (r) => {
      const rd = raw(r)
      const from = rd.source_city || rd.origin || rd.origin_iata
      const to = rd.destination_city || rd.destination || rd.destination_iata
      if (from && to) return `${from} → ${to}`
      return r.description
    },
  },
  {
    id: 'class',
    label: 'Class',
    render: (r) => raw(r).class || raw(r).transport_mode || '—',
  },
  {
    id: 'stops',
    label: 'Stops',
    align: 'center',
    render: (r) => raw(r).stops || '—',
  },
  {
    id: 'distance',
    label: 'Distance',
    align: 'right',
    className: 'font-mono',
    render: (r) => (r.quantity && r.unit === 'km' ? `${fmtNum(r.quantity, 0)} km` : '—'),
  },
  {
    id: 'date',
    label: 'Date',
    render: (r) => fmtDate(r.activity_date),
  },
  ...sharedTail,
]

export function getColumnsForSource(source: SourceFilter): ReviewColumn[] {
  switch (source) {
    case 'sap':
      return sapColumns
    case 'utility':
      return utilityColumns
    case 'travel':
      return travelColumns
    default:
      return allSourcesColumns
  }
}

export function getTableTitle(source: SourceFilter): string {
  switch (source) {
    case 'sap':
      return 'SAP fuel & procurement (Scope 1)'
    case 'utility':
      return 'Utility electricity (Scope 2)'
    case 'travel':
      return 'Business travel (Scope 3)'
    default:
      return 'All sources'
  }
}

/** All-sources view includes Scope column; single-source views omit it (implicit) */
export function showScopeColumn(source: SourceFilter): boolean {
  return source === ''
}

export function ScopeColumnCell({ scope }: { scope: number }) {
  return <ScopeBadge scope={scope} />
}
