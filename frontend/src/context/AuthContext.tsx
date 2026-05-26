import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { api } from '../api/client'
import type { User } from '../types'

interface AuthContextValue {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  logoutIdle: () => void
  isAuthenticated: boolean
  loading: boolean
}

const AuthContext = createContext<AuthContextValue | null>(null)

const SESSION_TIMEOUT_KEY = 'session_timeout'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'))
  const [loading, setLoading] = useState(!!localStorage.getItem('access_token'))

  const clearSession = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setToken(null)
    setUser(null)
  }, [])

  const fetchMe = useCallback(async () => {
    try {
      const { data } = await api.get<{ success: boolean; data: User }>('/auth/me/')
      setUser(data.data)
    } catch {
      clearSession()
    } finally {
      setLoading(false)
    }
  }, [clearSession])

  useEffect(() => {
    if (token) fetchMe()
    else setLoading(false)
  }, [token, fetchMe])

  const login = async (username: string, password: string) => {
    sessionStorage.removeItem(SESSION_TIMEOUT_KEY)
    const { data } = await api.post<{
      success: boolean
      data: { access: string; refresh: string; user: User }
    }>('/auth/login/', { username, password })
    localStorage.setItem('access_token', data.data.access)
    localStorage.setItem('refresh_token', data.data.refresh)
    setToken(data.data.access)
    setUser(data.data.user)
    setLoading(false)
  }

  const logout = useCallback(() => {
    clearSession()
  }, [clearSession])

  const logoutIdle = useCallback(() => {
    sessionStorage.setItem(SESSION_TIMEOUT_KEY, '1')
    clearSession()
  }, [clearSession])

  const value = useMemo(
    () => ({
      user,
      token,
      login,
      logout,
      logoutIdle,
      isAuthenticated: !!token && !!user,
      loading,
    }),
    [user, token, loading, logout, logoutIdle]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export function consumeSessionTimeoutFlag(): boolean {
  if (sessionStorage.getItem(SESSION_TIMEOUT_KEY)) {
    sessionStorage.removeItem(SESSION_TIMEOUT_KEY)
    return true
  }
  return false
}
