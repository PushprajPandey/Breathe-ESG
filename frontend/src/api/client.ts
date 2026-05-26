import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data as { error?: { message?: string }; detail?: string }
    if (data?.error?.message) return data.error.message
    if (data?.detail) return String(data.detail)
    if (err.response?.status === 401) return 'Please sign in again.'
    if (err.response?.status === 500) return 'Something went wrong on our servers. Please try again.'
    if (err.response?.status === 422) return data?.error?.message || 'This action cannot be completed.'
  }
  return 'An unexpected error occurred. Please try again.'
}
