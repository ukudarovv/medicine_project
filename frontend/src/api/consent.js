/**
 * API client for consent system
 */
import axios from './axios'

/**
 * Search patient by IIN
 * @param {string} iin - Patient IIN (12 digits)
 * @returns {Promise<Object>} Patient data
 */
export const searchPatientByIIN = async (iin) => {
  const response = await axios.post('/consent/search-patient/', { iin })
  return response.data
}

/**
 * Create access request
 * @param {Object} data - Request data
 * @param {string} data.patient_iin - Patient IIN
 * @param {Array<string>} data.scopes - Requested scopes
 * @param {string} data.reason - Reason for access
 * @param {number} data.requested_duration_days - Duration in days
 * @returns {Promise<Object>} Created access request
 */
export const createAccessRequest = async (data) => {
  const response = await axios.post('/consent/access-requests/', data)
  return response.data
}

/**
 * Get access request by ID
 * @param {string} requestId - Access request UUID
 * @returns {Promise<Object>} Access request data
 */
export const getAccessRequest = async (requestId) => {
  const response = await axios.get(`/consent/access-requests/${requestId}/`)
  return response.data
}

/**
 * Get access requests (for current org)
 * @param {Object} params - Query parameters
 * @param {number} params.patient_id - Filter by patient ID
 * @param {string} params.status - Filter by status
 * @returns {Promise<Array>} List of access requests
 */
export const getAccessRequests = async (params = {}) => {
  const response = await axios.get('/consent/access-requests/', { params })
  return response.data
}

/**
 * Get active access grants (for current org)
 * @param {Object} params - Query parameters
 * @param {number} params.patient_id - Filter by patient ID
 * @param {boolean} params.active_only - Show only active grants
 * @returns {Promise<Array>} List of access grants
 */
export const getAccessGrants = async (params = {}) => {
  const response = await axios.get('/consent/grants/', { params })
  return response.data
}

/**
 * Revoke access grant
 * @param {string} grantId - Access grant UUID
 * @param {string} reason - Revocation reason
 * @returns {Promise<Object>} Revocation result
 */
export const revokeAccessGrant = async (grantId, reason = '') => {
  const response = await axios.post(`/consent/grants/${grantId}/revoke/`, { reason })
  return response.data
}

/**
 * Get audit logs
 * @param {Object} params - Query parameters
 * @param {number} params.patient_id - Filter by patient ID
 * @param {string} params.action - Filter by action
 * @returns {Promise<Array>} List of audit logs
 */
export const getAuditLogs = async (params = {}) => {
  const response = await axios.get('/consent/audit-logs/', { params })
  return response.data
}

export default {
  searchPatientByIIN,
  createAccessRequest,
  getAccessRequest,
  getAccessRequests,
  getAccessGrants,
  revokeAccessGrant,
  getAuditLogs
}

