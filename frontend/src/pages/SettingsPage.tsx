import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import type { Client } from '../types'

export function SettingsPage() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'

  const { data: clients } = useQuery({
    queryKey: ['clients'],
    queryFn: async () => {
      const { data } = await api.get<{ results?: Client[] } | Client[]>('/clients/')
      return Array.isArray(data) ? data : (data as { results?: Client[] }).results ?? []
    },
    enabled: isAdmin,
  })

  const { data: users } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const { data } = await api.get<{ data: unknown[] }>('/users/')
      return data.data
    },
    enabled: isAdmin,
  })

  return (
    <div className="space-y-lg">
      <div>
        <h1 className="font-headline-lg text-headline-lg text-on-background">Settings</h1>
        <p className="font-body-sm text-on-surface-variant">Client and user management</p>
      </div>
      <div className="bg-surface-container-lowest rounded-xl p-md border border-outline-variant">
        <h2 className="font-headline-sm text-headline-sm mb-sm">Your Profile</h2>
        <dl className="grid grid-cols-2 gap-sm font-body-sm">
          <dt className="text-on-surface-variant">Username</dt>
          <dd>{user?.username}</dd>
          <dt className="text-on-surface-variant">Email</dt>
          <dd>{user?.email}</dd>
          <dt className="text-on-surface-variant">Role</dt>
          <dd>{user?.role}</dd>
        </dl>
      </div>
      {isAdmin && (
        <>
          <div className="bg-surface-container-lowest rounded-xl p-md border border-outline-variant">
            <h2 className="font-headline-sm text-headline-sm mb-md">Clients</h2>
            <ul className="space-y-xs">
              {(clients ?? []).map((c) => (
                <li key={c.id} className="font-body-sm flex justify-between py-xs border-b border-outline-variant">
                  <span>{c.name}</span>
                  <span className="text-on-surface-variant">{c.slug}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="bg-surface-container-lowest rounded-xl p-md border border-outline-variant">
            <h2 className="font-headline-sm text-headline-sm mb-md">Users</h2>
            <ul className="space-y-xs">
              {((users ?? []) as { id: number; username: string; role: string }[]).map((u) => (
                <li key={u.id} className="font-body-sm flex justify-between py-xs border-b border-outline-variant">
                  <span>{u.username}</span>
                  <span className="text-on-surface-variant">{u.role}</span>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
      {!isAdmin && (
        <p className="font-body-sm text-on-surface-variant">
          Admin access required to manage clients and users.
        </p>
      )}
    </div>
  )
}
