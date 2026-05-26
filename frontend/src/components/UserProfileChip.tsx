import type { User } from '../types'

export function UserProfileChip({ user, onLogout }: { user: User | null; onLogout: () => void }) {
  const display = user?.first_name
    ? `${user.first_name} ${user.last_name || ''}`.trim()
    : user?.username ?? 'User'
  const initials = display
    .split(' ')
    .map((p) => p[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
  const roleLabel = user?.role === 'ADMIN' ? 'Administrator' : 'Analyst'

  return (
    <div className="flex items-center gap-sm">
      <div className="hidden sm:flex items-center gap-sm pl-sm border-l border-outline-variant">
        <div
          className="w-9 h-9 rounded-full bg-primary-container flex items-center justify-center shrink-0"
          aria-hidden
        >
          <span className="font-label-md text-label-md text-on-primary-container">{initials}</span>
        </div>
        <div className="text-right leading-tight">
          <p className="font-label-md text-label-md text-on-background">{display}</p>
          <p className="font-label-sm text-label-sm text-on-surface-variant">{roleLabel}</p>
        </div>
      </div>
      <button
        type="button"
        onClick={onLogout}
        className="font-label-md text-label-md text-primary hover:underline px-xs"
      >
        Sign out
      </button>
    </div>
  )
}
