import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const apiClient = axios.create({
  baseURL: '/api/v1',  // Using Vite proxy
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    
    // Add branch header if available
    if (authStore.currentBranchId) {
      config.headers['X-Branch-Id'] = authStore.currentBranchId
    }
    
    // Add trailing slash for Django REST Framework compatibility
    if (config.url && !config.url.endsWith('/')) {
      // Check if URL has query params
      const hasParams = config.url.includes('?')
      if (hasParams) {
        // Insert slash before query params
        config.url = config.url.replace('?', '/?')
      } else {
        // Just add trailing slash
        config.url += '/'
      }
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const authStore = useAuthStore()
      try {
        await authStore.refreshToken()
        return apiClient(originalRequest)
      } catch (refreshError) {
        authStore.logout()
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient

