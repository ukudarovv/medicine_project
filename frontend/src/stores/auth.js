import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/axios'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('accessToken') || null)
  const refreshToken = ref(localStorage.getItem('refreshToken') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const currentBranchId = ref(localStorage.getItem('currentBranchId') || null)

  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(username, password) {
    try {
      const response = await apiClient.post('/auth/login', {
        username,
        password
      })
      
      const { access, refresh, user: userData, branches } = response.data
      
      accessToken.value = access
      refreshToken.value = refresh
      user.value = userData
      
      localStorage.setItem('accessToken', access)
      localStorage.setItem('refreshToken', refresh)
      localStorage.setItem('user', JSON.stringify(userData))
      
      // Set default branch if available
      if (branches && branches.length > 0) {
        const defaultBranch = branches.find(b => b.is_default) || branches[0]
        currentBranchId.value = String(defaultBranch.id)
        localStorage.setItem('currentBranchId', String(defaultBranch.id))
        console.log('Auto-selected branch:', defaultBranch.name, 'ID:', defaultBranch.id)
      }
      
      return true
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  async function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    currentBranchId.value = null
    
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
    localStorage.removeItem('currentBranchId')
  }

  async function refreshAccessToken() {
    try {
      const response = await apiClient.post('/auth/refresh', {
        refresh: refreshToken.value
      })
      
      accessToken.value = response.data.access
      localStorage.setItem('accessToken', response.data.access)
      
      return response.data.access
    } catch (error) {
      await logout()
      throw error
    }
  }

  function setBranch(branchId) {
    currentBranchId.value = branchId
    localStorage.setItem('currentBranchId', branchId)
  }

  return {
    accessToken,
    refreshToken,
    user,
    currentBranchId,
    isAuthenticated,
    login,
    logout,
    refreshToken: refreshAccessToken,
    setBranch
  }
})

