import { NavLink, Outlet } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { BrandLogo } from './BrandLogo'
import { UserProfileChip } from './UserProfileChip'
import { IdleSessionGuard } from './IdleSessionGuard'
import { useAuth } from '../context/AuthContext'

const nav = [
  { to: '/', icon: 'dashboard', label: 'Dashboard' },
  { to: '/ingestion', icon: 'dataset', label: 'Data Ingestion' },
  { to: '/review', icon: 'fact_check', label: 'Review', badge: true },
  { to: '/audit', icon: 'history', label: 'Audit Log' },
  { to: '/settings', icon: 'settings', label: 'Settings' },
]

export function Layout() {
  const { user, logout } = useAuth()
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const { data } = await api.get('/records/stats/')
      return data.data
    },
  })
  const pending = stats?.summary?.pending ?? 0

  return (
    <div className="bg-background text-on-background min-h-screen flex flex-col overflow-hidden">
      <IdleSessionGuard />
      <header className="bg-surface border-b border-outline-variant flex justify-between items-center px-lg py-xs h-16 shrink-0">
        <BrandLogo />
        <div className="flex items-center gap-md">
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full border border-outline-variant bg-surface-container-lowest">
            <span className="font-label-md text-label-md text-on-background">Global Org Corp</span>
            <span className="material-symbols-outlined text-[18px] text-on-surface-variant">expand_more</span>
          </div>
          <UserProfileChip user={user} onLogout={logout} />
        </div>
      </header>
      <div className="flex flex-1 overflow-hidden">
        <nav className="hidden lg:flex flex-col gap-xs px-sm py-lg w-sidebar-width shrink-0 border-r border-outline-variant bg-surface-container overflow-y-auto">
          <div className="mb-lg px-2 flex items-center gap-2">
            <img src="/logo-icon.png" alt="" className="h-8 w-8" />
            <div>
              <h2 className="font-headline-sm text-headline-sm font-bold text-primary leading-tight">BREATHE ESG</h2>
              <p className="font-label-sm text-label-sm text-on-surface-variant">Enterprise ESG Data</p>
            </div>
          </div>
          <div className="flex flex-col gap-1 flex-1">
            {nav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `p-3 flex items-center gap-3 rounded-xl transition-all ${
                    isActive
                      ? 'bg-primary-container text-on-primary-container font-bold'
                      : 'text-on-surface-variant hover:bg-surface-variant'
                  }`
                }
              >
                <span className={`material-symbols-outlined ${item.to === '/' ? 'filled' : ''}`}>
                  {item.icon}
                </span>
                <span className="font-label-md text-label-md flex-1">{item.label}</span>
                {item.badge && pending > 0 && (
                  <span className="bg-status-pending/10 text-status-pending px-2 py-0.5 rounded-full font-label-sm text-label-sm">
                    {pending}
                  </span>
                )}
              </NavLink>
            ))}
          </div>
        </nav>
        <main className="flex-1 overflow-y-auto p-md lg:p-lg">
          <div className="max-w-container-max mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
