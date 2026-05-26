import type { NavigateFunction } from 'react-router-dom'
import toast from 'react-hot-toast'
import { api } from './client'

let navigateRef: NavigateFunction | null = null

export function setNavigate(nav: NavigateFunction) {
  navigateRef = nav
}

export function setupInterceptors() {
  api.interceptors.response.use(
    (res) => res,
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        navigateRef?.('/login')
        toast.error('Session expired. Please sign in again.')
      } else if (error.response?.status >= 500) {
        toast.error('Server error. Please try again later.')
      }
      return Promise.reject(error)
    }
  )
}
