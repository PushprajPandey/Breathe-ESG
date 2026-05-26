const styles: Record<string, string> = {
  PENDING: 'bg-status-pending/10 text-status-pending',
  APPROVED: 'bg-status-approved/10 text-status-approved',
  FLAGGED: 'bg-status-flagged/10 text-status-flagged',
  REJECTED: 'bg-status-failed/10 text-status-failed',
  FAILED: 'bg-status-failed/10 text-status-failed',
}

export function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`inline-flex px-2 py-0.5 rounded-full font-label-sm text-label-sm ${styles[status] || styles.PENDING}`}
    >
      {status}
    </span>
  )
}

export function ScopeBadge({ scope }: { scope: number }) {
  const colors: Record<number, string> = {
    1: 'bg-scope-1/10 text-scope-1',
    2: 'bg-scope-2/10 text-scope-2',
    3: 'bg-scope-3/10 text-scope-3',
  }
  return (
    <span className={`inline-flex px-2 py-0.5 rounded-full font-label-sm text-label-sm ${colors[scope]}`}>
      Scope {scope}
    </span>
  )
}
