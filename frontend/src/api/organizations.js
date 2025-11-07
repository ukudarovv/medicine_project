import apiClient from './axios'

const organizationsAPI = {
  // Get all organizations (admin only)
  getAll() {
    return apiClient.get('/org/organizations/')
  },

  // Get single organization
  getOne(id) {
    return apiClient.get(`/org/organizations/${id}/`)
  },

  // Create organization (admin only)
  create(data) {
    return apiClient.post('/org/organizations/', data)
  },

  // Update organization (admin only)
  update(id, data) {
    return apiClient.patch(`/org/organizations/${id}/`, data)
  },

  // Delete organization (admin only)
  delete(id) {
    return apiClient.delete(`/org/organizations/${id}/`)
  },

  // Get users in organization
  getUsers(organizationId) {
    return apiClient.get(`/org/organizations/${organizationId}/users/`)
  },

  // Create user in organization
  createUser(organizationId, data) {
    return apiClient.post(`/org/organizations/${organizationId}/users/`, data)
  },

  // Organization users management
  getAllUsers(organizationId = null) {
    const params = organizationId ? { organization: organizationId } : {}
    return apiClient.get('/org/organization-users/', { params })
  },

  updateUser(userId, data) {
    return apiClient.patch(`/org/organization-users/${userId}/`, data)
  },

  deleteUser(userId) {
    return apiClient.delete(`/org/organization-users/${userId}/`)
  }
}

export default organizationsAPI

