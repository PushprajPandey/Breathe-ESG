import { useAuth } from '../context/AuthContext'
import { useIdleTimeout } from '../hooks/useIdleTimeout'

/** Logs out after 20 minutes of inactivity when user is authenticated. */
export function IdleSessionGuard() {
  const { isAuthenticated, logoutIdle } = useAuth()
  useIdleTimeout(logoutIdle, isAuthenticated)
  return null
}
