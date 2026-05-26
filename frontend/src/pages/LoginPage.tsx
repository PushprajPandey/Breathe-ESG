import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { getErrorMessage } from '../api/client'
import { BrandLogo } from '../components/BrandLogo'
import { consumeSessionTimeoutFlag, useAuth } from '../context/AuthContext'

export function LoginPage() {
  const [username, setUsername] = useState('analyst')
  const [password, setPassword] = useState('analyst123')
  const [loading, setLoading] = useState(false)
  const [sessionTimedOut, setSessionTimedOut] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (consumeSessionTimeoutFlag()) {
      setSessionTimedOut(true)
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setSessionTimedOut(false)
    try {
      await login(username, password)
      toast.success('Welcome back!')
      navigate('/')
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-surface-container min-h-screen flex items-center justify-center p-sm md:p-lg">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] bg-primary-container opacity-20 blur-[100px] rounded-full" />
        <div className="absolute top-[60%] -right-[10%] w-[40%] h-[40%] bg-secondary opacity-10 blur-[120px] rounded-full" />
      </div>
      <div className="relative z-10 w-full max-w-[440px] bg-surface-container-lowest rounded-xl shadow-[0px_4px_16px_rgba(18,28,42,0.06)] border border-outline-variant p-lg md:p-xl flex flex-col gap-lg">
        <div className="flex flex-col items-center text-center gap-sm">
          <BrandLogo className="flex-col sm:flex-row" />
          <h1 className="font-headline-md text-headline-md text-on-background mt-sm">Welcome back</h1>
          <p className="font-body-md text-body-md text-on-surface-variant">
            Enter your credentials to access your ESG dashboard.
          </p>
        </div>
        {sessionTimedOut && (
          <div
            className="rounded-lg border-2 border-status-flagged bg-status-flagged/15 px-md py-sm text-center"
            role="alert"
          >
            <p className="font-label-md text-label-md text-status-flagged">Session timeout</p>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-xs">
              You were signed out after 20 minutes of inactivity. Please sign in again.
            </p>
          </div>
        )}
        <form onSubmit={handleSubmit} className="flex flex-col gap-md w-full">
          <div className="flex flex-col gap-xs">
            <label htmlFor="email" className="font-label-md text-label-md text-on-background">
              Username
            </label>
            <input
              id="email"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-sm py-sm bg-surface-container-lowest border border-outline-variant rounded-lg font-body-md focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
              required
            />
          </div>
          <div className="flex flex-col gap-xs">
            <label htmlFor="password" className="font-label-md text-label-md text-on-background">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-sm py-sm bg-surface-container-lowest border border-outline-variant rounded-lg font-body-md focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-on-primary font-label-md py-sm rounded-xl hover:opacity-90 disabled:opacity-60 transition-opacity"
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>
        <p className="text-center font-body-sm text-on-surface-variant">
          Demo: analyst / analyst123 or admin / admin123
        </p>
      </div>
    </div>
  )
}
