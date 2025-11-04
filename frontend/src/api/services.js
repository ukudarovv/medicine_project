import apiClient from './axios'

// Service categories
export const getCategories = (params) => apiClient.get('/services/categories/', { params })
export const getCategory = (id) => apiClient.get(`/services/categories/${id}/`)
export const createCategory = (data) => apiClient.post('/services/categories/', data)
export const updateCategory = (id, data) => apiClient.put(`/services/categories/${id}/`, data)
export const deleteCategory = (id) => apiClient.delete(`/services/categories/${id}/`)

// Services
export const getServices = (params) => apiClient.get('/services/services/', { params })
export const getService = (id) => apiClient.get(`/services/services/${id}/`)
export const createService = (data) => apiClient.post('/services/services/', data)
export const updateService = (id, data) => apiClient.put(`/services/services/${id}/`, data)
export const deleteService = (id) => apiClient.delete(`/services/services/${id}/`)

// ICD Codes
export const getICDCodes = (params) => apiClient.get('/services/icd-codes/', { params })
export const searchICDCodes = (query) => apiClient.get('/services/icd-codes/', { params: { search: query } })

