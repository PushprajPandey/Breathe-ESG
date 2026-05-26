export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: 'ADMIN' | 'ANALYST'
  client: number | null
}

export interface NormalizedRecord {
  id: number
  source_type: string
  raw_data?: Record<string, string>
  activity_date: string | null
  description: string
  quantity: string | null
  unit: string
  normalized_quantity_kwh: string | null
  emission_kgco2e: string | null
  scope: number
  review_status: string
  reviewed_by_name: string | null
  reviewed_at: string | null
  is_locked: boolean
  emission_factor_name?: string
  parse_status?: string | null
  parse_error?: string
  upload_id?: number | null
  row_number?: number | null
  created_at: string
}

export interface StatsData {
  summary: {
    total: number
    pending: number
    approved: number
    flagged: number
    total_emissions_kgco2e: number
  }
  by_scope: { scope: number; count: number; emissions: string }[]
  recent: NormalizedRecord[]
}

export interface AuditLogEntry {
  id: number
  record: number | null
  record_description: string
  action: string
  performed_by_name: string
  performed_at: string
  before_state: Record<string, unknown> | null
  after_state: Record<string, unknown> | null
  message: string
}

export interface Client {
  id: number
  name: string
  slug: string
}
