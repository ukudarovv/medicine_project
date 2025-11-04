import apiClient from './axios'

// Employee CRUD
export const getEmployees = (params) => apiClient.get('/staff/employees/', { params })
export const getEmployee = (id) => apiClient.get(`/staff/employees/${id}/`)
export const createEmployee = (data) => apiClient.post('/staff/employees/', data)
export const updateEmployee = (id, data) => apiClient.put(`/staff/employees/${id}/`, data)
export const deleteEmployee = (id) => apiClient.delete(`/staff/employees/${id}/`)

// Get doctors only
export const getDoctors = () => apiClient.get('/staff/employees/doctors/')

// Grant access
export const grantAccess = (id, data) => apiClient.post(`/staff/employees/${id}/grant_access/`, data)

// Employee branches
export const getEmployeeBranches = (params) => apiClient.get('/staff/employee-branches/', { params })
export const createEmployeeBranch = (data) => apiClient.post('/staff/employee-branches/', data)
export const deleteEmployeeBranch = (id) => apiClient.delete(`/staff/employee-branches/${id}/`)

// Employee services
export const getEmployeeServices = (params) => apiClient.get('/staff/employee-services/', { params })
export const createEmployeeService = (data) => apiClient.post('/staff/employee-services/', data)
export const deleteEmployeeService = (id) => apiClient.delete(`/staff/employee-services/${id}/`)

