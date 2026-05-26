interface RecordActionsProps {
  onApprove: () => void
  onFlag: () => void
  onReject: () => void
  disabled?: boolean
}

export function RecordActions({ onApprove, onFlag, onReject, disabled }: RecordActionsProps) {
  return (
    <span className="inline-flex gap-xs justify-end">
      <button
        type="button"
        onClick={onApprove}
        disabled={disabled}
        className="font-label-sm text-label-sm px-sm py-xs rounded-lg bg-status-approved text-white hover:opacity-90 disabled:opacity-50 transition-opacity"
      >
        Approve
      </button>
      <button
        type="button"
        onClick={onFlag}
        disabled={disabled}
        className="font-label-sm text-label-sm px-sm py-xs rounded-lg bg-status-flagged text-white hover:opacity-90 disabled:opacity-50 transition-opacity"
      >
        Flag
      </button>
      <button
        type="button"
        onClick={onReject}
        disabled={disabled}
        className="font-label-sm text-label-sm px-sm py-xs rounded-lg bg-status-failed text-white hover:opacity-90 disabled:opacity-50 transition-opacity"
      >
        Reject
      </button>
    </span>
  )
}
